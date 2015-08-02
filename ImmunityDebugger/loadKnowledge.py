#!/usr/bin/env python

import immlib
import pickle

def main(args):
    imm = immlib.Debugger()
    knowledge = []
    count = 0
    with open("C:\\Users\\sbobovyc\\workspace\\immunity_knowledge.pickle", 'rb') as f:
        knowledge = pickle.load(f)
    for data in knowledge:
        #imm.log("%s %s" % (data[0],data[1]))
        imm.addKnowledge(data[0],data[1])
        count += 1
    imm.log("Loaded %i items of knowledge" % count)
    return "Finished"
    
