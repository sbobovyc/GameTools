#!/usr/bin/env python

import immlib

def main(args):
    imm = immlib.Debugger()
    count = 0
    for info in imm.listKnowledge():
        imm.log(info)
        count += 1
    imm.log("Printed %i items of knowledge" % count)
    return "Finished"
