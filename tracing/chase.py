#!/usr/bin/env python
"""
TODO: filter dski events by the child's pid.

This code was adapted from traceme and discovery/tools.py.
"""
import sys
import os
import tempfile
import subprocess
import pyccsm.ccsmapi as ccsmapi
from datastreams import dski
from datastreams import dsui

class CCSMContext(object):
    
    def __init__(self, set_name='dskiperf', pid=None):
        self.fd = None
        self.set_name = set_name
        if not pid:
            self.pid = os.getpid()
        else:
            self.pid = pid

        self.thread_name = "%s_%d" % (self.set_name, self.pid)

    def open(self):

        # Create the CCSM set representing the traced thread.
        self.fd = ccsmapi.ccsm_open()
        ccsmapi.ccsm_create_set(self.fd, self.set_name, 0)        
        ccsmapi.ccsm_create_component_self(self.fd, self.thread_name)
        ccsmapi.ccsm_add_member(self.fd, self.set_name, self.thread_name)
        

    def close(self):
        """
        Actions taken after command execution.
        Child class can override.
        """
        ccsmapi.ccsm_remove_member(self.fd, self.set_name, self.thread_name)
        ccsmapi.ccsm_destroy_component_by_name(self.fd, self.thread_name)
        ccsmapi.ccsm_destroy_set(self.fd, self.set_name)
        return ccsmapi.ccsm_close(self.fd)


class Perf(object):

    DSTRM_NAME = 'perfdstrm' 
    CHANNEL_NAME = 'chan1'
    FILTER_RESPONSE = 'ACCEPT'

    def __init__(self):
        self.buffer_count = 50
        self.buffer_size = 500000


        self.enabled_families = [
            'FORK',
            'SYSCALL',
        ]

        self.pid = None




    def open_dski_context(self, name=None ):
        """
        Actions taken prior to command execution.
        """
        
        if name:
            name = ''.join(filter(lambda s: s.isalpha(), name))
            suffix = '_%s_dski' % name
        else:
            suffix = '_dski'
            
            ds_context = None
                
        try:
            # Create the DS Python context for configuration and
            # logging of the event stream. Note that we tell it the
            # name of the logging output file, which it opens and
            # associates with this context
            #
            datadir = tempfile.mkdtemp(suffix=suffix, dir=os.getcwd())

            # owner = xrw, group = xrw, other = xr
            os.chmod(datadir, 0775)
            ds_context = dski.dski_context(datadir)

        except IOError:
            print "Unable to open DSKI device. Is the module loaded???"
            raise

        # Allocate the desired number of buffers and the total
        # buffer size as configured and associate them with
        # this DSKI context. Note that these resources are
        # associated with the name "chan1".
        #
        chan = ds_context.create_channel(
            self.CHANNEL_NAME, self.buffer_size, self.buffer_count, 0)

        # This actually creates the data stream, named "ds1"
        # which will use the buffer resouces represented by
        # "chan1".
        #
        ds = ds_context.create_datastream(self.DSTRM_NAME, self.CHANNEL_NAME)

        # Enable DSKI for the families that were listed above
        #
        for ename in self.enabled_families:
            ds.enable_family(ename)

        # Start DSKI
        ds_context.start_logging()

        return ds_context


    def close_dski_context(self, ds_context):
        return ds_context.close()


    def open_ccsm_context(self):
        ccsm_context = CCSMContext()
        ccsm_context.open()
        return ccsm_context


    def close_ccsm_context(self, ccsm_context):
        return ccsm_context.close()


    def apply_active_filters(self, ds_context, ccsm_context):
        datastream = ds_context.datastreams[self.DSTRM_NAME]
        
        datastream.task_filter(
            ccsm_context.pid, ccsm_context.set_name, 
            self.FILTER_RESPONSE)

    

    def call(self, args):
#        return os.system(args)
        return subprocess.call(args)

        
    def trace(self, *args):

        ccsm_context = self.open_ccsm_context()
        ds_context = self.open_dski_context(name=args[0])
#        ds_context.perf_enable()
#        self.apply_active_filters(ds_context, ccsm_context)

        self.call(args)

#        ds_context.perf_disable()

        self.close_dski_context(ds_context)    
        self.close_ccsm_context(ccsm_context)

if __name__ == "__main__":
    perf = Perf()
    perf.trace(*sys.argv[1:])
