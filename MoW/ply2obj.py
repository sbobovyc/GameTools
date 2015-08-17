from __future__ import print_function

import argparse
import os
import struct

import ply

parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', help='Input file')
parser.add_argument('outfile', nargs='?', default=None, help='Output file')
parser.add_argument('--uvy', default=False, action='store_true', help='Translate UV down in y direction (AS2)')
args = parser.parse_args()
infile = args.infile
outfile = args.outfile
translate_uv_y = args.uvy

if outfile == None and infile != None:
    outfile = os.path.basename(infile).split('.')[0] + ".obj"

if infile != None and os.path.splitext(infile)[1][1:].strip() == "ply":
    p = ply.PLY(infile, translate_uv_y)
    p.dump(outfile)
    
else:
    print("Nothing happened")
    parser.print_help()
