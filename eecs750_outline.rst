Introduction
=============

- What is the problem.

  - There is a need for an performance evalution tool that is able to:

    - obtain as much information as possible from as little
      information

	- do it cohesively, i.e. most tools are piecewise and are
          heavy in text based processing

	- due to the nature of systems programming

- Why current solutions are inferior

  - The current solutions for performance evaluation are peicewise.

	- Requires pipeing of separate tools
	- lacks the meta systems level perspective

  - The canonical example "strace" requries a few systemcalls
    (peekuser, wait) for each of the traced slave processes
    systemcalls
 
- The implementation of chase involves a holistic approach to systems
  profiling

  - Attempts to use a set of carefully placed instrumentation points
    (DSKI) to dump binary information
	- Only four
		- systemcall enter
		- systemcall exit
		- ptrace syscall enter
		- ptrace syscall exit
	- The binary dump on enter is a copy of stack image of the
          register when the systemcall is executed
	- the binary dump on exit is a copy of the stack image of the
          return value and the number of the systemcall
  - The current iteration uses an offline postprocessing scheme
    - To reduce instrumentation effect
	- There has not been enough gathered data to know which types
          of online (activefiltering) processing would be interesting
          to take place.

Related Work
=============

- user tools that use ptrace/proc
  - such as
    - strace
    - vmstat
    - top
    - free 
    - etc.

  - These tools often need to go through multiple stages
  - use messy ascii text manipulation 
  - Not useful for the more holistic systems view

- perf
  - the defacto linux systems profiling tool
  - based off of per component events and counts 
  - can be used for tracing
    - but it is at the assembly instruction level
    - often not useful for a hgiher level narrative since one must
      have pretty detailed knowledge of the code and generated
      assembly.
  - neat feature is the ability to add dynamic tracepoints with kprobes
    - falls victim to the super complicated to use effectively domain
  - must be compiled into the kernel

- kusp datastreams
  - provides the ability to add types of events to the kernel
    - binary events 
      - name
      - timestamp
      - pid
      - optional struct binary dump 
    - histograms
    - counters

  - provides an ability to incorporate instrumentation points into
    user programs as well
  
  - events are dumped to binary files on the local disk for post
    exection processing.

  - not nailed to a specific purpose and is quite flexible and able to
    be used in seval ways in order to provide a meta level view and
    descriptions from relatively few instrumentation points.

- discovery
  - a project built off of kusp datastreams aimed at giving the
    structure and components of a computation
    - both passive and active components are considered
  - ability to narrate and visualize the sockets, threads, pipes,
    shmem, etc., that are created/used during a programs execution

- ftrace

- kprobes

- tracehook

- systemtap
  - 

- Dtrace
  - dynamic tracing
  - sun/solaris based

	
Experimental Design
====================

- The testing framework relys on automatic compilation, execution, and
  stuff.

- Broken into a few different interative steps
  - Iteration 0
    - Canonical C programs that only execute one systemcall. 
	  - Do not use the glibc wrappers, instead call the syscall() (macro?) directly with the syscall number and arguments
	  - Emphasis put on systemcalls with no arguments and intuative return values
	    - Think getpid()
	  - TODO: List programs
	  - Post processing provides a strace style output
    - UNIX

  - Ite
	
- stuff stuff stuff

Implementation
==============

*Mentionables*

- Systemcall hooks

- Syscall db
  - created by searching and plundering the kernel code using a python
    script that searches for the systemcall macro definitions. 
    
    - able then to obtain:
      - name of the system call
      - type and name of the arguments

  - other python scripts then use glibc headers and kernel sources to
    obtain the systemcall numbers and extra information
  
  - The parsed data is then agglomerated and stuff

- postprocessing

- Kconfigs

- rt patch

Conclusions
===========

- future work
  - slowly extend to give a holistic systems level view
  

Why is it not already solved, other solutions are inferior, or it is a topic which is worth studying in order to learn more about it.
Why was your solution to the problem superior or interesting in some way, or your study of a question worth doing.
How the rest of the paper is structured. What issues are addressed in which sections.
Related Work
What other efforts to solve this problem exist and why do they solve it less well than the effort discussed in this paper. In the case of a pure functional or performance evaluation, why is the information not already available in the form addressed by the project.
What other efforts to solve related problems or investigate related topics exist, which are not identical to the proposed effort but whose results or methods provide relevant information or insight. Why are these related efforts or studies not a complete answer to the proposed question, and the proposed work is thus worth doing.
Implementation

High level summary of what you implemented introducing all of the relevant concepts necessary to understand the proposed work.
Background information, if any, required by the target audience to understand what your implemented work was and to understand your explanation of how it works.
What you implemented and how it works.
Evaluation
Experimental design for your implementation. List the questions you were trying to answer. Describe the experimental design including the metrics, parameters, and methodology.
For each experiment, describe its metric(s), parameter(s), and method. Describe what question(s) is is supposed to answer. Then present the results and lead the reader through an interpretation of those results which shows how it answers the relevant questions and any other interesting points the results raise.
At the end of this section have a summary or conclusion subsection descussing why the reader should conclude that the work was a good idea, why it was well done, and why the reader should be impressed.
Conclusions
Short summary of what the problems is, why your approach is worth considering as a good solution to the real problem. Why your solution is better than other existing or related efforts, and why the reader should be impressed.
What you or others can or should do in the future to extend the work done. Improving the described approach to apply it to new or harder problems, or modifying the approach to apply it to related but different problems.
Conclusion
