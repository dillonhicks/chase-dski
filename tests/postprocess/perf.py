"""
==============================================================
:mod`perf` KUSP Perf Post Processing Filters
==============================================================
    :synopsis: A Data Streams Post Processing filter for the extracting
        and narration of Group Scheduling Data Stream events.

.. moduleauthor:: Dillon Hicks <hhicks@ittc.ku.edu>

**Current Version: 1.0**


Module Changes
===============

(YYYY-MM-DD) Revision : Changes

(2012-04-14) r10394 : Created filter

"""
from __future__ import print_function
import sys
import time
from datastreams.postprocess import filtering
from datastreams.postprocess import entities
from datastreams import namespaces


from syscalldb.syscallargstable import name_to_args as sc_args
from syscalldb.syscallnumbers import number_to_name as sc_names 


class EnterCountFilter(filtering.Filter):
    expected_parameters = {
            "consume" : {
                         "types" : "boolean",
                         "doc" : "Whether to delete matching entities after processing",
                         "default" : False
                         },
    }
    
    def initialize(self):
        self.count_ptr = self.get_ns_pointer("SYSCALL/NO_PERF_ENTER")
        self.message = 'dski_syscall_trace_enter: %d'

        self.count = 0


    def process(self, entity):
        if entity.get_cid() == self.count_ptr.get_cid():
            self.count += 1
            print(self.count)

        self.send_output("default", entity)
    
    def finalize(self):
        print(self.messgage % self.count)



class LeaveCountFilter(filtering.Filter):
    
    def initialize(self):
        self.count_ptr = self.get_ns_pointer("SYSCALL/NO_PERF_LEAVE")
        self.message = 'dski_syscall_trace_enter: %d'

        self.count = 0


    def process(self, entity):
        if entity.get_cid() == self.count_ptr.get_cid():
            self.count += 1
            


        self.send_output("default", entity)
    
    def finalize(self):
        print(self.messgage % self.count)


    
class StraceFilter(filtering.Filter):
    """  
    """
    # syscall number of sys_exit_group it is a special case as it does
    # not return because the excuting thread exits.
    EXIT_NUMBER = 1
    EXIT_GROUP_NUMBER = 252
    NO_RETURN_SYSCALLS = (EXIT_NUMBER, EXIT_GROUP_NUMBER)
    MAX_NUM_ARGS = 6
    X86_ARGS =  ('bx','cx','dx','si','di','bp')

    expected_parameters = {
            "outfile" : {
                         'types' : 'string',
                         'doc'   : 'The path of the outfile to print to.',
                         'default' : ''
                         },
            
            "consume" : {
                         "types" : "boolean",
                         "doc" : "Whether to delete matching entities after processing",
                         "default" : False
                         },

            "drop_unmatched" : {
                         "types" : "boolean",
                         "doc" : "Drop SYSCALL/LEAVES that do not " \
                             "match up to SYSCALL/ENTER",
                         "default" : False
                         },

    }

    def initialize(self):
        """
        The "initialize" hook provides a location for declaring global
        variables and reading in any filter options or configuration
        file arguments specified by the expected_parameters
        dictionary. It is called before any other portion of the
        filter. The hook takes in a reference to "self" which is, as
        the name indicates, the filter itself. To create a global
        variable, just add the variable in dotted notation to "self".
        """
        
        #####################################
        #   Filter Entity Pointers
        #####################################
        

        # Hooray!
        # 
        self.syscall_enter_ptr = self.get_ns_pointer("SYSCALL/ENTER")
        self.syscall_leave_ptr = self.get_ns_pointer("SYSCALL/LEAVE")


        # This list is created to make all of the namespace pointers
        # iterable. So there can be a simple 'catch-all' loop 
        # for group scheduling events in process().
        #
        self.pointers = [
            self.syscall_enter_ptr,
            self.syscall_leave_ptr,
            ]
        

        
        
        ################################
        #  Filter Configuration Options
        ################################

        # This last parameter will simply determine if the events used
        # to generate the above intervals will be passed on to any
        # following filters, or destroyed.
        self.consume = self.params["consume"]


        self.drop_unmatched = self.params['drop_unmatched']
   
        if 'outfile' in self.params:
            # User specified an file path to which to write
            # the Group Scheduling Events, Attempt to open
            # specified file for writing.
            #
            try:
                self.outstream = open(self.params['outfile'], 'w')
            except IOError, eargs:
                # Nope, it isn't writable due to an IOError. 
                # Let them know the error and warn them that
                # the default action is to fallback to stdout
                # as an output stream if the output they 
                # specify fails to initialize.
                #
                print('Warning: Falling back to output stream sys.stdout')
                self.outstream = sys.stdout
        else:
            self.outstream = sys.stdout

        # Used to make times relative to make them easier to read.
        self.start_time = None

        self.found_enter = False
        
        self.trace_parts = []
        self.trace_msg = ''
        self.trace_fmt = '{0} {1} {2} {3} {4}'
        
        name = self.__class__.__name__
        self.prefix = name[0] if name else 'X'




    def print_trace(self):
        str_parts = [str(p) for p in self.trace_parts]
        msg = ' '.join(str_parts)
        print(msg, file=self.outstream)
        del self.trace_parts
        self.trace_parts = []


    def process(self, entity):
        """ 
        The "process" hook must be implemented when creating a custom
        filter. It is also the only hook which receives the events
        flowing down the pipeline. The 'filtering' happens here.
        """
        match = False

        

        # The first event indicates the start time.
        if not self.start_time:
            self.start_time = entity.get_nanoseconds()

    
        entity_cid = entity.get_cid()

        if not any((entity_cid == ptr.get_cid() 
                    for ptr in self.pointers)):

            self.send_output("default", entity)
            return 

        match = True

        name = entity.get_name()
            

        # Compute relative time to the beginning of the evnet log.
        time = (entity.get_nanoseconds() - self.start_time) / 10**3


        data = entity.get_extra_data()
        pid =  entity.get_pid()
        regs = data['data']

        if entity.get_cid() == self.syscall_enter_ptr.get_cid():
            

            number = regs['orig_ax']
            name = sc_names[number]
            
            try:
                args_defn = sc_args[name]
            except KeyError:
                print('Warning: no args defn for %s' % name, file=self.outstream)
                args_defn = (('??','??'),)*self.MAX_NUM_ARGS

#            num_args = len(args_defn)
#            print(num_args)
            args = ['%s=%s' % (args_defn[i][1],regs[self.X86_ARGS[i]])
                               for i in range(len(args_defn)) ]


            if not self.found_enter or not self.drop_unmatched:
                self.found_enter = True
                self.trace_msg = '%s (%s) %s()' % (self.prefix, number,name)

                self.enter_time = time

                self.trace_parts.append(self.prefix)
                self.trace_parts.append(pid)
                self.trace_parts.append(number)
                args_string = '(' + ', '.join(args) + ')'
                syscall_string = name + args_string
                self.trace_parts.append(syscall_string)
#                self.trace_parts.append(time)               
#                self.trace_parts.append(args_string)
               
            if number in self.NO_RETURN_SYSCALLS:
                self.trace_msg += " = ?? (%d)" % number
                self.trace_parts.append(' = ??')
                self.trace_parts.append(number)
                self.trace_parts.append(time)

#                print(self.trace_msg, file=self.outstream)
                self.print_trace()

                self.trace_msg = ''
                self.found_enter = False

        elif entity.get_cid() == self.syscall_leave_ptr.get_cid():

            retval = regs['ax']
            number = regs['orig_ax']
            self.trace_msg += ' = %s (%s)\n' % (retval,number)
            self.trace_parts.append('=')
            self.trace_parts.append(number)
            self.trace_parts.append(time)
            
            
            if not len(self.trace_msg):
                print("WARNING Exit with no Enter", file=self.outstream)
            
            if not self.drop_unmatched:
#                print(self.trace_msg, file=self.outstream)
                self.print_trace()
            elif self.drop_unmatched and self.found_enter:
#                print(self.trace_msg, file=self.outstream) 
                self.print_trace()

            self.trace_msg = ''
            self.found_enter = False
            
        else:
            print("huh?", file=self.outstream)
            
        

        if match and not self.consume:
            self.send_output("default", entity)




    def finalize(self):
                    
        print('', file=self.outstream)
        if self.outstream and \
                not self.outstream in (sys.stdout, sys.stderr):
            self.outstream.close()



class PtraceFilter(StraceFilter):
    expected_parameters = {
            "outfile" : {
                         'types' : 'string',
                         'doc'   : 'The path of the outfile to print to.',
                         'default' : ''
                         },
            
            "consume" : {
                         "types" : "boolean",
                         "doc" : "Whether to delete matching entities after processing",
                         "default" : False
                         },

            "drop_unmatched" : {
                         "types" : "boolean",
                         "doc" : "Drop SYSCALL/PTRACE_LEAVE'S that do not " \
                             "match up to SYSCALL/PTRACE_ENTER",
                         "default" : False
                         },

    }
    

    def initialize(self):
        """
        The "initialize" hook provides a location for declaring global
        variables and reading in any filter options or configuration
        file arguments specified by the expected_parameters
        dictionary. It is called before any other portion of the
        filter. The hook takes in a reference to "self" which is, as
        the name indicates, the filter itself. To create a global
        variable, just add the variable in dotted notation to "self".
        """
        
        #####################################
        #   Filter Entity Pointers
        #####################################
        
        StraceFilter.initialize(self)
        
        # Hooray!
        # 
        self.syscall_enter_ptr = self.get_ns_pointer("SYSCALL/PTRACE_ENTER")
        self.syscall_leave_ptr = self.get_ns_pointer("SYSCALL/PTRACE_LEAVE")


        # This list is created to make all of the namespace pointers
        # iterable. So there can be a simple 'catch-all' loop 
        # for group scheduling events in process().
        #
        self.pointers = [
            self.syscall_enter_ptr,
            self.syscall_leave_ptr,
            ]
        

        
        
    #     # ################################
    #     # #  Filter Configuration Options
    #     # ################################

    #     # This last parameter will simply determine if the events used
    #     # to generate the above intervals will be passed on to any
    #     # following filters, or destroyed.
    #     self.consume = self.params["consume"]


    #     self.drop_unmatched = self.params['drop_unmatched']
   
    #     if 'outfile' in self.params:
    #         # User specified an file path to which to write
    #         # the Group Scheduling Events, Attempt to open
    #         # specified file for writing.
    #         #
    #         try:
    #             self.outstream = open(self.params['outfile'], 'w')
    #         except IOError, eargs:
    #             # Nope, it isn't writable due to an IOError. 
    #             # Let them know the error and warn them that
    #             # the default action is to fallback to stdout
    #             # as an output stream if the output they 
    #             # specify fails to initialize.
    #             #
    #             print('Warning: Falling back to output stream sys.stdout')
    #             self.outstream = sys.stdout
    #     else:
    #         self.outstream = sys.stdout

    #     # Used to make times relative to make them easier to read.
    #     self.start_time = None

    #     self.found_enter = False
    #     self.trace_msg = ''
                        

    # def process(self, entity):
    #     """ 
    #     The "process" hook must be implemented when creating a custom
    #     filter. It is also the only hook which receives the events
    #     flowing down the pipeline. The 'filtering' happens here.
    #     """
    #     match = False

        

    #     # The first event indicates the start time.
    #     if not self.start_time:
    #         self.start_time = entity.get_nanoseconds()

    
    #     entity_cid = entity.get_cid()

    #     if not any((entity_cid == ptr.get_cid() 
    #                 for ptr in self.pointers)):

    #         self.send_output("default", entity)
    #         return 

    #     match = True

    #     name = entity.get_name()
            

    #     # Compute relative time to the beginning of the evnet log.
    #     time = (entity.get_nanoseconds() - self.start_time) / 10**3


    #     data = entity.get_extra_data()

    #     if entity.get_cid() == self.syscall_enter_ptr.get_cid():
    #         regs = data['data']
            
    #         name = regs['orig_ax'][0][0]
    #         number = regs['orig_ax'][1]

    #         if not self.found_enter or not self.drop_unmatched:
    #             self.found_enter = True
    #             self.trace_msg = 'P (%s) %s()' % (number,name)

    #         if number == 252:
    #             self.trace_msg += " = ?? (252)"
    #             print(self.trace_msg, file=self.outstream)
    #             self.trace_msg = ''
    #             self.found_enter = False

    #     elif entity.get_cid() == self.syscall_leave_ptr.get_cid():

    #         number, retval = data['data']
    #         self.trace_msg += ' = %s (%s)\n' % (retval,number)
            
            
    #         if not len(self.trace_msg):
    #             print("WARNING Exit with no Enter", file=self.outstream)
            
    #         if not self.drop_unmatched:
    #             print(self.trace_msg, file=self.outstream)
    #         elif self.drop_unmatched and self.found_enter:
    #             print(self.trace_msg, file=self.outstream) 


    #         self.trace_msg = ''
    #         self.found_enter = False
            
    #     else:
    #         print("huh?", file=self.outstream)
            

    #     if match and not self.consume:
    #         self.send_output("default", entity)




    # def finalize(self):
                    
    #     print('', file=self.outstream)
    #     if self.outstream and \
    #             not self.outstream in (sys.stdout, sys.stderr):
    #         self.outstream.close()
