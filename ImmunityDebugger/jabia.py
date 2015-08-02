#!/usr/bin/env python

import immlib
import struct
from immlib import LogBpHook, BpHook


class ReadFileHook(LogBpHook):
    def __init__(self, file_path, handle):
        LogBpHook.__init__(self)
        self.file_path = file_path
        self.handle = handle

    def run(self, regs):
        imm = immlib.Debugger()
        callstack = imm.callStack()
        for a in callstack:
            #imm.log("Address: %08x - Stack: %08x - Procedure: %s - frame: %08x - called from: %08x" %( a.address,a.stack,a.procedure,a.frame,a.calledfrom))
            if "Buffer" in a.getProcedure():
                buffer_address = "0x" +  a.getProcedure().split('=')[1].strip()
                imm.log("File %s buffer at %s" % (self.file_path, buffer_address))
                
            
class CreateFileReturnHook(LogBpHook):
    def __init__(self, file_path):
        LogBpHook.__init__(self)
        self.file_path = file_path
    
    def run(self, regs):
        imm = immlib.Debugger()
        # get value in EAX, which is the file handle
        handle = regs["EAX"]
        imm.log("EAX is 0x%08X " % handle)

        read_hook = ReadFileHook(self.file_path, handle)
        read_hook.add("ReadFileHook", imm.getAddress("ReadFile"))
            
            
class CreateFileHook(LogBpHook):
    def __init__(self, file_path):
        LogBpHook.__init__(self)
        self.file_path = file_path

    def run(self, regs):
        imm = immlib.Debugger()
        callstack = imm.callStack()
        for a in callstack:
            #imm.log("Address: %08x - Stack: %08x - Procedure: %s - frame: %08x - called from: %08x" %( a.address,a.stack,a.procedure,a.frame,a.calledfrom))
            #TODO what if CreateFile fails?
            
            if self.file_path in a.getProcedure():
                #imm.log("Address: %08x - Stack: %08x - Procedure: %s - frame: %08x - called from: %08x" %( a.address,a.stack,a.procedure,a.frame,a.calledfrom))                
                #imm.log("Found it! %s" % hex(a.calledfrom+6))
                #imm.setUnconditionalBreakpoint(a.calledfrom+6)
                hook_return = CreateFileReturnHook(self.file_path)
                hook_return.add("CreateFileReturnHook", a.calledfrom+6)
            
class MemScanHook(BpHook):
    def __init__(self, buf):
        BpHook.__init__(self)
        self.buf = buf
    def run(self, regs):
        imm = immlib.Debugger()
        for a in imm.callStack():
            imm.log("In MemScanHook, Address: %08x - Stack: %08x - Procedure: %s - frame: %08x - called from: %08x" %( a.address,a.stack,a.procedure,a.frame,a.calledfrom))
            
            for address in imm.searchOnWrite(self.buf):
                imm.log("Found patter at address: 0x%08x" % address)
                imm.cleanHooks()
                module = imm.getModule(imm.getDebuggedName())
                base = module.getBase()
                end = base + module.getSize()
                imm.deleteBreakpoint(base, end)
                imm.pause()
                return                            
            imm.run()
        
def main(args):
    imm = immlib.Debugger()
    module = imm.getModule(imm.getDebuggedName())
    imm.log("module %s at 0x%08X" % (module, module.getBase()))
    buf = "6D 65 64 75 6E 61 5F 61 69 72 70 6F 72 74 00 BA 0E 00 00 00 0F 00 00 00 00 00 00 00 27 00 00 00".replace( ' ', '' ).decode("hex")
    knowledge = imm.listKnowledge()

    # set breakpoint on place where save game is loaded
    imm.setBreakpoint(0x40BF80)
    # make sure module is analysed
    if not module.isAnalysed():
        module.Analyse()
    for f in imm.getAllFunctions(module.getBase()):        
        for ret in imm.getFunctionEnd(f):
            if "0x%08X" % ret not in knowledge:
                imm.log("function 0x%08X ret at 0x%08X" % (f, ret))
                h = MemScanHook(buf)
                h.add("memscan 0x%08X"%f, ret)
    
    
    """
    module_name = "kernel32.dll"
    api_name = "CreateFileW"
    #api_name = "CreateFileA"
    file_name = "myfile.bin"
    #file_name = "data_win32.dat"
        
    hook = CreateFileHook(file_name)
    f = imm.getAddress(api_name)
    hook.add("CreateFileHook", f)
    """

    return "Hook done"
