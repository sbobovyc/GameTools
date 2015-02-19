"""
Copyright (C) 2014 Stanislav Bobovych
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
import argparse
import struct
import StringIO
import os
import errno
import sys

class brz_file(object):
    def __init__(self, path):
        self.path = path
        self.file_count = 0
        self.brz_file_list = []
        
    def unpack(self, outdir, verbose=False):
        with open(self.path, "rb") as f:
            u1,count = struct.unpack("<II", f.read(8))
            print("Unknown int: %i, Count: %i" % (u1, count))
            for i in range(0,count):
                offset, = struct.unpack("<I", f.read(4))
                name_len, = struct.unpack("<H", f.read(2))
                file_name, = struct.unpack("%is" % name_len, f.read(name_len))        
                dir_len, = struct.unpack("<H", f.read(2))
                dir_name, = struct.unpack("%is" % dir_len, f.read(dir_len))
                entry = brz_file_entry(file_name, dir_name, offset)
                if verbose:
                    print(entry)
                self.brz_file_list.append(entry)     
            for i in range(0, count):
                directory = os.path.join(outdir, self.brz_file_list[i].dir)
                                
                try: os.makedirs(directory)
                except OSError, err:
                    # Reraise the error unless it's about an already existing directory 
                    if err.errno != errno.EEXIST or not os.path.isdir(directory): 
                        raise
                new_file = os.path.join(outdir, self.brz_file_list[i].dir, self.brz_file_list[i].name)
                with open(new_file, "wb") as f_new:
                    f.seek(self.brz_file_list[i].offset)
                    if i != count-1:
                        file_length = self.brz_file_list[i+1].offset - self.brz_file_list[i].offset
                        f_new.write(f.read(file_length))
                    else:
                        f_new.write(f.read())   
                        
    def pack(self, directory, verbose=False):
        # walk through dirs and get file paths, file sizes and add lengths of file paths
        buf = StringIO.StringIO()
        with open(self.path, "wb") as f:
            f.write(struct.pack("II", 0,0))
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    entry = brz_file_entry(filename, dirpath, 0, os.path.getsize(os.path.join(dirpath, filename)))
                    print(entry)
                    self.brz_file_list.append(entry)
            f.seek(4)
            f.write(struct.pack("<I", len(self.brz_file_list)))
            offset = f.tell()
            for entry in self.brz_file_list:
                offset += len(struct.pack("<IH%isH%is" % (len(entry.name), len(entry.dir)), entry.offset, len(entry.name), entry.name, len(entry.dir), entry.dir))
                with open(os.path.join(entry.dir, entry.name), "rb") as ef:
                    buf.write(ef.read())
            for entry in self.brz_file_list:
                f.write(struct.pack("<IH%isH%is" % (len(entry.name), len(entry.dir)), offset, len(entry.name), entry.name, len(entry.dir), entry.dir))
                offset += entry.file_size
            f.write(buf.getvalue())
            
            
class brz_file_entry(object):
    def __init__(self, name, path, offset, size=0):
        self.name = name
        self.dir = path
        self.offset = offset
        self.file_size = size
        
    def __str__(self):
        return "%s, %s, 0x%x, %i" % (self.dir, self.name, self.offset, self.file_size)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool that can unpack/pack Combat Mission brz files.')
    parser.add_argument('filepath', nargs='?', help='BRZ file or directory')
    parser.add_argument('-o', '--outdir', default=None, help='Output directory')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print info as files are unpacked')
    args = parser.parse_args()

    filepath = args.filepath
    outdir = os.path.basename(filepath).split('.')[0] if args.outdir == None else args.outdir            
    if os.path.isfile(args.filepath):
        brz_file(filepath).unpack(outdir, args.verbose)    
    else:
        print("Packing does not work yet")
        #indir = os.path.dirname(filepath)
        #outfile = indir + ".brz"
        #brz_file(outfile).pack(indir)
    


            
            
