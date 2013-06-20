#!/usr/bin/env python
#
# Creates a list of system calls for a given source tree as a python
# dictionary.
# 
# typical usage:
#
# $ gensyscallargstable.py -d <src_dir>
#
# where <src_dir> is the path to the kernel root (normally $KUSPKERNELROOT)
#
#
# note to myself:
#
#  $ cat /proc/kallsyms | grep -G " sys_.*"
#
# Is also another way to check the systemcalls on a currently
# executing kernel.
#
from __future__ import print_function
import sys
import signal
import os
import re
from pprint import pformat
import fnmatch
import argparse

def gen_find(pattern, root):
    """
    Walk the root directory looking for file names matching pattern.

    - Courtesy of Beasley generator slides.
    """
    for path, dirs, files in os.walk(root):
        for name in fnmatch.filter(files, pattern):
            yield os.path.join(path, name)    


def gen_filter_archx86(files):
    """
    Filter out the architecture dependent files if they do not pertain
    to our beloved x86.
    """
    for filename in files:
        if 'arch' in filename:
            if not 'x86' in filename:
                continue
        yield filename


def gen_cat(files):
    """
    For each file iterate over the file yielding a result for each
    line of each file that is in the form:
    
    (filename, line-num, line-text)   
    """
    for filename in files:
        with open(filename, 'r') as infile:    
            for i, line in enumerate(infile, start=1): 
                yield (filename, i, line)


def gen_grep(start_pat, end_pat, lines):
    """
    This is a "smart" grep as it starts matching with a start pattern
    and stops only when it finds the end pattern. this allows fo find
    definitions that were defined on multiple lines.    

    This does not properly match a few types of syscalls that appear
    to be in an old format. There are only about 5 of them.
    """
    start_regex = re.compile(start_pat)
    end_regex = re.compile(end_pat)

    matched_lines = []
    for filename, i, line in lines:
        if not matched_lines:
            # There are no matched lines yet...  Lets see if we have
            # found the start of a match.
            if start_regex.search(line):
                # Beginning of match found, add it to the matched
                # lines. 
                matched_lines.append((i,line))                
                if end_regex.search(line):
                    # the end of the match was found on the same line
                    # so we can just stop matching and yield the list
                    # of one line here.
                    yield tuple(matched_lines)
                    del matched_lines
                    matched_lines = []
                    
            else:
                # Didn't find the start of a match so continue to next
                # line.
                continue

        else:
            # we are in the middle of a match so add the next line.
            matched_lines.append((i, line))
            if end_regex.search(line):
                # this line is the end of the match so go ahead and
                # yield the lines that contain the match and clear the
                # match list.
                yield tuple(matched_lines)
                del matched_lines
                matched_lines = []
            

def gen_proper_format(matches):
    """
    Pieces together the lines matched from the grep step into a single
    string. 
    """
    for match_parts in matches:
        syscall = ''
        for i, part in match_parts:
            syscall += part.strip()
    
        yield syscall


def parse_definition_type_1(defn):
    """
    SYSCALL_DEFINE[0-6](<name>, <args>...)
    """
    defn = defn[16:-1]
    parts = defn.split(',')
    parts = [p.strip() for p in parts]

    obj = {
        'name' : parts.pop(0),
        'args' : [],
        }
    
    dtype = None
    var = None
    for i, part in enumerate(parts):
        if i % 2 == 0:
            dtype = part
        else:
            var = part
            obj['args'].append((dtype, var))
            
    return obj


def parse_definition_type_2(defn):
    """
    SYSCALL_DEFINE(<name>)(<args>...)
    """
    i = defn.find('(') + 1
    f = defn.find(')')
    obj = {
        'name' : defn[i:f],
        'args' : ['PELIGRO! WARNING! NOTDONE!'],
        }

    return obj

def parse_definition_type_3(defn):
    """

    PTREGSCALL(<name>)

    For reference:

    #define PTREGSCALL(name) \
            ALIGN; \
    ptregs_##name: \
	    leal 4(%esp),%eax; \
	    jmp sys_##name;


    """
    i = defn.find('(') + 1
    f = defn.find(')')
    obj = {
        'name' : defn[i:f],
        'args' : [('struct pt_regs *', 'regs'), 'PELIGRO! WARNING! NOTDONE!']
        }

    return obj


def gen_parse_to_objects(formatted_strings):
    """
    Parse the match strings into dictionaries.

    {
    'name' : '<syscall_name>',
    'args' : [ ('<data_type>', '<var_name>'), ...],
    }
    """
    type1_regex = re.compile('^SYSCALL_DEFINE\d')
    type2_regex = re.compile('^SYSCALL_DEFINE[(]')
    type3_regex = re.compile('^PTREGSCALL[(]')

    for string in formatted_strings:
        if type1_regex.search(string):
            obj = parse_definition_type_1(string)
        elif type2_regex.search(string):
            # the older style of syscall 
            obj = parse_definition_type_2(string)
        elif type3_regex.search(string):
            obj = parse_definition_type_3(string)
        else:
            raise ValueError(
                'ERROR: Syscall definition of unknown type: %s' % string)
        
        print(pformat(obj), file=sys.stderr)
        yield obj


def accumulate_objects_as_table(objs):
    """
    Take a generator of syscall objects and create a dictionary that
    does the mapping:
    
    name -> args_list
    """
    table = {}
    for obj in objs:
        table[obj['name']] = obj['args']

    return table 


def main(data_dir, pattern, verbose, **kwargs):
    print('This takes a min or so to run, be patient!')

    all_files = gen_find(pattern, data_dir)
    files = gen_filter_archx86(all_files)
    lines = gen_cat(files)

    # SYSCALL_DEFINE is the macro for most system calls. The super
    # special ones that requrie the pt_regs pointer (fork, execv,
    # clone) in entry.S are defined with the PTREGSCALL assembler
    # macro. Why those need the pt_regs pointer is not immediately
    # apparent and if my laziness doesn't overcome me, then I will
    # will explain why at a later time.
    #
    matches =  gen_grep('(^SYSCALL_DEFINE)|(^PTREGSCALL)', '[)]', lines)
    formatted_matches = gen_proper_format(matches)
    
    objects = gen_parse_to_objects(formatted_matches)

    table = accumulate_objects_as_table(objects)
    
    from pprint import pformat

    print(pformat(table))
    print("Number of syscalls:", len(table))



if __name__ == '__main__':

    #####################
    # Argument Parsing
    #####################

    # Create the argument parser
    #
    parser = argparse.ArgumentParser(description='Generate systemcalls as a '
                                     'python dictionary')
    
    # 
    parser.add_argument('-d', '--dir', 
                        dest='data_dir',
                        help='kernel source root directory',
                        required=True)


    # Override the file search pattern if needed
    parser.add_argument('-p', '--pattern', 
                        dest='pattern',
                        help='the file search pattern',
                        required=False,
                        default='*.[hHcCsS]')
 
    
    parser.add_argument('-v', '--verbose',
                        help='Toggle verbosity (debug output)',
                        required=False,
                        action='store_true',
                         )



    # Parsing the args creates a namespace object for this
    # script. Each argument will be a dot accessible attribute of this
    # namespace object. For example, for a given required argument
    # "--config" there will be a corresponding attribute:
    #
    # namespace.config
    # 
    namespace = parser.parse_args()


    # It is often more useful to convert the parsed arguments to a
    # dictionary such that we can do a mapping when calling the main
    # function. The vars() function converts the public attributes of
    # an object (in the case of the namespace object, the arguments)
    # to a dictionary.
    #
    args = vars(namespace)
    

    #####################################
    # Calling main() with args dictionary
    #####################################

    main(**args)
