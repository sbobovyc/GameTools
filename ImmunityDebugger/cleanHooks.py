#!/usr/bin/env python

import immlib

def main(args):
    imm = immlib.Debugger()
    imm.cleanHooks()    
    for hook in imm.listHooks():
        imm.log(hook)
    return "Cleaned hooks"
