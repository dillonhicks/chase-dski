#!/usr/bin/env python
#
#
# Cross check the system call data accumulated from different sources
# to find unknown gaps in the data.
#
from syscallargstable import name_to_args
from syscallnumbers import number_to_name

def main():
    for number, name in number_to_name.items():
        try:
            name_to_args[name]
        except KeyError:
            print 'Unknown args for: ', number, name


if __name__ == "__main__":
    main()
