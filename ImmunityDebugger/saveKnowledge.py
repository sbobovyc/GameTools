#!/usr/bin/env python

import immlib
import pickle

def main(args):
    imm = immlib.Debugger()
    knowledge = []
    for kID in imm.listKnowledge():
        info = imm.getKnowledge(kID)
        knowledge.append((kID, info))
    with open("C:\\Users\\sbobovyc\\workspace\\immunity_knowledge.pickle", 'wb') as f:
        pickle.dump(knowledge, f)

    imm.log("Saved %i items of knowledge" % len(knowledge))
    return "Finished"
    
