"""
Created on December 19, 2012
"""
"""   
    Copyright (C) 2012 Stanislav Bobovych

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import os

def gfx2swf(inpath, outpath):
    with open(inpath, "rb") as infile:
        data = infile.read()
        with open(outpath, "wb") as outfile:
            outfile.write(data)
            outfile.seek(0x0)
            outfile.write("CWS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
                                     'Tool that converts Planetside 2 gfx files to swf.\n' \
                                     )

    parser.add_argument('infile', nargs='?', help='Input file')
    parser.add_argument('outfile', nargs='?', help='Output file')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Show detailed output.')

    args = parser.parse_args()
    infile = args.infile
    outfile = args.outfile
    verbose = args.verbose

    if infile != None:
        gfx_filepath = os.path.abspath(infile)        

        if outfile == None:
            swf_filepath = os.path.splitext(infile)[0]+".swf"
        else:
            swf_filepath = os.path.abspath(outfile)
            
        
        print "Converting %s to %s" % (gfx_filepath, swf_filepath)
        gfx2swf(gfx_filepath, swf_filepath)
        
    else:
        print "Nothing happened"
        parser.print_help()        
