#!/bin/env python
# -*- coding: UTF-8 -*-
"""
An example for showing how a client can run the commands on a DIM server. 

"""

import sys
import math
import random

# Import the pydim module
import fact.dim as pydim

def command1():
    
    f = random.choice([math.pi, math.e, 42])
    
    #The argument must be a tuple
    args = (f,)
    print "Calling command 1. Arguments: %s" % args
    res = pydim.dic_cmnd_service("example-command-1", args, "F")

def command2():
    n = random.choice(range(5))
    text = random.choice(["hola", "hi", "bonjour"])
    
    args = (n, text)
    print "Calling command 2. Arguments: %s, %s" % args
    res = pydim.dic_cmnd_service("example-command-2", args, "I:1;C")

def help():
    print """This is a DIM client for the commands example server.

The following options are available:
    
    1     Run command 1
    2     Run command 2
    H     Display this help text
    Q     Exit this program

    """

def main():

    help()

    exit = False
    while not exit:
        
        action = raw_input("Action (Press 'Q' to exit): ")

        if action == "1":
            command1()
        elif action == "2":
            command2()
        elif action == "Q":
            exit = True
            print "Bye!"
        elif action == "H":
            help()

if __name__ == "__main__":
    main()