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

class RDBDATA_data_entry:
    def __init__(self, offset, file_pointer):
        old_offset = file_pointer.tell()
        file_pointer.seek(offset)
        self.data_type, = struct.unpack("<I", file_pointer.read(4))
        self.RDB_id, = = struct.unpack("<I", file_pointer.read(4))
        self.data_length, = struct.unpack("<I", file_pointer.read(4))
        self.unknown, = struct.unpack("<I", file_pointer.read(4))
        self.data = file_pointer.read(self.data_length)
        file_pointer.seek(old_offset)
        
class RDBDATA_file:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.header = None #RDB0
        self.data = None
        
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
            self.header = struct.unpack("IIII", f.read(4))
            self.data = f.read()
