import argparse
import os
import struct

import ply

parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', help='Input file')
parser.add_argument('outfile', nargs='?', default=None, help='Output file')
args = parser.parse_args()
infile = args.infile
outfile = args.outfile

if outfile == None and infile != None:
    outfile = os.path.basename(infile).split('.')[0] + ".obj"

if infile != None and os.path.splitext(infile)[1][1:].strip() == "ply":
    p = ply.PLY(infile)
    p.dump(outfile)
    
else:
    print "Nothing happened"
    parser.print_help()
