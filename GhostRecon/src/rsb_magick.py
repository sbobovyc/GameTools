"""
Created on November 25, 2011

@author: sbobovyc
"""
"""   
    Copyright (C) 2011 Stanislav Bobovych

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
from RSB.RSB_File import RSB_File, RSB_Magic

parser = argparse.ArgumentParser(description='Tool that can read, write and show information about Red Storm Bitmaps (RSB).')

parser.add_argument('file1', nargs='?', help='Input file')
parser.add_argument('file2', nargs='?', help='Output file')
parser.add_argument('RSB_Format', nargs='?', help="Output RSB RSB_Format. Supported formats:%s" % RSB_Magic.keys())

args = parser.parse_args()
file1 = args.file1
file2 = args.file2
RSB_Format = args.RSB_Format

if file1 != None and file2 == None and os.path.splitext(file1)[1][1:].strip() == "rsb":
    info_filepath = os.path.abspath(file1)
    rsb_im = RSB_File(filepath=info_filepath, peek=True)        
    print rsb_im
    
elif file1 != None and file2 != None and os.path.splitext(file1)[1][1:].strip() == "rsb" and \
        os.path.splitext(file2)[1][1:].strip() != "rsb":
    
    print "Converting RSB to non-RSB format."
    rsb_filepath = os.path.abspath(file1)
    rsb_im = RSB_File(filepath=rsb_filepath)
    output_filepath = os.path.abspath(file2)
    rsb_im.rsb2img(output_filepath)
    
elif file1 != None and file2 != None and \
        os.path.splitext(file1)[1][1:].strip() != "rsb" and \
        os.path.splitext(file2)[1][1:].strip() == "rsb" and \
        RSB_Format != None:
    
    print "Converting non-RSB to RSB format."
    im_filepath = os.path.abspath(file1)
    rsb_im = RSB_File()
    rsb_filepath = os.path.abspath(file2)
    rsb_im.img2rsb(RSB_Format, im_filepath, rsb_filepath)
    
else:
    print "Nothing happened"
    parser.print_help()
        
