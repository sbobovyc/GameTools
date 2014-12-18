#!/usr/bin/env python

import immlib
from immlib import LogBpHook


class MyLogBpHook(LogBpHook):
    def __init__(self):
        LogBpHook.__init__(self)

    def run(self, regs):
        imm = immlib.Debugger()
        callstack = imm.callStack()
        for a in callstack:
            imm.log("Address: %08x - Stack: %08x - Procedure: %s - frame: %08x - called from: %08x" %( a.address,a.stack,a.procedure,a.frame,a.calledfrom))
        

def usage(imm):
    imm.log("!hookapi module api")
    imm.log("!hookapi kernel32.dll CreateFileA")


def main(args):
    imm = immlib.Debugger()
    
    if not args:
        usage(imm)
        return "Wrong Arguments (Check Log Windows for the usage information)"

    module_name = args[0]
    api_name = args[1]
    
    imm.log("module name:%s api name:%s" % (module_name, api_name))
    
    module = imm.getModule(module_name)

    hook = MyLogBpHook()
    f = imm.getAddress(api_name)
    hook.add("hookit", f)
    

    return "Hook done"
