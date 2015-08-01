#!/usr/bin/env python

import immlib

def main(args):
    imm = immlib.Debugger()

    for info in imm.listKnowledge():
        imm.log(info)

    return "Finished"
