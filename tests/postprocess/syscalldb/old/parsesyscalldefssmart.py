# parses the syscall definitions and attemts to obtain incomplete defs
# (i.e. there were multiple lines and the grep did not get them)
#
# The syscall defitions were createed by running::
#
# $ find $KUSPKERNELROOT -name "*.[cChHS]" -print | xargs grep -n SYSCALL_DEFINE
#
# 
from __future__ import print_function
import sys
import re
from pprint import pformat
import systable

def main():
    contents = ""

    args_by_name = {}
    args_by_number = {}
    nr_syscall = -1

    with open('syscallsdefs.txt', 'r') as defsfile:
        contents = defsfile.read()

    for line in contents.splitlines():
        srcfile, lineno, definition = line.split(':')

        # $KUSPKERNELROOT/dir/dir/dir
        # $KUSPKERNELROOT/include/linux for example
        path_parts = srcfile.split('/')


        if path_parts[1] == 'arch' and path_parts[2] != 'x86':

            print("INFO: Skipping %s. Reason: arch=%s" % 
                  (definition, path_parts[2]), file=sys.stderr)  
            continue 

        if not definition.startswith('SYSCALL_DEFINE'):
            print("INFO: Skipping %s. Reason: Not a syscall definition" % 
                  (definition,), file=sys.stderr)  

            continue

        num_args = definition[14]
        if not num_args.isdigit(): 
            print("INFO: Skipping %s. Reason: Not an expected definition "
                  "style (it's probably old." % 
                  (definition,), file=sys.stderr)  
            continue
        
        num_args = int(num_args)

        if not definition.strip().endswith(')'):
            print("INFO: Skipping %s from %s."
                  "Reason: Not a COMPLETE definition" % 
                  (definition, srcfile), file=sys.stderr)  
            continue

        definition = definition.strip().replace(')', '')

        macro, macro_args = definition.split('(', 1)

        if num_args > 0:
            macro_args =  macro_args.split(',')
            name = macro_args[0]
            args = macro_args[1:]
        else:

            name = macro_args.strip()
            args = ()

        args = map(lambda s: s.strip(), args)

        
        args_by_name[name] = []
        try:
            nr_syscall = systable.NAME_TO_NUMBER[name]
            
        except KeyError:
            print("INFO: Unknown syscall name %s." % name)  
            nr_syscall = -1

        args_by_number[nr_syscall] = []

        dt = None
        var = None
        for i, arg in enumerate(args):
            if i % 2 == 0:
                dt = arg
                continue
            var = arg
            args_by_name[name].append((dt,arg))
            args_by_number[nr_syscall].append((dt,arg))
                
    print(pformat(args_by_name))
    print(pformat(args_by_number))
    print(len(args_by_name))
    print(len(args_by_number))
if __name__ == "__main__":
    main()
