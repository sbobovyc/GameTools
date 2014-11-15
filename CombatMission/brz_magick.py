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

import argparse
import struct
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
            print(u1,count)
            for i in range(0,count):
                offset, = struct.unpack("<I", f.read(4))
                name_len, = struct.unpack("<H", f.read(2))
                file_name, = struct.unpack("%is" % name_len, f.read(name_len))        
                dir_len, = struct.unpack("<H", f.read(2))
                dir_name, = struct.unpack("%is" % dir_len, f.read(dir_len))
                if verbose:
                    print("offset", hex(offset))
                    print("name", file_name)
                    print("dir", dir_name)                    
                self.brz_file_list.append(brz_file_entry(file_name, dir_name, offset))     
            for i in range(0, count):
                directory = os.path.join(outdir, self.brz_file_list[i].dir)
                                
                try: os.makedirs(directory)
                except OSError, err:
                    # Reraise the error unless it's about an already existing directory 
                    if err.errno != errno.EEXIST or not os.path.isdir(directory): 
                        raise        
                with open(os.path.join(outdir, self.brz_file_list[i].dir, self.brz_file_list[i].name), "wb") as f_new:
                    f.seek(self.brz_file_list[i].offset)
                    if i != count-1:
                        file_length = self.brz_file_list[i+1].offset - self.brz_file_list[i].offset
                        f_new.write(f.read(file_length))
                    else:
                        f_new.write(f.read())   
                        
    def pack(self, verbose=False):
        pass
        
class brz_file_entry(object):
    def __init__(self, name, path, offset):
        self.name = name
        self.dir = path
        self.offset = offset

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool that can unpack Combat Mission brz files.')
    parser.add_argument('outdir', nargs='?', help='Output directory')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print info as files are unpacked')
    args = parser.parse_args()
    
    #filepath = "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission Battle for Normandy DEMO\Data\Normandy Demo v100.brz"            
    #filepath = "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission Battle for Normandy DEMO\Data\Normandy Demo v110.brz"
    filepath = "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission Battle for Normandy DEMO\Data\Normandy Demo v110B.brz"

    outdir = "out"
    if args.outdir != None:
        outdir = args.outdir
    print(outdir)
    brz_file(filepath).unpack(outdir, args.verbose)
    


            
            
