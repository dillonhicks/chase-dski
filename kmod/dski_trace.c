#include <asm/uaccess.h>
#include <asm/ptrace.h>
#include <linux/fs.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/errno.h>
#include <linux/err.h>
#include <linux/kobject.h>
#include <linux/string.h>
#include <linux/sched.h>

#include <linux/kusp/dski.h>
#include <linux/kusp/dski_trace.h>



/* DSTRM_DEBUG_DECL(DSKI_TRACE, DEBUG); */

#ifdef NO_SSDF_DTRACE_DEBUG
#define DTRACE_DEBUG(fmt, args...) DSTRM_DEBUG(DSKI_TRACE, DEBUG, fmt, ##args)
#else
#define DTRACE_DEBUG(fmt, args...) printk("DSKI_TRACE(%s:%d) " fmt, __FILE__, __LINE__, ##args)
#endif 

/**
 * Keeps the count of the current number of processes using the KUSP
 * PERF which when dski_trace_count > 0 causes the system call entry
 * and system call exit instrumentation points to be generated.
 */
atomic_t dski_trace_count = ATOMIC_INIT(0);

atomic_t syscall_enter_count = ATOMIC_INIT(0);
atomic_t syscall_leave_count = ATOMIC_INIT(0);


static inline void 
dski_trace_enable(void) {
	if (unlikely(atomic_read(&dski_trace_count) < 0))
		atomic_set(&dski_trace_count, 0);
	atomic_inc(&dski_trace_count);
}


static inline void 
dski_trace_disable(void) {
	if (atomic_read(&dski_trace_count) == 0)
		return;

	atomic_dec(&dski_trace_count);
}



/**
 * Format the struct that records the syscall enter.
 */
static inline void 
__dski_trace_format_enter(struct pt_regs *regs, dski_trace_t *tdb) {

	tdb->waypoint = DSKI_TRACE_SYS_ENTER_WP;

	tdb->sys_enter.bx = regs->bx;
	tdb->sys_enter.cx = regs->cx;
	tdb->sys_enter.dx = regs->dx;
	tdb->sys_enter.si = regs->si;
	tdb->sys_enter.di = regs->di;
	tdb->sys_enter.ax = regs->ax;
	tdb->sys_enter.ds = regs->ds;      
	tdb->sys_enter.es = regs->es;
	tdb->sys_enter.fs = regs->fs;
	tdb->sys_enter.gs = regs->gs;
	tdb->sys_enter.orig_ax = regs->orig_ax;
	tdb->sys_enter.ip = regs->ip;
	tdb->sys_enter.cs = regs->cs;
	tdb->sys_enter.flags = regs->flags;
	tdb->sys_enter.sp = regs->sp;
	tdb->sys_enter.ss = regs->ss;
} 


/**
 * Format the binary struct that records the syscall leave. 
 */
static inline void 
__dski_trace_format_leave(struct pt_regs *regs, dski_trace_t *tdb) {

	tdb->waypoint = DSKI_TRACE_SYS_LEAVE_WP;
	
	tdb->sys_leave.orig_ax = regs->orig_ax;
	tdb->sys_leave.ax = regs->ax;       
}


/**
 * if dski perf has been enabled (dski_trace_count > 0) this code, when
 * called from ENTRY(system_call) in entry_32.S, will record the
 * contents of the registers intended for the next syscall. The number
 * of the particular system call is stored in regs->orig_ax. Further
 * modification to this code could incorporate some sort of semantic
 * processing of the register contents based on the system call number
 * as one could discern the types of data described by the contents of
 * the registers.
 */
static void
trace_syscall_enter(void *data)
{

	/*
	 * The trace data block structure. 
	 */
	dski_trace_t tdb;
	struct pt_regs *regs;
	
	regs = (struct pt_regs *)data;

	atomic_inc(&syscall_enter_count);

	/* Skip when perf has is not enabled, every enable increments
	 * the counter  */     
	if (likely(atomic_read(&dski_trace_count) == 0)) {
		/* If dski_perf is not enabled - make the return value
		 * (%eax) to the syscall number to keep with the
		 * ptrace's syscall_trace_enter() semantics.
		 */
		/* DSTRM_EVENT(SYSCALL, NO_PERF_ENTER, current->pid); */
		return;
	}

	__dski_trace_format_enter(regs, &tdb);

	DSTRM_EVENT_DATA(SYSCALL, ENTER, current->pid, sizeof(tdb), &tdb,
			 "parse_dski_trace_type");


}



static void 
trace_syscall_leave(void *data) {

	/* Trace control block */
	dski_trace_t tdb;

	struct pt_regs *regs;
	
	regs = (struct pt_regs *)data;

	atomic_inc(&syscall_leave_count);

	/* Skip when perf has is not enabled, every enable increments
	 * the counter  */
	if (likely(atomic_read(&dski_trace_count) == 0)) {
		/* DSTRM_EVENT(SYSCALL, NO_PERF_LEAVE, current->pid); */
		return;
	}

	__dski_trace_format_leave(regs, &tdb);

	DSTRM_EVENT_DATA(SYSCALL, LEAVE, current->pid, sizeof(tdb), &tdb,
			"parse_dski_trace_type");

}



static void
ptrace_syscall_enter(void * data) {

	/*  The trace data block structure. */
	dski_trace_t tdb;

	struct pt_regs *regs;
	regs = (struct pt_regs *)data;
	
	__dski_trace_format_enter(regs, &tdb);

	DSTRM_EVENT_DATA(SYSCALL, PTRACE_ENTER, current->pid, sizeof(tdb), &tdb,
			 "parse_dski_trace_type");


}

static void
ptrace_syscall_leave(void * data) {

	/*  The trace data block structure. */
	dski_trace_t tdb;

	struct pt_regs *regs;
	regs = (struct pt_regs *)data;
       
	__dski_trace_format_leave(regs, &tdb);

	DSTRM_EVENT_DATA(SYSCALL, PTRACE_LEAVE, current->pid, sizeof(tdb), &tdb,
			 "parse_dski_trace_type");

}





/*
 * ===============================
 * DSKI TRACE IOCTL Interface 
 * ===============================
 */


/*
 * Generic open call that will always be successful since there is no
 * extra setup we need to do for this module.
 */
static int
dski_trace_open(struct inode *inode, struct file *file) {
	return 0;
}


static int
dski_trace_close(struct inode *inode, struct file *file) {
	return 0;
}


static long
dski_trace_ioctl(struct file *file, 
		 unsigned int ioctl_num, unsigned long ioctl_param) {
	int                         ret = 0;
	dski_trace_ioctl_param      local_param;

	if (copy_from_user
	    ((void *)&local_param, (void *)ioctl_param, _IOC_SIZE(ioctl_num))) {
		ret = -ENOMEM;
		goto out;
	}

	switch (ioctl_num) {


	case DSKI_TRACE_CTRL:
	{
		if (local_param.trace_ctrl.cmd == DSKI_TRACE_ENABLE)
			dski_trace_enable();
		else if (local_param.trace_ctrl.cmd == DSKI_TRACE_DISABLE)
			dski_trace_disable();
		else
			ret = -EINVAL;
		break;
	}

	default:
	{
		DTRACE_DEBUG("No such ioctl call number %d.", ioctl_num);
		ret = -EINVAL;
	}

	}; /* switch(ioctl_num) */

	
out:
	return ret;
}






/* 
 * ===============================================
 *            Sysfs Interface
 * ===============================================
 */

/*
 * The easiest approach is for each variable you wish to expose to
 * sysfs should have a show() and store() routine. These are the
 * kobject/sysfs versions of the typical get/set routines.
 *
 */


/*
 *
 */
static ssize_t 
trace_count_show(struct kobject *kobj, 
		 struct kobj_attribute *attr, char *buf) {

	int ret = 0;
	
	DTRACE_DEBUG("reading dski_trace_count.\n");
	
	ret =  sprintf(buf, "%d\n", atomic_read(&dski_trace_count));

	return ret;
}


static ssize_t
trace_count_store(struct kobject *kobj, struct kobj_attribute *attr,
		  const char *buf, size_t count) {

	int trace_count = 0;

	/* 
	 * One downside to sysfs is all data is passed around as
	 * buffers that are character arrays. To get the desired
	 * integer value from the buffer we must use the sscanf
	 * function to convert the character data in the buffer to an
	 * integer.
	 */
	sscanf(buf, "%d", &trace_count);


	if (trace_count == 0) {
		DTRACE_DEBUG("trace_count == 0, no effect on dski_trace_count.\n");		
	} else if (trace_count > 0) {
		DTRACE_DEBUG("trace_count > 0 | %d | atomic_inc(&dski_trace_count).\n",
			    trace_count);
		atomic_inc(&dski_trace_count);
	} else {
		DTRACE_DEBUG("trace_count < 0 | %d | atomic_dec(&dski_trace_count).\n",
			    trace_count);
		atomic_dec(&dski_trace_count);
	}
       
	/* 
	 * I am unsure why the <variable>_store routines seem to
	 * require to return the count argument. Possibly something to
	 * do with KSets? I'm not sure at the moment.
	 */
	return count;
}


static struct kobj_attribute dski_trace_count_attr =
	__ATTR(trace_count,       /* Var to which to add attrs  */
	       0666,		  /* mode (a la chmod) */
	       trace_count_show,  /* sysfs callback to read var  */
	       trace_count_store);/* sysfs callback to write var */


/*
 *
 */
static ssize_t 
syscall_enter_count_show(struct kobject *kobj, 
		 struct kobj_attribute *attr, char *buf) {

	int ret = 0;
	
	DTRACE_DEBUG("Reading dski_trace_count.\n");
	
	ret =  sprintf(buf, "%d\n", atomic_read(&syscall_enter_count));	

	return ret;
}

static ssize_t
syscall_enter_count_store(struct kobject *kobj, struct kobj_attribute *attr,
		  const char *buf, size_t count) {
	DTRACE_DEBUG("Attempting to set the set readonly syscall_enter_count.\n");
	return count;
}


static struct kobj_attribute syscall_enter_count_attr =
	__ATTR(syscall_enter_count,       /* Var to which to add attrs  */
	       0666,		  /* mode (a la chmod) */
	       syscall_enter_count_show,  /* sysfs callback to read var  */
	       syscall_enter_count_store);/* sysfs callback to write var */




/*
 *
 */
static ssize_t 
syscall_leave_count_show(struct kobject *kobj, 
		 struct kobj_attribute *attr, char *buf) {

	int ret = 0;
	
	DTRACE_DEBUG("Reading dski_trace_count.\n");
	
	ret =  sprintf(buf, "%d\n", atomic_read(&syscall_leave_count));	

	return ret;
}

static ssize_t
syscall_leave_count_store(struct kobject *kobj, struct kobj_attribute *attr,
		  const char *buf, size_t count) {
	DTRACE_DEBUG("Attempting to set the set readonly syscall_leave_count.\n");
	return count;
}


static struct kobj_attribute syscall_leave_count_attr =
	__ATTR(syscall_leave_count,       /* Var to which to add attrs  */
	       0666,		  /* mode (a la chmod) */
	       syscall_leave_count_show,  /* sysfs callback to read var  */
	       syscall_leave_count_store);/* sysfs callback to write var */




/*
 * Create a group of attributes so that we can create and destory them all
 * at once.
 */
static struct attribute *dski_trace_kobj_attrs[] = {
	&dski_trace_count_attr.attr,
	&syscall_enter_count_attr.attr,
	&syscall_leave_count_attr.attr,
	NULL,	/* need to NULL terminate the list of attributes */
};

/*
 * An unnamed attribute group will put all of the attributes directly in
 * the kobject directory.  If we specify a name, a subdirectory will be
 * created for the attributes with the directory being the name of the
 * attribute group.
 */
static struct attribute_group dski_trace_kobj_attr_group = {
	.attrs = dski_trace_kobj_attrs,
};

/*
 * The root kobj for this module. 
 */
static struct kobject *dski_trace_kobj;



/* 
 * ===============================================
 *            Module init/exit 
 * ===============================================
 */


static struct file_operations dski_trace_dev_fops = {
	.owner		= THIS_MODULE,
	.open		= dski_trace_open,
	.release 	= dski_trace_close,
	.unlocked_ioctl	= dski_trace_ioctl
};

static struct miscdevice dski_trace_misc = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = DSKI_TRACE_MODULE_NAME,
	.fops = &dski_trace_dev_fops
};



static int __init 
dski_trace_init(void) {

	int ret = 0;

	/*
	 * Attempt to register the module as a misc. device with the
	 * kernel.
	 */
	ret = misc_register(&dski_trace_misc);
	
	if (ret < 0) {
		/* Registration failed so give up. */
		goto out;
	}


	/*
	 * Create a simple kobject with the name of "dski_trace",
	 * located under /sys/kernel/
	 *
	 * As this is a simple directory, no uevent will be sent to
	 * userspace.  That is why this function should not be used for
	 * any type of dynamic kobjects, where the name and number are
	 * not known ahead of time.
	 */
	dski_trace_kobj = kobject_create_and_add(DSKI_TRACE_MODULE_NAME, kernel_kobj);
	if (!dski_trace_kobj) {
		ret = -ENOMEM;
		goto out;
	}

	/* Create the files associated with this kobject */
	ret = sysfs_create_group(dski_trace_kobj, &dski_trace_kobj_attr_group);
	if (ret) {
		kobject_put(dski_trace_kobj);
		
	}

	dski_tracehooks.trace_syscall_enter_func = trace_syscall_enter;
	dski_tracehooks.trace_syscall_leave_func = trace_syscall_leave;

	dski_tracehooks.ptrace_syscall_enter_func = ptrace_syscall_enter;
	dski_tracehooks.ptrace_syscall_leave_func = ptrace_syscall_leave;

       
	DTRACE_DEBUG("DSKI Trace module loaded.\n");


out:
	return ret;


}


static void __exit 
dski_trace_exit(void) {

	dski_tracehooks.trace_syscall_enter_func = NULL;
	dski_tracehooks.trace_syscall_leave_func = NULL;
	dski_tracehooks.ptrace_syscall_enter_func = NULL;
	dski_tracehooks.ptrace_syscall_leave_func = NULL;

	misc_deregister(&dski_trace_misc);
	DTRACE_DEBUG("DSKI Trace module unloaded.\n");
}



module_init(dski_trace_init);
module_exit(dski_trace_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("DSKI Trace Module");
MODULE_AUTHOR("Dillon Hicks <hhicks@ittc.ku.edu>");
