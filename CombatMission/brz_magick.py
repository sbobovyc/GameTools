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
from __future__ import division
import argparse
import struct
import os
import errno
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO


def update_progress(progress):
    sys.stdout.write('\r[{bar: <10}] {percent}%'.format(bar='#'*int(progress*10), percent=int(progress*100)))
    sys.stdout.flush()


class BrzFile:
    def __init__(self, path):
        self.path = path
        self.file_count = 0
        self.brz_file_list = []
        
    def unpack(self, outdir, verbose=False):
        with open(self.path, "rb") as f:
            u1,count = struct.unpack("<II", f.read(8))
            # print("Unknown int: ", u1)
            print("File count: %i" % count)
            for i in range(0,count):
                offset, = struct.unpack("<I", f.read(4))
                name_len, = struct.unpack("<H", f.read(2))
                file_name, = struct.unpack("%is" % name_len, f.read(name_len))        
                dir_len, = struct.unpack("<H", f.read(2))
                dir_name, = struct.unpack("%is" % dir_len, f.read(dir_len))
                entry = BrzFileEntry(file_name, dir_name, offset)
                if verbose:
                    print(entry)
                self.brz_file_list.append(entry)     
            for i in range(0, count):
                directory = os.path.join(outdir, self.brz_file_list[i].dir.decode("ascii"))
                directory = directory.replace('\\', '/')
                try: 
                    os.makedirs(directory)
                except OSError as err:
                    # Reraise the error unless it's about an already existing directory 
                    if err.errno != errno.EEXIST or not os.path.isdir(directory): 
                        raise
                new_file = os.path.join(outdir, self.brz_file_list[i].dir.decode("ascii"), self.brz_file_list[i].name.decode("ascii"))
                new_file = new_file.replace('\\', '/')
                with open(new_file, "wb") as f_new:
                    f.seek(self.brz_file_list[i].offset)
                    if i != count-1:
                        file_length = self.brz_file_list[i+1].offset - self.brz_file_list[i].offset
                        f_new.write(f.read(file_length))
                    else:
                        f_new.write(f.read())
                update_progress(i/count)
                        
    def pack(self, directory, verbose=False):
        # walk through dirs and get file paths, file sizes and add lengths of file paths
        if sys.version_info <= (3,0):
            buf = StringIO()
        else:
            buf = BytesIO()
        with open(self.path, "wb") as f:
            f.write(struct.pack("II", 0,0))
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    rel_dir_path = os.path.relpath(dirpath, os.path.dirname(directory))
                    entry = BrzFileEntry(filename, rel_dir_path, 0, os.path.getsize(os.path.join(dirpath, filename)))
                    print(entry)
                    self.brz_file_list.append(entry)
            f.seek(4)
            f.write(struct.pack("<I", len(self.brz_file_list)))
            offset = f.tell()
            for entry in self.brz_file_list:
                offset += len(struct.pack("<IH%isH%is" % (len(entry.name), len(entry.dir)), entry.offset, len(entry.name), entry.name.encode("ascii"), len(entry.dir), entry.dir.encode("ascii")))
                with open(os.path.join(os.path.dirname(directory), entry.dir, entry.name), "rb") as ef:
                    buf.write(ef.read())
            for entry in self.brz_file_list:                
                f.write(struct.pack("<IH%isH%is" % (len(entry.name), len(entry.dir)), offset, len(entry.name), entry.name.encode("ascii"), len(entry.dir), entry.dir.encode("ascii")))
                offset += entry.file_size
            f.write(buf.getvalue())
            
            
class BrzFileEntry(object):
    def __init__(self, name, path, offset, size=0):
        self.name = name
        self.dir = path
        self.offset = offset
        self.file_size = size
        
    def __str__(self):
        return "%s, %s, 0x%x, %i" % (self.dir, self.name, self.offset, self.file_size)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool that can unpack/pack Combat Mission brz files.',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filepath', nargs='?', help='BRZ file or directory')
    parser.add_argument('-x', '--extract', default=False, action='store_true', help="Unpack brz file")
    parser.add_argument('-c', '--compress', default=False, action='store_true', help="Pack files into brz")
    parser.add_argument('-o', '--outdir', default=os.getcwd(), help='Output directory')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print info as files are unpacked')
    args = parser.parse_args()
    
    filepath = args.filepath
    outdir = args.outdir
    if args.extract and not args.compress:
        BrzFile(filepath).unpack(outdir, args.verbose)
    elif args.compress and not args.extract:
        indir = os.path.split(filepath)[1]
        outfile = indir + ".brz"
        BrzFile(outfile).pack(filepath)
    else:
        print("Unknown command")
        parser.print_help()
