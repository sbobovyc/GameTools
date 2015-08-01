#!/usr/bin/env python

import immlib
from immlib import LogBpHook, BpHook

class ReturnLog(LogBpHook):
    def __init__(self):
        LogBpHook.__init__(self)
    
    def run(self, regs):
        imm = immlib.Debugger()
        eip = regs["EIP"]
        imm.log("EIP is 0x%08X " % eip)
        imm.addKnowledge("0x%08X" % eip, eip)
        self.UnHook()
        imm.deleteBreakpoint(eip, eip+4)

def main(args):
    imm = immlib.Debugger()
    module = imm.getModule(imm.getDebuggedName())
    imm.log("module %s at 0x%08X" % (module.getName(), module.getBase()))
    """
    if args[0] == "show":
        imm.log("Show")
        fast = imm.listKnowledge()
        if not fast:
            return "Knowledge is empty"        
        for a in ret:
            imm.log(a)
        return "Done"
    """
    # make sure module is analysed
    if not module.isAnalysed():
        module.Analyse()
    for f in imm.getAllFunctions(module.getBase()):
        for ret in imm.getFunctionEnd(f):                
            imm.log("function 0x%08X ret at 0x%08X" % (f, ret))
            hook = ReturnLog()
            hook.add("ReturnLog 0x%08X"%f, ret)
            #fast = immlib.FastLogHook(imm)
            #fast.logFunction(ret)
            #fast.logRegister("EIP")
            #fast.Hook()
            
    # i think fasthook because fast hook is over writing rets, getFunctionEnd is having trouble
    return "Found returns, attached hooks"
