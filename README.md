**tracing**

First you will want to add the location of the tracing program
``chase.py`` to your binary search path::
 
    $ cd chase_dski/tracing
    $ export PATH=$PATH:`pwd`

A typical trace (a chase) is executed by::

    $ chase.py <cmd> [args ...]
    ... lots of output ...    


To see the results of the trace you must first postprocess the dski
binary data created by executing the previous command::

    $ cd chase_dski
    $ ./tests/postprocess/postprocess.py -d <tmp-dir>

Which, in turn creates a file, ``perf_pp.out``, which contains the
trace narrative::

    $ more perf_pp.out


**files**

tracing/chase.py: Python script that opens a dski systemcall tracing context
    and dumps the binary data to a temp directory in the current
    working directory. These directories will have the form
    ``XXXX_perf_dski/``.

perf.py: Datastreams postprocessing filter that recreates strace
    output. Completed postprocessing file (ie the race narrative) is
    dumped to a file "perf_pp.out". 

postprocess.py: a script that wraps the postprocess command provided
    by the kusp RPM install. It simply create a postprocess
    configuration file from a template string (substituting
    commandline arguments) and calls postprocessing with the created
    configuration file.



**directories**

- docs: notes about various issues of the project and pertinent
        documents from other sources.

- srcs: Sources of other projects like strace and glibc which are
  useful in discovering information about syscalls, tracing, etc.

- syscalldb: directory containing all the growing amount of compiled
  information from various sources about systemcalls. For example,
  their names, numbers, arguments, manpages, flags, etc. 

  In progress are a set of scripts that attempt to compile information
  from various sources and create tables tables that aggregate all of
  data about a specific syscall into one place. Currently the
  intermediate info is in the form of python dictionaries but the end
  result should be an XML file or files that should contain elements
  that define per syscall::

    - name of syscall
    - number of syscall
    - args list, and for each arg
      
        - c data type
        - varibale name 

        - depending on the data type
      
           - for flags, give the acceptable flag values and their
             symbols (or a reference thereto)

	   - for user buffers, whether the buffer is a read | write
             buffer

	   - for user structs, how to parse the struct from python
             (the format specified by the stuct module)
 
    - A list of errors and for each error

        - how they are caused

 
  Sources include but are not limited to:

    - glibc
    - strace 
    - linux kernel
    - /proc/kallsysms
    
  
- tests: Obviously a directory for user program tests. These are
  described more in depth at
  ``$KUSPROOT/docs/datastreams/tools/chase.rst``
  

