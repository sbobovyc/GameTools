"""
Created on October 7, 2012
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
import struct
import os
import re


def dump_file(fd, filepath, offset, size):
    saved_position = fd.tell()
    fd.seek(offset)
    data = fd.read(size)
    fout = open(filepath, "wb")
    fout.write(data)
    fout.close()
    fd.seek(saved_position)

def dump_section(fd, offset, outdir, file_filter=None, verbose=False, dry=False):
    fd.seek(offset)
    next_section_offset, = struct.unpack('>I', f.read(4))
    entries, = struct.unpack('>I', f.read(4))
    if verbose:
        print "Next section:", hex(next_section_offset)    
        print "Entries:", entries
        print "+++++++++++++++++++++++++++++"

    for i in range(0, entries):
        length, = struct.unpack('>I', f.read(4))
        length = int(length)
        filename = f.read(length)
        offset, = struct.unpack('>I', f.read(4))
        file_length, = struct.unpack('>I', f.read(4))
        crc32, = struct.unpack('>I', f.read(4))

        if verbose:
            print "File", i
            print "Length of filename:", length
            print filename
            print "File offset:", hex(offset)
            print "File legnth:", hex(file_length)
            print "CRC32:", hex(crc32).rstrip('L')
            print "+++++++++++++++++++++++++++++"
        # dumpt out file
        if not dry:
            match = True
            if file_filter != None:
                match = re.search(file_filter, filename)
                
            if match:
                dump_file(f, os.path.join(outdir, filename), offset, file_length)
            

    return next_section_offset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
                                     'Tool that can unpack Planetside 2 pack files.\n' \
                                     'You can add a regex expression to only dump out certain files.\n' \
                                     'For example, -f "xml|txt", will only dump xml or txt files.' \
                                     )

    parser.add_argument('file', nargs='?', help='Input file')
    parser.add_argument('outdir', nargs='?', help='Output directory')
    parser.add_argument('-i', '--info', default=False, action='store_true', help='Output information about pack file')
    parser.add_argument('-n', '--dry', default=False, action='store_true', help='Perform a dry run, don\'t actually write out files.')
    parser.add_argument('-f',  '--filter', default=None, action='store', help='Regex filter')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Show detailed output.')


    args = parser.parse_args()
    file = args.file
    outdir = args.outdir
    info = args.info
    verbose = args.verbose
    dry = args.dry
    file_filter = args.filter

    if file != None and info != False:
        info_filepath = os.path.abspath(file)
        print "Not implemented yet."
            
    elif file != None:      
        extension = os.path.splitext(file)[1][1:].strip()
        pack_filepath = os.path.abspath(file)
        
        print "Unpacking %s" % pack_filepath
        
        if extension != "pack":
            print "File is not a .pack" 

        if outdir != None:            
            output_filepath = os.path.abspath(outdir)   
        else:
            output_filepath = os.path.splitext(os.path.basename(pack_filepath))[0]

        if not os.path.exists(output_filepath) and not dry:
            print "Creating", output_filepath
            os.makedirs(output_filepath)

        f = open(pack_filepath, "rb")
        next_section_offset = 0x0
        print "Dumping..."
        while(1):
            next_section_offset = dump_section(f, next_section_offset, output_filepath, file_filter, verbose, dry)
            if next_section_offset == 0x0:
                break;
        f.close()
        
                
    else:
        print "Nothing happened"
        parser.print_help()
    

    
