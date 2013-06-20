#!/usr/bin/env python
"""
Monitors all system call activity on a system.
"""
import sys
import os
import cmd
import tempfile
import subprocess
import pyccsm.ccsmapi as ccsm
from datastreams import dski
from datastreams import dsui


class Perf(object):

    USAGE = "usage: %prog [<options>] <cmd>"

    def __init__(self):
        self.buffer_count = 50
        self.buffer_size = 500000


        self.enabled_families = [
            'FORK',
            'SYSCALL',
        ]

        self.pid = None




    def open_context(self, name=None ):
        """
        Actions taken prior to command execution.
        """
        
        if name:
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
            "chan1", self.buffer_size, self.buffer_count, 0)

        # This actually creates the data stream, named "ds1"
        # which will use the buffer resouces represented by
        # "chan1".
        #
        ds = ds_context.create_datastream("ds1", "chan1")

        # Enable DSKI for the families that were listed above
        #
        for ename in self.enabled_families:
            ds.enable_family(ename)

        # Start DSKI
        ds_context.start_logging()

        # note there does not seem to be a pid filter any
        # more.
        #
        # if self.pid:
        #     ds.pid_filter( ((self.pid, {'response': 'ACCEPT'}),), 'ACCEPT')

        return ds_context



    def close_context(self, ds_context):

        ds_context.close()

        pass


    def call(self, args):
#        return os.system(args)
        return subprocess.call(args)
                

    # def setup_ccsm(self, args):
    #     self.thread_name = "chase.py thread_%s_" % (self.pid)

    #     # Send information about the traceme thread.
    #     dsui_output = tempfile.mkstemp(
    #         suffix="_traced.dsui.bin", dir=self.options.outdir)

    #     # owner = rw, group = rw, other = r
    #     os.chmod(dsui_output, 0664)
    #     dsui.start(dsui_output, 0)
    #     dsui.event("TRACEME", "TRACEME_TOOL", os.getpid())
    #     dsui.close()

    #     # Create the CCSM set representing the traceme thread.
    #     self.ccsm_fd = ccsm_mod.ccsm_open()
    #     ccsm_mod.ccsm_create_set(self.ccsm_fd, self.ccsm_set_name,0)
    #     ccsm_mod.ccsm_create_component_self(self.ccsm_fd, self.traceme_thread_name)
    #     ccsm_mod.ccsm_add_member(self.ccsm_fd, self.ccsm_set_name,self.traceme_thread_name)



    # def cleanup_ccsm(self):
    #     """
    #     Actions taken after command execution.
    #     Child class can override.
    #     """
    #     ccsmapi.ccsm_remove_member(
    #         self.ccsm_fd, self.ccsm_set_name, self.traceme_thread_name)
    #     ccsmapi.ccsm_destroy_component_by_name(self.ccsm_fd, self.traceme_thread_name)
    #     ccsmapi.ccsm_destroy_set(self.ccsm_fd, self.ccsm_set_name)



        
    def trace(self, *args):

        self.pid = os.getpid()

        # outdir = self.options.outdir

        # if not os.path.isdir(outdir):
        #     os.makedirs(outdir)

        
        ds_context = self.open_context(name='sysmon')


        ds_context.perf_enable()
        print('Now collecting all system call information')
        raw_input('Press any key to exit...')
        ds_context.perf_disable()

        self.close_context(ds_context)    



if __name__ == "__main__":
    perf = Perf()
    perf.trace(*sys.argv[1:])
