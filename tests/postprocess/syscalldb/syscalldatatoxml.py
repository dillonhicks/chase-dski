#!/usr/bin/env python
#
#
from __future__ import print_function
import sys
import os
import re
from pprint import pformat
import fnmatch
import argparse

from syscallargstable import name_to_args
from syscallnumbers import name_to_number, number_to_name

from lxml import etree

def syscall_to_named_element(name, args):
    elem = etree.Element(name)

    try:
        num_elem = etree.SubElement(elem, "number")
        num_elem.text = str(name_to_number[name])
    except KeyError:
        num_elem = "ERROR_UNKNOWN_NUMBER"

    try:
        for data_type, var_name in args:
            arg_elem = etree.SubElement(elem, "arg")
            type_elem = etree.SubElement(arg_elem, "type")
            type_elem.text = data_type
            var_elem = etree.SubElement(arg_elem, "name")
            var_elem.text = var_name
        
            # For future expansion
            etree.SubElement(arg_elem, 'help').text =''

    except ValueError:
        arg_elem = etree.SubElement(elem, "ERROR_BAD_ARGS_FORMAT")
        
    # For future expansion
    help_elem = etree.SubElement(elem, "help")
    help_elem.text = ''
    
    return elem


def syscall_to_numbered_element(name, args):
    try:
        #xml tags cannot start with a number so prefix n to the number
        number = 'n%s' % str(name_to_number[name])
    except KeyError:
        number = "ERROR_UNKNOWN_NUMBER"

    elem = etree.Element(number)

    name_elem = etree.SubElement(elem, "name")
    name_elem.text = name

    try:
        for data_type, var_name in args:
            arg_elem = etree.SubElement(elem, "arg")
            type_elem = etree.SubElement(arg_elem, "type")
            type_elem.text = data_type
            var_elem = etree.SubElement(arg_elem, "name")
            var_elem.text = var_name
        
            # For future expansion
            etree.SubElement(arg_elem, 'help').text =''

    except ValueError:
        arg_elem = etree.SubElement(elem, "ERROR_BAD_ARGS_FORMAT")
        
    # For future expansion
    help_elem = etree.SubElement(elem, "help")
    help_elem.text = ''
    
    return elem


def main(verbose, **kwargs):
    """
    """

    named_elem = etree.Element("syscalls_by_name")
    numbered_elem = etree.Element("syscalls_by_number")

    for name, args in name_to_args.items():
        syscall_elem = syscall_to_named_element(name, args)
        named_elem.append(syscall_elem)
        syscall_elem2 = syscall_to_numbered_element(name, args)
        numbered_elem.append(syscall_elem2)

    print(etree.tostring(named_elem, pretty_print=True))

    with open('syscalls_by_name.xml', 'w') as sc_file:
        print(etree.tostring(named_elem, pretty_print=True), file=sc_file)

    print(etree.tostring(numbered_elem, pretty_print=True))
    with open('syscalls_by_number.xml', 'w') as sc_file:
        print(etree.tostring(numbered_elem, pretty_print=True), file=sc_file)



if __name__ == '__main__':

    #####################
    # Argument Parsing
    #####################

    # Create the argument parser
    #
    parser = argparse.ArgumentParser(description='Generate systemcalls as an xml table')
    


    parser.add_argument('-v', '--verbose',
                        help='Toggle verbosity (debug output)',
                        required=False,
                        action='store_true',
                        default=False,
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
