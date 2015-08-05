#!/usr/bin/env python

import immlib
import argparse
import pickle
import os


def main(args):
    imm = immlib.Debugger()
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('--search', '-s', dest='search_address')
    parser.add_argument('--printk', '-p', default=False, action='store_true')
    parser.add_argument('--clean', '-c', default=False, action='store_true')
    parser.add_argument('--save', default=False, action='store_true')
    parser.add_argument('--load', default=False, action='store_true')
    parser.add_argument('--path')

    par_arg = parser.parse_args(args)
    #imm.log("%s" % par_arg)
    
    if par_arg.path == None:
        par_arg.path = os.getcwd()

    if par_arg.printk != False:
        count = 0
        for info in imm.listKnowledge():
            imm.log(info)
            count += 1
        imm.log("Printed %i items of knowledge" % count)    
    elif par_arg.search_address != None:
        knowledge = imm.getKnowledge("%s" % par_arg.search_address)
        if knowledge != None:
            imm.log("Found %s" % par_arg.search_address)
    elif par_arg.clean == True:
        imm.cleanKnowledge()
    elif par_arg.save == True:
        knowledge = []
        for kID in imm.listKnowledge():
            info = imm.getKnowledge(kID)
            knowledge.append((kID, info))
        path = os.path.join(par_arg.path, "knowledge.pickle")
        with open(path, 'wb') as f:
            imm.log("Saving %s" % path)
            pickle.dump(knowledge, f)

        imm.log("Saved %i items of knowledge" % len(knowledge))
    elif par_arg.load == True:
        knowledge = []
        count = 0
        path = os.path.join(par_arg.path, "knowledge.pickle")
        with open(path, 'rb') as f:
            imm.log("Loading %s" % path)
            knowledge = pickle.load(f)
        for data in knowledge:
            #imm.log("%s %s" % (data[0],data[1]))
            imm.addKnowledge(data[0],data[1])
            count += 1
        imm.log("Loaded %i items of knowledge" % count)        
    
    return "Finished"
    
