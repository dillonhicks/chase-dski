#ifndef DSKI_TRACE_H
#define DSKI_TRACE_H



#ifdef __KERNEL__



#define DSKI_TRACE_MODULE_NAME "dski_trace"


/* Used to globally enable tracing enabled when > 0 */
extern atomic_t dski_trace_count;


/** 
 * Waypoint symbols to inform the trace control structure's
 * (dski_trace_s) union.
 */
enum dski_trace_waypoint {
	DSKI_TRACE_SYS_ENTER_WP=0,
	DSKI_TRACE_SYS_LEAVE_WP
};


/**
 * Stores the stack image of all of the registers contained on a
 * syscall entry.
 */
typedef struct dski_trace_enter_s {
	
	/* Registers */
	unsigned long bx; 	/* syscall param 0 */
	unsigned long cx;       /* syscall param 1 */
	unsigned long dx;       /* syscall param 2 */
	unsigned long si;       /* syscall param 3 */
	unsigned long di;       /* syscall param 4 */
	unsigned long bp;       /* syscall param 5 */

	unsigned long ax;       

	unsigned long ds;
	unsigned long es;
	unsigned long fs;
	unsigned long gs;

	/* Trap frame context */
	unsigned long orig_ax; /* syscall number */
	unsigned long ip; 
	unsigned long cs;
	unsigned long flags;
	unsigned long sp;
	unsigned long ss;
	
} dski_trace_enter_t;


/** 
 * On the syscall leave we only care what the syscall number was and
 * the return value so we only store those registers. For this
 * iteration we make the assumption that the contents of the existing
 * registers does not change.
 */
typedef struct dski_trace_leave_s {

	unsigned long ax; 	/* sycall return value */
	unsigned long orig_ax; 	/* syscall number */

	/* TODO.D: Add the user buffers. */
} dski_trace_leave_t;


/** 
 * General tracing structure. Used currently only for syscalls but
 * created to be general.
 */
typedef struct dski_trace_s {
	enum dski_trace_waypoint waypoint;
	union {
		dski_trace_enter_t sys_enter;
		dski_trace_leave_t sys_leave;
	};
} dski_trace_t;



#endif	/* __KERNEL__ */



/*
 * =============================
 * DSKI Trace IOCTL 
 * =============================
 */


enum dski_trace_cmd {
	DSKI_TRACE_ENABLE = 0,
	DSKI_TRACE_DISABLE,
};


struct dski_ioc_trace_ctrl {
	enum dski_trace_cmd  cmd;
};



typedef union dski_trace_ioctl_union {
	struct dski_ioc_trace_ctrl               trace_ctrl; 
} dski_trace_ioctl_param;


#define DSKI_TRACE_CTRL           _IOW('t', 1, struct dski_ioc_trace_ctrl)




#endif /* DSKI_TRACE_H */
