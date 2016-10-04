from __future__ import print_function

"""@package mdr_mutator
Documentation for this module. 
More details.
"""

"""
Copyright (C) 2015 Stanislav Bobovych
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

        VIpattern = re.compile('f (\d+)/(\d+) (\d+)/(\d+) (\d+)/(\d+)')
        VTpattern = re.compile('vt (\d+.\d+) (\d+.\d+)')        
        Vpattern = re.compile('v ([-]?\d+.\d+) ([-]?\d+.\d+) ([-]?\d+.\d+)')        
        with open(path, "rb") as f:
            lines = f.readlines()
            for line in lines:
                match = VIpattern.match(line)
                if match != None:
                    self.index_array.append( [int(match.group(1))-1, int(match.group(3))-1, int(match.group(5))-1] )
                match = VTpattern.match(line)
                if match != None:
                    self.uv_array.append( [float(match.group(1)), float(match.group(2))] )
                match = Vpattern.match(line)
                if match != None:
                    self.vertex_array.append( [float(match.group(1)), float(match.group(2)), float(match.group(3))] )
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool for mutating mdr files.')
    parser.add_argument('file', nargs='?', help='Input manifest json file')
    parser.add_argument('--scale', '-s', default=1.0, help='Scaling factor')
    parser.add_argument('-o', '--outdir', default=os.getcwd(), help='Output path')
    args = parser.parse_args()
    scale = float(args.scale)

    print(args)
    if args.file is None:
        print("Error, supply a file as parameter")
        sys.exit()
    
    with open(args.file, "rb") as f:
        obj = json.loads(f.read())
        name = obj[0]
        print("Name", name)
    with open(os.path.join(os.path.dirname(args.file), name + ".mdr"), "rb") as f_mdr_orig:
        bindata = f_mdr_orig.read()
    with open(os.path.join(args.outdir, name+".mdr"), "wb") as f_mdr:
        f_mdr.write(bindata)  # copy file
        for sub_module in obj[1]:
            obj_name = "%s_%s.obj" % (sub_module[u'model'], sub_module[u'sub_model'])
            print(obj_name)
            obj = SimpleOBJ(os.path.join(os.path.dirname(args.file), obj_name))
            
            f_mdr.seek(sub_module[u'vertex_index_offset'])
            print("Writing vert index at", hex(f_mdr.tell()))
            for vi in obj.index_array:
                new_vi = struct.pack("<HHH", *vi)
                f_mdr.write(new_vi)
            print("End vert index at", hex(f_mdr.tell()))

            f_mdr.seek(sub_module[u'uv_offset'])
            print("Writing uv at", hex(f_mdr.tell()))
            for uv in obj.uv_array:
                new_uv = struct.pack("ff", *uv)
                f_mdr.write(new_uv)
            print("End uv at", hex(f_mdr.tell()))

            f_mdr.seek(sub_module[u'vertex_offset'])
            print("Writing verts at", hex(f_mdr.tell()))
            for vert in obj.vertex_array:
                new_vertex = struct.pack("fff", scale*vert[0], scale*vert[1], scale*vert[2])
                f_mdr.write(new_vertex)
            print("End vert at", hex(f_mdr.tell()))

            if u'material' in sub_module.keys():
                for mat in sub_module[u'material']:
                    f_mdr.seek(mat[0][u'offset'])
                    bindata = struct.pack("ff", *mat[1][u'unknown_constants'])
                    f_mdr.write(bindata)
                    bindata = struct.pack("fff", *mat[1][u'ambient_color'])
                    f_mdr.write(bindata)
                    bindata = struct.pack("fff", *mat[1][u'diffuse_color'])
                    f_mdr.write(bindata)
                    bindata = struct.pack("fff", *mat[1][u'specular_color'])
                    f_mdr.write(bindata)
                    bindata = struct.pack("f", mat[1][u'specular_exponent'])
                    f_mdr.write(bindata)
                    # for row in mat[1]:
                    #     packed_row = struct.pack("fff", *row[:-1])
                    #     f_mdr.write(packed_row)
