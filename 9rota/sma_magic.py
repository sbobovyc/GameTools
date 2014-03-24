"""
Copyright (C) 2013 Stanislav Bobovych

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
import sys
import errno
import zlib

class File(object):
    def __init__(self, path, offset, size, unk):
        self.path = path
        self.offset = offset
        self.size = size
        self.unk = unk

    def create(self, file_pointer, deflate=True):
        directory = os.path.dirname(self.path)
        try: os.makedirs(directory)
        except OSError, err:
            # Reraise the error unless it's about an already existing directory 
            if err.errno != errno.EEXIST or not os.path.isdir(directory): 
                raise
        if self.size > 0:
            file_pointer.seek(self.offset)
            data = file_pointer.read(self.size)            
            with open(self.path, "wb") as f:
                # decompress
                if self.unk != 0 and deflate:
                    data = zlib.decompress(data)
                f.write(data)

class SMA(object):
    def __init__(self):
        self.magic = "SMA"
        self.version = 2
        self.num_files = None
        self.unknown = 0
        self.files = []

    def unpack(self, path, parse_only=False, deflate=True, verbose=False):
        with open(path, "rb") as f:
            self.magic, = struct.unpack("3s", f.read(3))
            self.version, = struct.unpack("<H", f.read(2))
            print self.magic, self.version
            if self.version != 2:
                print "Wrong version detected!"
                sys.exit()

            self.num_files, = struct.unpack("<I", f.read(4))
            print "Number of files:", self.num_files

            self.unknown, = struct.unpack("<I", f.read(4))

            for i in range(0, self.num_files):
                count, = struct.unpack("B", f.read(1))
                path, = struct.unpack("%is" % count, f.read(count))
                file_size, = struct.unpack("<I", f.read(4))
                unk1, = struct.unpack("<I", f.read(4))
                offset, = struct.unpack("<I", f.read(4))
                # unk1 is not adler32 or crc32
                if verbose:
                    print "%s, unknown %s, file size %s, offset: %s" % (path,  hex(unk1), hex(file_size), hex(offset))
                
                self.files.append(File(path, offset, file_size, unk1))

            if not parse_only:
                for fil in self.files:
                    fil.create(f, deflate)

    
    def pack(self, directory, output_file):
        total_filepath_lengths = 0
        # walk through dirs and get file paths, file sizes and add lengths of file paths
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_filepath_lengths += len(filepath)
                fil = File(filepath, 0, os.path.getsize(filepath), 0)
                self.files.append(fil)

        # start building file
        byte_buffer = self.magic
        byte_buffer += struct.pack("<H", self.version)
        byte_buffer += struct.pack("<I", len(self.files))
        byte_buffer += struct.pack("<I", self.unknown)
        
        # calculate first file offset based on header size
        offset = len(byte_buffer) + total_filepath_lengths + 13*len(self.files)
        print total_filepath_lengths, hex(offset)

        for fil in self.files:
            fil.offset = offset
            offset += fil.size
            print fil.path, hex(fil.offset)
            byte_buffer += struct.pack("<B%isIII" % len(fil.path), len(fil.path), fil.path, fil.size, fil.unk, fil.offset)

        with open(output_file, "wb") as f_out:
            f_out.write(byte_buffer)
            for fil in self.files:
                with open(fil.path, "rb") as f_in:
                    f_out.write(f_in.read())
                        
        
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool that can unpack/pack 9th Company .pak file.')

    parser.add_argument('file', nargs='?', help='Data file')
    parser.add_argument('directory', nargs='?', help='Data directory')
    parser.add_argument('--no-deflate', default=False, action='store_true', help='Don\'t deflate files when unpacking')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print verbose info')
    parser.add_argument('-i', '--info', default=False, action='store_true', help='Print verbose info without unpacking the files')    
    
    args = parser.parse_args()
    filename = args.file
    directory = args.directory
    deflate = not args.no_deflate
    verbose = args.verbose
    info = args.info

    if info:
        verbose = True
        
    if filename != None and directory == None:
        filepath = os.path.abspath(filename)
        sma = SMA()
        sma.unpack(filepath, info, deflate, verbose)
    if filename != None and directory != None:
        sma = SMA()
        sma.pack(directory, filename)
        
        
