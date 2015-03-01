#!/bin/env python
# -*- coding: UTF-8 -*-
"""
An example of a DIM server with commands.

"""

import sys
import time

# Import the pydim module
import fact.dim as pydim

def command_callback1(value, tag):
    """
    
    value: A tuple containing a float
    tag: A context argument (possibly empty)
    
    """
    print "command_callback1 called. Argument: %s %d" % (value[0], tag)

def command_callback2(cmd, tag):
    """
    
    cmd: A tuple containing an integer and a string of variable length
    tag: A context argument (possibly empty) 
    """
    print "command_callback2 called. Arguments: %s %s and tag%s" % (cmd[0], cmd[1], tag)

def main():
    cmd1 = pydim.dis_add_cmnd('example-command-1', 'F', command_callback1, 2)
    cmd2 = pydim.dis_add_cmnd('example-command-2', 'I:1;C', command_callback2, 3) 

    if not cmd1 or not cmd2:
      print "An error occurred while registering the commands"
      sys.exit(1)

    pydim.dis_start_serving("example-commands")
    print "Starting the server"
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
