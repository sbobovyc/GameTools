#!/usr/bin/env python

import immlib
from immlib import LogBpHook, BpHook


class ReturnBP(BpHook):
    def __init__(self):
        BpHook.__init__(self)
        
    def run(self, regs):
        imm = immlib.Debugger()
        eip = regs["EIP"]
        imm.log("bp, EIP is 0x%08X " % eip)
        imm.addKnowledge("0x%08X" % eip, eip)
        #self.UnHook()
        imm.deleteBreakpoint(eip, eip+4)
        imm.run()
        
class ReturnLog(LogBpHook):
    def __init__(self):
        LogBpHook.__init__(self)
    
    def run(self, regs):
        imm = immlib.Debugger()
        eip = regs["EIP"]
        imm.log("log, EIP is 0x%08X " % eip)
        imm.addKnowledge("0x%08X" % eip, eip)
        self.UnHook()
        imm.deleteBreakpoint(eip, eip+4)

def main(args):    
    imm = immlib.Debugger()    
    module = imm.getModule(imm.getDebuggedName())
    imm.log("module %s at 0x%08X" % (module.getName(), module.getBase()))
    use_log_bp = True

    if len(args) > 0 and args[0] == "false":
        imm.log("Using non logging bp")
        use_log_bp = False
    
    
    # make sure module is analysed
    if not module.isAnalysed():
        module.Analyse()
    knowledge = imm.listKnowledge()
    hooked = 0
    not_hooked = 0
    
    for f in imm.getAllFunctions(module.getBase()): 
        for ret in imm.getFunctionEnd(f):
            if "0x%08X" % ret not in knowledge:
                #imm.log("function 0x%08X ret at 0x%08X" % (f, ret))
                if use_log_bp:
                    hook = ReturnLog()
                    hook.add("ReturnLog 0x%08X"%f, ret)                
                    hooked +=1
                else:
                    hook = ReturnBP()
                    hook.add("ReturnBP 0x%08X"%f, ret)                
                    hooked +=1
                    
                # i think fasthook because fast hook is over writing rets, getFunctionEnd is having trouble
                #fast = immlib.FastLogHook(imm)
                #fast.logFunction(ret)
                #fast.logRegister("EIP")
                #fast.Hook()
            else:
                not_hooked += 1
        
    
    imm.log("Hooked %i, skipped %i" % (hooked, not_hooked))             
    return "Found returns, attached hooks"
