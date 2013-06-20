strace tracing codepath
=======================

Tracing begins ``def straceC_trace()``

Note that the following pythonic pseudo code is the 1000 ft policy
level view of how strace goes about tracing a process. The names for
functions look peculiar but are in the form::

    func <filename><EXT>_<function_name>(<c args>)

Such that the filenames are relative to the root strace 4.6 source
tree. This will then create a syntax such that the function ``int
trace()`` from ``strace-4.6/strace.c`` will map to a pseudo code
function ``def straceC_trace()``.  

Also be aware that dude to the many different architectures and OSes
for which this code is written there might be multiple
functiondefinitions surrounded by ``#define <SOME_ARCH>`` or ``#define
<SOME_OS>`` in this case where I have noticed these duplicates the
reader should find a line number in a comment directly within the
start of the function.

If that line number cannot be found you can assume that the pseudo
code is for codeblocks contained within either or both:

- ``#ifdef LINUX``
- ``#ifdef I386``


Futher, those reading this code whould be familiar enough with the
names of systemcalls to know how to differentiate between a pseudocode
markup for clairity and brevity and a proper syscall function call.


def straceC_trace():
    
    # wait for some slave process to have some status pid is the pid
    # of the slave on succesful return, otherwise it is -1 and the
    # error is stored in errno.
    
    pid = wait_for_slave(desired_status)
    
    if slave_is_interactive:
        # Take special precations?
        sigprocmask(SIG_SETMASK, &empty_set, NULL)
    

    # get the tracing struct for this process from the PID to Trace
    # Control Block table.        
    tracing_struct = straceC_pid2tcb(pid)
    
    if slave_exited:        
        record_exit()
        do_cleanup()
        # get rid of the tbc
        straceC_droptcb(tcp)
        return 

    # record the trace
    if syscallC_trace_syscall() < 0:
        if not tcp->ptrace_errno:
            # "ptrace() failed in trace_syscall() with ESRCH.  Likely a
            # result of process disappearing mid-flight.  Observed
            # case: exit_group() terminating all processes in thread
            # group. In this case, threads "disappear" in an
            # unpredictable moment without any notification to strace
            # via wait()." - verbatim from strace.c
            if attched_to_slave(tcp):
                # assuming in this case slave!=exist but tcp still does
                straceC_detach(tcp, 0)
            else:
                # kill off slave
                ptrace(PTRACE_KILL, tcp->pid, (char *) 1, SIGTERM)
                # cleanup tcb table
                straceC_droptcb(tcp)

    # restart the ptrace context
    if not ptrace_restart(PTRACE_SYSALL, tcp, 0):
        # They chose a generic fail code in this case for some reason.
        return -1



def syscallC_trace_syscall(struct tcb *tcp):
    
    ret = 0 

    if slave_exiting_syscall(tcp):
        ret = syscallC_trace_syscall_exiting(tcp)
    else: # slave_entering_syscall
        ret = syscallC_trace_syscall_entering(tcp)

    return ret


def syscallC_trace_syscall_entering(struct tcb *tcp):
    result = 0
    syscall_number = get_scno(tcp)
    if syscall_number == 0:
        # sc == 0: sys_restart_syscall
        return syscall_number
    if syscall_number == 1:
        result = syscallC_syscall_fixup(tcp)
    if result == 1:
        result = syscallC_syscall_enter(tcp)
    if result == 0:
        return result

    


def syscallC_trace_syscall_exiting(struct tcb *tcp):
    pass


def syscallC_syscall_fixup(struct tcb *tcp):
    # Called in trace_syscall() at each syscall entry and exit.
    # Returns:
    if ignore_syscall(tcp):
        return 0 # "ignore this syscall", bail out of trace_syscall() silently.
    elif good_syscall(tcp):
        return 1 # ok, continue in trace_syscall().
    else:
        # other: error, trace_syscall() should print error indicator
        # ("????" etc) and bail out.
        return ERROR 

def syscallC_syscall_enter(struct tcb *tcp):

    i = 0
    
    # scno > 0 && <= num_syscalls
    if syscall_number_is_valid(tcb->scno):
        # sysent[tcp->scno].nargs != -1 (in other words, the number of
        #  args for syscall table entry for scno does not equal -1 and
        #  thus is implemented by strace)
        if syscall_is_implemented(tcp->scno):
            # tcp->u_nargs = sysent[tcp->scno.nargs
	    set_num_args_from_syscall_table(tcp)
	else:
            # tcp->u_nargs = MAX_ARGS 
            # #ifdef HPPA
            #   MAX_ARGS = 6 
            # #else 
            #  MAX_ARGS = 32
            # #endif
            set_num_args_max(tcp)
            
    
    for arg_idx in range(tcp->u_nargs):
        # for each argument index in the on [0:num_args).
        if upeek(tcp, arg_index*4, &tcp->u_arg[i]) < 0 :
            # use upeek() to grab the contents of the registers stack
            # images for the slave process by knowing that stack image
            # for each register image is 4 bytes long and they are
            # stored linearly. So if at an offset of 0x00 on the stack
            # you would get ebx (arg0) then 0x04 would be ecx (arg1)
            # and so forth.
            return -1


        
    return 1;

