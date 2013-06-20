#!/usr/bin/env python
"""

counts entry and exits

"""
from __future__ import print_function
import os
import tempfile
import logging as log
import shlex
import subprocess

POSTPROCESS_CMD_TPL = 'postprocess -f '

# Convenient suffix for the postprocessing config files created.
#
DSKI_PERF_SUFFIX = '_syscall_count.pipes'

# This template string is used to construct the postprocessing file.
#
#
POSTPROCESS_TPL = """
<main>
filter_modules = [ "perf.py", ]
filters = {
	dski1 = [
		head.input(
			file = ["./%(data_dir)s/chan1/cpu*.bin"]
			)

                perf.EnterCountFilter()

                perf.LeaveCountFilter()
		]

	}
"""


def cleanup_logging():
    log.info('exit handler called')
    log.info('stopping logging')
    log.shutdown()


def setup_logging():
    import atexit
    
    # Setup logging if we desire verbosity
    #
    log.basicConfig(stream=sys.stderr, level=log.DEBUG)
    
    # Register the exit handler that will properly shutdown
    # logging.
    #
    atexit.register(cleanup_logging)
    
    # Start logging
    log.info('logging started')
    


def create_pipeline_config(data_dir):

    config = POSTPROCESS_TPL % {'data_dir' : data_dir}

    with tempfile.NamedTemporaryFile(
        suffix=DSKI_PERF_SUFFIX, dir=os.getcwd(), 
        delete=False) as outfile:
    
        print(config, file=outfile)
    
    return outfile.name
        




def main(data_dir, verbose, *args, **kwargs):
    """
    The "main" logic function. In the convention I have started, all
    arguments to this function should be in the keyword
    style. Further, for each argument defined by the argument parser,
    there should be a corresponding argument such that "--<arg>" will
    then be an argument to main(..., arg=None). 
    
    If an argument is defined as a requried argument in the parser we
    can be resonably sure that there will not be a value of "None" by
    the time the function is called. If you wish to have a belt and
    suspenders method, go ahead and give the argument a default value
    in the parser arguements, or main(..., arg=<default>).

    The *args and **kwargs were kept as a catch all for misc args and
    options.
    """
    
    if verbose: setup_logging()
    
    configfile = create_pipeline_config(data_dir)
    
    cmd = shlex.split(POSTPROCESS_CMD_TPL + configfile)
    
    subprocess.check_call(cmd)
    
    
    

if __name__ == '__main__':

    import sys
    import signal
    import argparse


    #####################
    # Argument Parsing
    #####################

    # Create the argument parser
    #
    parser = argparse.ArgumentParser(description='Postprocess a given directory')
    
    # 
    parser.add_argument('-d', '--dir', 
                        dest='data_dir',
                        help='The dir containing DSKI PERF binary to postprocess',
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

