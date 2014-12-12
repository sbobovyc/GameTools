#!/usr/bin/env python

import immlib

def main(args):
    imm = immlib.Debugger()
    module = imm.getModule(imm.getDebuggedName())
    base = module.getBase()
    end = base + module.getSize()
    imm.deleteBreakpoint(base, end)    
    return "Deleted breakpoints"
