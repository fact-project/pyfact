
#! /usr/bin/python
# ----------------------------------------------------------------------------
#
# -*- coding: iso-8859-1 -*-
#
# debug.py
# 
# Logging module
#
# TODO: make everything object oriented and add support for more levels of
# filtering
#
# Needs python > 2.0. Might work with 1.5.X and above
from __future__ import print_function
__version__="1.0"
__date__="2006"
__author__="Radu Stoica"

# ----------------------------------------------------------------------------

import sys, string, os

#global _DEBUG, _VERBOSE, _ERROR
_DEBUG   = 0
_VERBOSE = 1
_ERROR   = 1

__private = 'test'

__err = sys.stderr
__out = sys.stdout
__dbg = sys.stdout

def resetErrorStream():
    __err = sys.stderr

def resetOutputStream():
    __out = sys.stdout

def resetDebugStream():
    __dbg = sys.stdout

def setErrorStream(fileDescriptor):
    if not hasattr(fileDescriptor, 'write'):
        raise AttributeError("File descriptor %s has no write method"
                             %fileDescriptor)
    global __err
    __err = fileDescriptor

def setOutputStream(fileDescriptor):
    if not hasattr(fileDescriptor, 'write'):
        raise AttributeError("File descriptor %s has no write method"
                             %fileDescriptor)
    global __out
    __out = fileDescriptor

def setDebugStream(fileDescriptor):
    if not hasattr(fileDescriptor, 'write'):
        raise AttributeError("File descriptor %s has no write method"
                             %fileDescriptor)
    global __dbg
    __dbg = fileDescriptor

def setSyslog(name=None, facility=None):
    import syslog
    class SysLogger:
        def __init__(self, level=syslog.LOG_UUCP):
            self.level = level
            
        def write(self, msg):
            if msg == '\n': return
            syslog.syslog(self.level, msg)

        def flush(self):
            pass
    
    if facility is None : facility = syslog.LOG_UUCP
    syslog.openlog(name, 0, facility)
    setOutputStream(SysLogger(syslog.LOG_INFO))
    setErrorStream (SysLogger(syslog.LOG_ERR))
    setDebugStream (SysLogger(syslog.LOG_DEBUG))
    

def setDebug(value):
    global _DEBUG
    _DEBUG = value

def getCallerID(level, just=20):
    """    
    Returns a string containing informations about the function that called it
    at a desired level.
    level = how many level up should the tracing of this function start.
    
    @param level How many level up should the tracing of this function start.
    @param just: The string will be left justified with the provided input
    @return a string containing informations about the function that called it
    at the desired stack level.
    """
    linePrintStart = ""
    linePrintEnd = ""    
    try:
        raise FakeException("")
    except:
        func = sys.exc_info()[2].tb_frame
    while level >= 0:
        func = func.f_back
        level -= 1
    obj = func.f_locals.get("self", None)
    functionName = func.f_code.co_name
    if obj:
        callStr = "%-8s::%-8s %s%3d%s"\
                   %(obj.__class__.__name__,
                    func.f_code.co_name,
                    linePrintStart,
                    func.f_lineno,
                    linePrintEnd)
    else:
        callStr = "%-18s %s%3d%s"\
                  %(func.f_code.co_name, linePrintStart, 
                    func.f_lineno, linePrintEnd)
    return callStr.ljust(just)


def LAST_EXCEPTION():
    return str(sys.exc_info()[0]) + " :" + str (sys.exc_info()[1])

def SAY2(*args):
    """Prints messages adding the caller class name and the line of where the call was invoked.
    Behaviour can be changed (on/off) by modifying the _VERBOSE global var.
    """
    if _VERBOSE:
        msg = "%s: %s" %(getCallerID(2), string.join(map(str, args)))
        print >> __out, msg
        __out.flush()

def ERROR2(*args):
    """Prints messages adding the caller class name and the line of where the call was invoked.
    Behaviour can be changed (on/off) by modifying the _ERROR global var.
    """
    if _ERROR:
        msg="ERROR: in " + getCallerID(2) + ": " + string.join(map(str, args))
        print >> __err, msg
        __err.flush()

def DEBUG2(*args):
    """Prints messages adding the caller class name and the line of where the call was invoked.
    Behaviour can be changed (on/off) by modifying the _DEBUG global var.
    """
    if _DEBUG:
        msg="DEBUG: in " + getCallerID(2) + ": " + string.join(map(str,args))
        print >> __dbg, msg
        __dbg.flush()

def SAY(*args):
    """Prints messages adding the caller class name and the line of where the call was invoked.
    Behaviour can be changed (on/off) by modifying the _VERBOSE global var.
    """
    if _VERBOSE:
        msg = "%s: %s" %(getCallerID(1), string.join(map(str, args)))
        print >> __out, msg
        __out.flush()

def ERROR(*args):
    """Prints messages adding the caller class name and the line of where the call was invoked.
    Behaviour can be changed (on/off) by modifying the _ERROR global var.
    """
    if _ERROR:
        msg="ERROR: in " + getCallerID(1) + ": " + string.join(map(str, args))
        print >> __err, msg
        __err.flush()

def DEBUG(*args):
    """Prints messages adding the caller class name and the line of where the call was invoked.
    Behaviour can be changed (on/off) by modifying the _DEBUG global var.
    """
    if _DEBUG:
        msg="DEBUG: in " + getCallerID(1) + ": " + string.join(map(str,args))
        print >> __dbg, msg
        __dbg.flush()

def parseCommandLine():
    """Sets the debugging location based on the command line arguments given.
    Argument: 
        -f (foreground)    -> all logging informations goes to stdout/stderr
        -l (log) <logfile> -> prints to <logfile>
        -s (syslog)        -> prints to syslog using the UUCP facility
    """
    if '-l' in sys.argv[1:]:
        try:
            f = open(sys.argv[sys.argv.index('-l')+1], 'a+')
        except:
            raise RuntimeError("Could not open log file")
        setErrorStream(f)
        setOutputStream(f)
        setDebugStream(f)
        sys.argv.pop(sys.argv.index('-l')+1)
        sys.argv.remove('-l')
    elif '-f' in sys.argv[1:]:
        sys.argv.remove('-f')
    elif '-s' in sys.argv[1:]:
        setSyslog(sys.argv[0])
        sys.argv.remove('-s')
    else:
        setSyslog(sys.argv[0])

def commandLineUsage():
   
    print("""Output options:
        -f           -> stdout/stderr (foreground mode)
        -l <logfile> -> prints to <logfile>
        -s           -> syslog using the UUCP facility
    """)

# ---------------------------------------------------------------------------
if __name__=='__main__':
    _DEBUG = 1
    SAY("This is a normal output message")
    ERROR("This is an error message")
    DEBUG("This is a debug message")
    print("Sending the same messages through syslog")
    setSyslog("Test debugging")
    SAY("This is a normal output message")
    ERROR("This is an error message")
    DEBUG("This is a debug message")
