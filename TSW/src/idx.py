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

import os
import sys
import struct

class IDX_bundle_entry:
    def __init__(self):
        self.RDB_type = None
        self.RDB_id = None

    def unpack(self, file_pointer, verbose=False):
        #print hex(file_pointer.tell())
        self.RDB_type, self.RDB_id = struct.unpack("<II", file_pointer.read(8))
        if verbose:
            print "\tRDB Type: %i RDB ID: %i" % (self.RDB_type, self.RDB_id)
        
class IDX_bundle_data:
    def __init__(self):
        self.name_length = None
        self.name = None
        self.num_entries = None
        self.bundle_entries = []

    def unpack(self, file_pointer, verbose=False):
        self.name_length, = struct.unpack("<I", file_pointer.read(4))
        self.name = file_pointer.read(self.name_length)    
        self.num_entries, = struct.unpack("<I", file_pointer.read(4))
        self.num_entries /= 256
        
        if verbose:
            print "Bundle name:",  self.name, "Entry count: ", self.num_entries
        for entry in range(0, self.num_entries):
            self.bundle_entries.append(IDX_bundle_entry().unpack(file_pointer, verbose))        
            
class IDX_bundles:
    def __init__(self):
        self.num_bundles = None
        self.bundle_data = []

    def unpack(self, file_pointer, verbose=False):
        self.num_bundles, = struct.unpack("<I", file_pointer.read(4))
        if verbose:
            print "Number of bundles", self.num_bundles
        for bundle in range(0, self.num_bundles):
            self.bundle_data.append(IDX_bundle_data().unpack(file_pointer, verbose))
            file_pointer.read(1)
            
class IDX_entry_details:
    def __init__(self):
        self.RDB_file_number = None
        self.unknown1 = None #Flags?
        self.unknown2 = None #????
        self.unknown3 = None #????
        self.rdbdata_offset = None
        self.entry_length = None
        self.md5hash = None

    def unpack(self, file_pointer, verbose=False):
        self.RDB_file_number, self.unknown1, self.unknown2, self.unknown3 = struct.unpack("BBBB", file_pointer.read(4))
        self.rdbdata_offset, = struct.unpack("<I", file_pointer.read(4))
        self.entry_length, = struct.unpack("<I", file_pointer.read(4))
        # unpack md5 hash
        self.md5hash, = struct.unpack("!Q", file_pointer.read(8))
        self.md5hash = self.md5hash << 64
        md5hash_lower, = struct.unpack("!Q", file_pointer.read(8))
        self.md5hash |= md5hash_lower

        if verbose:
            print "\tRDB file number: %i" % (self.RDB_file_number)
            print "\tFlags???: 0x%x" % (self.unknown1)
            print "\tUnknown: 0x%x" % (self.unknown2)
            print "\tUnknown: 0x%x" % (self.unknown3)
            print "\tOffset in rdbdata file: 0x%x" % (self.rdbdata_offset)
            print "\tLength of entry data: %i" % (self.entry_length)
            print "\tMD5:", str(hex(self.md5hash)).strip('L')

        return self
        
class IDX_index:
    def __init__(self):
        self.RDB_type = None
        self.RDB_id = None

    def unpack(self, file_pointer, verbose=False):
        self.RDB_type, self.RDB_id = struct.unpack("<II", file_pointer.read(8))
        if verbose:
            print "\tRDB Type: %i RDB ID: %i" % (self.RDB_type, self.RDB_id)
        return self
            
class IDX_index_header:
    def __init__(self):
        self.magic = None       # IBDR
        self.version = None     # 0x07
        self.md5hash = None
        self.num_indeces = None

    def unpack(self, file_pointer, dest_filepath, verbose=False):
        self.magic, = struct.unpack("4s", file_pointer.read(4))
        self.version, = struct.unpack("<I", file_pointer.read(4))
        # unpack md5 hash
        self.md5hash, = struct.unpack("!Q", file_pointer.read(8))
        self.md5hash = self.md5hash << 64
        md5hash_lower, = struct.unpack("!Q", file_pointer.read(8))
        self.md5hash |= md5hash_lower
        self.num_indeces, = struct.unpack("<I", file_pointer.read(4))

        if verbose:
            print "Magic: ", self.magic
            print "Version: ", self.version
            print "MD5 of index data: ", str(hex(self.md5hash)).strip('L')
            print "Number of indeces: ", self.num_indeces
        
class IDX_index_file:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.header = None
        self.indeces = []
        self.entry_details = []
        self.bundles = None
        
        if self.filepath != None:
            self.open(filepath)

    def open(self, filepath=None):
        if filepath == None and self.filepath == None:
            print "File path is empty"
            return
        if self.filepath == None:
            self.filepath = filepath    
        
    def dump(self, dest_filepath=os.getcwd(), verbose=False):
        with open(self.filepath, "rb") as f:
            self.header = IDX_index_header()
            self.header.unpack(f, dest_filepath, verbose)
            for index in range(0, self.header.num_indeces):
                if verbose:
                    print "\tIndex: ", index
                self.indeces.append(IDX_index().unpack(f, verbose))
            for index in range(0, self.header.num_indeces):
                if verbose:
                    print "Index: ", index
                self.entry_details.append(IDX_entry_details().unpack(f, verbose))
            self.bundles = IDX_bundles().unpack(f, verbose)

    def get_indeces(self, RDB_type):
        id2index = {}
        for i in range(0, self.header.num_indeces):
            if self.indeces[i].RDB_type == RDB_type:
                id2index[self.indeces[i].RDB_id] = i
        return id2index

    def get_entry_details(self, index):
        entry_detail = self.entry_details[index]
        filename = "%02i.rdbdata" % (entry_detail.RDB_file_number)
        return (filename, entry_detail.rdbdata_offset, entry_detail.entry_length)


if __name__ == "__main__":
    filepath = sys.argv[1]
    idx = IDX_index_file(filepath)
    idx.dump(verbose=True)
