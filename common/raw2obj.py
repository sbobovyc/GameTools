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

import argparse
import sys
import struct
import os
import ast
import pandas as pd
import numpy as np

VERTEX_FORMAT = "v %f %f %f"
INDEX_FORMAT = "f %i %i %i"
INDEX_FORMAT2 = "f %i/%i %i/%i %i/%i"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tool that\'s used to read raw data dumps or html tables of vertex data and print wavefront obj vertices.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', nargs='?', help='Raw file')
    parser.add_argument('--type', required=True, choices=['indices', 'positions', 'texcoords'])
    parser.add_argument('--input-type', choices=['bin', 'csv', 'html'])
    parser.add_argument('--mode', default='TRIANGLES', required=False, choices=['TRIANGLE_STRIP', 'TRIANGLES'], help='Draw elements mode')
    parser.add_argument('--order', default='CCW', choices=['CCW', 'CW'], help='Ordering of front facing faces')
    parser.add_argument('--csv_header',
                        default='{\'vertex_index\':1, \'position_x\':2, \'position_y\':3, \'position_z\':4, \'texcoord_x\':14, \'texcoord_x\':15}',
                        help="CSV column mapping {column_name: column_number")
    parser.add_argument('-o', '--offset', default="0x0", help='Offset into binary file, in hex')
    parser.add_argument('-f', '--format', default="UNSIGNED_SHORT", choices=['UNSIGNED_SHORT', 'UNSIGNED_INT'], help='Format of binary data')
    parser.add_argument('-s', '--stride', type=int, default=0, help='Stride of binary')
    parser.add_argument('-c', '--count', type=int, default=sys.maxsize, help='Number of vertices')

    args = parser.parse_args()
    path = args.file

    if args.input_type is None:
        extension = os.path.splitext(path)[1][1:].strip()
    else:
        extension = args.input_type

    faces = {}
    vertices = {}
    indices = {}
    face = 0

    if extension == "bin":
        offset = int(args.offset, 16)
        count = args.count
        if count != sys.maxsize:
            if args.type == "indices":
                if args.format == 'UNSIGNED_INT':
                    count = args.count * 3 * 4
                else:
                    count = args.count * 3 * 2
            elif args.type == "positions":
                count = args.count * 3 * 4
            elif args.type == "texcoords":
                count = args.count * 2 * 4

        byte_count = 0
        with open(path, 'rb') as f:
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(offset)
            i = 0
            while byte_count < count:
                if args.type == "indices":
                    data_size = 3 * 2   # assume vertex indices are unsigned shorts
                    data_format = 'H'*3
                    if args.format == 'UNSIGNED_INT':  # else unsigned int
                        data_size = 3 * 4
                        data_format = 'I'*3
                    buf = f.read(data_size)
                    if not buf:
                        break
                    idx0, idx1, idx2 = struct.unpack(data_format, buf)
                    faces[i] = [idx0, idx1, idx2]
                    if args.mode == "TRIANGLE_STRIP":
                        if args.order == 'CCW':
                            if i % 2:
                                faces[i] = [idx2, idx1, idx0]
                            else:
                                faces[i] = [idx0, idx1, idx2]
                        else:
                            if i % 2:
                                faces[i] = [idx0, idx1, idx2]
                            else:
                                faces[i] = [idx2, idx1, idx0]

                        f.seek(f.tell() - int(2*(data_size/3)))
                        if f.tell() + 2*(data_size/3) == file_size:
                            break
                    elif args.mode == "TRIANGLES":
                        faces[i] = [idx0, idx1, idx2]
                    byte_count += data_size
                    i += 1
                elif args.type == "positions":
                    buf = f.read(3 * 4)  # assume vertex positions are floats
                    if not buf:
                        break
                    f1, f2, f3 = struct.unpack("fff", buf)
                    print(VERTEX_FORMAT % (f1, f2, f3))
                    byte_count += 3 * 4
                    # apply stride
                    f.seek(f.tell() + args.stride - 3*4)
                elif args.type == 'texcoords':
                    buf = f.read(2 * 4)  # assume texture coordinates are floats
                    if not buf:
                        break
                    u, v, = struct.unpack("ff", buf)
                    print("vt", u, v)
                    byte_count += 2 * 4
                    # apply stride
                    f.seek(f.tell() + args.stride - 2*4)
            for key, value in faces.items():
                print(INDEX_FORMAT2 % (value[0] + 1, value[0] + 1, value[1] + 1, value[1] + 1, value[2] + 1, value[2] + 1))  # wavefront obj index starts at 1

        print("# number of bytes", byte_count)
    elif extension == "csv":
        df = pd.read_csv(args.file)
        csv_header = ast.literal_eval(args.csv_header)
        if args.mode == "TRIANGLE_STRIP":
            for i, row in df.iterrows():
                if i < 2:
                    pass
                else:
                    idx0 = int(df.iloc[i - 2, csv_header['vertex_index']])
                    idx1 = int(df.iloc[i - 1, csv_header['vertex_index']])
                    idx2 = int(df.iloc[i, csv_header['vertex_index']])

                    x, y, z = df.iloc[i-2, csv_header['position_x']:csv_header['position_z']+1]
                    vertices[idx0] = [x, y, z]
                    x, y, z = df.iloc[i-1, csv_header['position_x']:csv_header['position_z']+1]
                    vertices[idx1] = [x, y, z]
                    x, y, z = df.iloc[i, csv_header['position_x']:csv_header['position_z']+1]
                    vertices[idx2] = [x, y, z]

                    if args.order == 'CCW':
                        if i % 2:
                            faces[f] = [idx2, idx1, idx0]
                            f += 1
                        else:
                            faces[f] = [idx0, idx1, idx2]
                            f += 1
                    else:
                        if i % 2:
                            faces[f] = [idx0, idx1, idx2]
                            f += 1
                        else:
                            faces[f] = [idx2, idx1, idx0]
                            f += 1
        elif args.mode == "TRIANGLES":
            for i in range(0, df.shape[0], 3):
                idx0 = int(df.iloc[i, csv_header['vertex_index']])
                x, y, z = df.iloc[i, csv_header['position_x']:csv_header['position_z']+1]
                vertices[idx0] = [x,y,z]
                i += 1
                idx1 = int(df.iloc[i, csv_header['vertex_index']])
                x, y, z = df.iloc[i, csv_header['position_x']:csv_header['position_z']+1]
                vertices[idx1] = [x, y, z]
                i += 1
                idx2 = int(df.iloc[i, csv_header['vertex_index']])
                x, y, z = df.iloc[i, csv_header['position_x']:csv_header['position_z']+1]
                vertices[idx2] = [x, y, z]
                faces[f] = [idx0, idx1, idx2]
                f += 1
        for key, value in faces.items():
            print(INDEX_FORMAT % (value[0]+1, value[1]+1, value[2]+1))  # wavefront obj index starts at 1
        for key, value in vertices.items():
            print(VERTEX_FORMAT % (value[0], value[1], value[2]))
    elif extension == "html":
        df = pd.read_html(path, header=None)[0]
        print("#", df.shape)
        if args.type == "indices":
            if args.mode == "TRIANGLE_STRIP":
                for i, row in df.iterrows():
                    if i < 2:
                        pass
                    else:
                        v0,v1,v2 = (df[1][i-2]+1, df[1][i-1]+1, df[1][i]+1)
                        if v0 == v1 or v1 == v2 or v0 == v2:
                            pass
                        if i % 2:
                            print("f %i %i %i" % (v2,v1,v0))
                        else:
                            print("f %i %i %i" % (v0,v1,v2))
            elif args.mode == "TRIANGLES":
                for i in range(0, df.shape[0], 3):
                    v0,v1,v2 = (df[1][i]+1, df[1][i+1]+1, df[1][i+2]+1)
                    print("f %i %i %i" % (v0,v1,v2))
        elif args.type == "positions":            
            for i, row in df.iterrows():
                print("v %f %f %f" % (row[1], row[2], row[3]))
