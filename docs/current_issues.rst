
- unable to get a full accounting for all syscalls.

    - Specifically when running obsrv_write or echo

- I have decided to dski instrumentation points in arch/x86/ptrace.c

    - SYSCALL/PTRACE_ENTER - syscall_trace_enter()
    - SYSCALL/PTRACE_LEAVE - syscall_trace_leave()
    
- The idea is that, assuming that ptrace is called for every system
  call when a command is executed under strace I will be able to
  observe syscalls and know whether or not I can produce the calls I
  cannot.
