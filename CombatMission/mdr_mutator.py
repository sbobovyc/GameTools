from __future__ import print_function

"""@package mdr_mutator
Documentation for this module. 
More details.
"""

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
import struct
import os
import sys
import argparse
import json
import re


class SimpleOBJ:

    def __init__(self, path):
        self.index_array = []
        self.uv_array = []
        self.vertex_array = []

        pattern = re.compile('vt (\d+.\d+) (\d+.\d+)')
        with open(path, "rb") as f:
            lines = f.readlines()
            for line in lines:
                match = pattern.match(line)
                if match != None:
                    self.uv_array.append([float(match.group(1)), float(match.group(2))])
            
            
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool for mutating mdr files.')
    parser.add_argument('file', nargs='?', help='Input file')
    args = parser.parse_args()
    
    if args.file == None:
        print("Error, supply a file as parameter")
        sys.exit()

    with open(args.file, "rb") as f:
        obj = json.loads(f.read())
        name = obj[0]
        print("Name", name)
    with open(name+".mdr", "r+b") as f_mdr:
        for sub_module in obj[1]:
            obj_name = "%s_%s.obj" % (sub_module[u'model'], sub_module[u'sub_model'])
            print(obj_name)
            obj = SimpleOBJ(obj_name)
            f_mdr.seek(sub_module[u'uv_offset'])
            print(f_mdr.tell())
            for uv in obj.uv_array:
                new_uv = struct.pack("ff", *uv)
                f_mdr.write(new_uv)
