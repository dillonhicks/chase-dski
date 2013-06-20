#!/usr/bin/env python
#
# Creates two tables of system calls for a given source tree 
#
# 1. name -> number
# 2. number -> name
# 
#
# typical usage:
#
# $ gensyscallnumbers.py -d <src_dir>
#
# where <src_dir> is the path to the kernel root 
#
from __future__ import print_function
import sys
import os
import re
from pprint import pformat
import fnmatch
import argparse

# As of 2.6.31, the syscall table for x86 was located at the following
# assembly file.
#
syscall_table_filepath = "arch/x86/kernel/syscall_table_32.S"


def gen_lines(src_root):    
    """
    For a given kernel source root:
     
    - open the syscall table file

    - generate the lines of the file w/o leading/trailing whitespace.
    """
    filepath = os.path.join(src_root, syscall_table_filepath)
    with open(filepath, 'r') as table_file:
        for line in table_file:
            yield line.strip()


def gen_filtered_lines(lines):
    """
    Given a generator that produces a strings (lines):
    
     - Filter out lines that do not begin with '.long'
     
    """
    for line in lines:
        if not line.startswith('.long'):
            continue
        yield line


def gen_syscall_entries(lines):
    """
    Given a generator of lines in the expected format:

    - parse the syscall name from the line

    - Filter out entries labeled sys_ni_syscall as this means that
      systemcall number is not implemented.

    - generate a tuple for each line in the form (num, name)

    we can be assured that since the table is defined linearly in
    assembly that enumerating each line will give us the correct
    syscall number.

    """
    for i, line in enumerate(lines):
        parts = line.split()
        syscall_long_name = parts[1].strip()
        
        prefix, syscall_name = syscall_long_name.split('_', 1)

        if not (syscall_name.find('ni_syscall') < 0):
            continue

        yield (i, syscall_name)


def accumulate_entries_as_tables(entries):
    """
    Given a generator of syscall entries (see gen_syscall_entries)
    create two dictionaries.
   
    1. name->number
    2. number->name

    Likely only (2) will be the most useful but at this moment having
    both mappings doesn't seem like a bad just-in-case step.
    """
    name_table = {}
    num_table = {}
    for number, name in entries:
        name_table[name] = number
        num_table[number] = name

    return name_table, num_table


def main(data_dir, verbose, **kwargs):
    """
    """
    all_lines = gen_lines(data_dir)
    lines = gen_filtered_lines(all_lines)
    entries = gen_syscall_entries(lines)
    name_table, num_table = \
        accumulate_entries_as_tables(entries)

    from pprint import pformat
    
    print(pformat(name_table))
    print() 
    print()
    print(pformat(num_table))



if __name__ == '__main__':

    #####################
    # Argument Parsing
    #####################

    # Create the argument parser
    #
    parser = argparse.ArgumentParser(description='Generate systemcalls as an xml table')
    
    # 
    parser.add_argument('-d', '--dir', 
                        dest='data_dir',
                        help='kernel source root directory',
                        required=True)


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
