import os
import sys
import struct

class entry:
    def __init__(self):
        self.RDB_id = None
        self.filename_length = None
        self.filename = None

    def unpack(self, file_pointer, verbose=False):
        self.RDB_id, self.filename_length = struct.unpack("<II", file_pointer.read(8))
        self.filename = file_pointer.read(self.filename_length).strip('\0')
        if verbose:
            print "\tRDB id: %i, File name: %s" % (self.RDB_id, str(self.filename).strip('\0'))
            pass
        return self

class types:
    def __init__(self):
        self.RDB_type = None
        self.num_entries = None
        self.filename_entries = []

    def unpack(self, file_pointer, verbose=False):
        self.RDB_type, self.num_entries = struct.unpack("<II", file_pointer.read(8))
        if verbose:
            print "RDB type: %i, Num entries: %i" % (self.RDB_type, self.num_entries)
        for i in range(0, self.num_entries):
            self.filename_entries.append(entry().unpack(file_pointer, verbose))
        return self
                                        
class mapping:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.RDB_type = None
        self.RDB_id = None
        self.unknown = None
        self.num_types = None
        self.types = []
    
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
            self.RDB_type, self.RDB_id, self.unknown = struct.unpack("<III", f.read(12))
            self.num_types, = struct.unpack("<I", f.read(4))
            if verbose:
                print "RDB type", self.RDB_type
                print "RDB id", self.RDB_id
                print "Num types", self.num_types
            for tp in range(0, self.num_types):
                self.types.append(types().unpack(f, verbose))
                
if __name__ == "__main__":
    filepath = sys.argv[1]
    fm = mapping(filepath)
    fm.dump(verbose=True)
