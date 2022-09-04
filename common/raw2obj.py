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
import ast
import os
import struct
import sys
import pandas as pd
from enum import Enum


class InputType(Enum):
    bin = 'bin'
    csv = 'csv'
    html = 'html'


class DataType(Enum):
    indices = 'indices'
    positions = 'positions'
    texcoords = 'texcoords'


class DrawElementsMode(Enum):
    TRIANGLE_STRIP = 'TRIANGLE_STRIP'
    TRIANGLES = 'TRIANGLES'


class BinaryFormat(Enum):
    UNSIGNED_SHORT = 'UNSIGNED_SHORT'
    UNSIGNED_INT = 'UNSIGNED_INT'


class FaceOrder(Enum):
    CCW = 'CCW'
    CW = 'CW'


VERTEX_FORMAT = "v %f %f %f"
INDEX_FORMAT = "f %i %i %i"
INDEX_FORMAT2 = "f %i/%i %i/%i %i/%i"
TEXTURE_COORDS = "vt %f %f"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tool that\'s used to read raw data dumps, CSV or HTML tables of vertex data and print Wavefront obj.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', nargs='?', help='Input file')
    parser.add_argument('--type', choices=[DataType.indices.value, DataType.positions.value,
                                           DataType.texcoords.value])
    parser.add_argument('--input-type',
                        choices=[InputType.bin.value, InputType.csv.value, InputType.html.value])
    parser.add_argument('--mode', default=DrawElementsMode.TRIANGLES.value, required=False,
                        choices=[DrawElementsMode.TRIANGLE_STRIP.value,
                                 DrawElementsMode.TRIANGLES.value], help='Draw elements mode')
    parser.add_argument('--order', default=FaceOrder.CCW.value,
                        choices=[FaceOrder.CCW.value, FaceOrder.CW.value],
                        help='Ordering of front facing faces')

    bin_group = parser.add_argument_group("bin options")
    bin_group.add_argument('-o', '--offset', default="0x0", help='Offset into binary file, in hex')
    bin_group.add_argument('-s', '--stride', type=int, default=0, help='Stride of binary')
    bin_group.add_argument('-c', '--count', type=int, default=sys.maxsize,
                           help='Number of vertices')
    bin_group.add_argument('--skip', type=int, default=0, help='Skip n bytes')
    bin_group.add_argument('-f', '--format', default=BinaryFormat.UNSIGNED_SHORT.value,
                           choices=[BinaryFormat.UNSIGNED_SHORT.value,
                                    BinaryFormat.UNSIGNED_INT.value], help='Format of binary data')

    csv_group = parser.add_argument_group("csv options")
    csv_group.add_argument('--csv_header',
                           default='{\'vertex_index\':1, \'position_x\':2, \'position_y\':3, \'position_z\':4, \'texcoord_x\':14, \'texcoord_y\':15}',
                           help="CSV column mapping {\'column_name\': column_number}")

    args = parser.parse_args()
    path = args.file

    if args.input_type is None:
        input_type = InputType[os.path.splitext(path)[1][1:].strip()]
    else:
        input_type = InputType[args.input_type]

    if input_type == InputType.bin or input_type == InputType.html:
        if args.type is not None:
            data_type = DataType[args.type]
        else:
            print("For bin or html, you must supply input data type (--type)")
            sys.exit(-1)

    faces = {}
    vertices = {}
    indices = {}
    texture_coords = {}
    face = 0
    binary_format = BinaryFormat[args.format]
    mode = DrawElementsMode[args.mode]
    face_order = FaceOrder[args.order]

    if input_type == InputType.bin:
        offset = int(args.offset, 16)
        count = args.count
        if count != sys.maxsize:
            if data_type == DataType.indices:
                if binary_format == BinaryFormat.UNSIGNED_INT:
                    count = args.count * 3 * 4
                else:
                    count = args.count * 3 * 2
            elif data_type == DataType.positions:
                count = args.count * 3 * 4
            elif data_type == DataType.texcoords:
                count = args.count * 2 * 4

        byte_count = 0
        with open(path, 'rb') as f:
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(offset)
            i = 0
            while byte_count < count:
                if data_type == DataType.indices:
                    data_size = 3 * 2  # assume vertex indices are unsigned shorts
                    data_format = 'H' * 3
                    if binary_format == BinaryFormat.UNSIGNED_INT:  # else unsigned int
                        data_size = 3 * 4
                        data_format = 'I' * 3
                    buf = f.read(data_size)
                    if not buf:
                        break
                    idx0, idx1, idx2 = struct.unpack(data_format, buf)
                    faces[i] = [idx0, idx1, idx2]
                    if mode == DrawElementsMode.TRIANGLE_STRIP:
                        if face_order == FaceOrder.CCW:
                            if i % 2:
                                faces[i] = [idx2, idx1, idx0]
                            else:
                                faces[i] = [idx0, idx1, idx2]
                        else:
                            if i % 2:
                                faces[i] = [idx0, idx1, idx2]
                            else:
                                faces[i] = [idx2, idx1, idx0]

                        f.seek(f.tell() - int(2 * (data_size / 3)))
                        if f.tell() + 2 * (data_size / 3) == file_size:
                            break
                    elif mode == DrawElementsMode.TRIANGLES:
                        faces[i] = [idx0, idx1, idx2]
                    byte_count += data_size
                    i += 1
                elif data_type == DataType.indicespositions:
                    buf = f.read(3 * 4)  # assume vertex positions are floats
                    if not buf:
                        break
                    f1, f2, f3 = struct.unpack("fff", buf)
                    print(VERTEX_FORMAT % (f1, f2, f3))
                    byte_count += 3 * 4
                    # apply stride
                    f.seek(f.tell() + args.stride - 3 * 4)
                elif data_type == DataType.texcoords:
                    next_read_address = f.tell() + args.stride
                    f.read(args.skip)
                    buf = f.read(2 * 4)  # assume texture coordinates are floats
                    if not buf:
                        break
                    u, v, = struct.unpack("ff", buf)
                    print("vt", u, v)
                    byte_count += 2 * 4
                    f.seek(next_read_address)
            for key, value in faces.items():
                print(INDEX_FORMAT2 % (
                    value[0] + 1, value[0] + 1, value[1] + 1, value[1] + 1, value[2] + 1,
                    value[2] + 1))  # wavefront obj index starts at 1
        print("# number of bytes", byte_count)
    elif input_type == InputType.csv:
        df = pd.read_csv(args.file)
        csv_header = ast.literal_eval(args.csv_header)
        if mode == DrawElementsMode.TRIANGLE_STRIP:
            for i, row in df.iterrows():
                if i < 2:
                    pass
                else:
                    idx0 = int(df.iloc[i - 2, csv_header['vertex_index']])
                    idx1 = int(df.iloc[i - 1, csv_header['vertex_index']])
                    idx2 = int(df.iloc[i, csv_header['vertex_index']])

                    x, y, z = df.iloc[i - 2, csv_header['position_x']:csv_header['position_z'] + 1]
                    vertices[idx0] = [x, y, z]
                    x, y, z = df.iloc[i - 1, csv_header['position_x']:csv_header['position_z'] + 1]
                    vertices[idx1] = [x, y, z]
                    x, y, z = df.iloc[i, csv_header['position_x']:csv_header['position_z'] + 1]
                    vertices[idx2] = [x, y, z]

                    if face_order == FaceOrder.CCW:
                        if i % 2:
                            faces[face] = [idx2, idx1, idx0]
                            face += 1
                        else:
                            faces[face] = [idx0, idx1, idx2]
                            face += 1
                    else:
                        if i % 2:
                            faces[face] = [idx0, idx1, idx2]
                            face += 1
                        else:
                            faces[face] = [idx2, idx1, idx0]
                            face += 1
        elif mode == DrawElementsMode.TRIANGLES:
            for i in range(0, df.shape[0], 3):
                def extract(idx): return (int(df.iloc[idx, csv_header['vertex_index']]),
                                          df.iloc[idx,
                                          csv_header['position_x']:csv_header['position_z'] + 1],
                                          df.iloc[idx, csv_header['texcoord_x']:csv_header['texcoord_y'] + 1] if 'texcoord_x' in csv_header and 'texcoord_y' in csv_header else ())


                idx0, vert0, tex0 = extract(i)
                vertices[idx0] = [*vert0]
                texture_coords[idx0] = [*tex0]
                idx1, vert1, tex1 = extract(i + 1)
                vertices[idx1] = [*vert1]
                texture_coords[idx1] = [*tex1]
                idx2, vert2, tex2 = extract(i + 2)
                vertices[idx2] = [*vert2]
                texture_coords[idx2] = [*tex2]

                faces[face] = [idx0, idx1, idx2]
                face += 1
        if 'texcoord_x' in csv_header and 'texcoord_y' in csv_header:
            for key, value in faces.items():
                print(INDEX_FORMAT2 % (value[0] + 1, value[0] + 1, value[1] + 1, value[1] + 1, value[2] + 1,
                    value[2] + 1))  # wavefront obj index starts at 1
        else:
            for key, value in faces.items():
                print(INDEX_FORMAT % (value[0] + 1, value[1] + 1, value[2] + 1))  # wavefront obj index starts at 1
        for key, value in vertices.items():
            print(VERTEX_FORMAT % (value[0], value[1], value[2]))
        if 'texcoord_x' in csv_header and 'texcoord_y' in csv_header:
            for key, value in texture_coords.items():
                print(TEXTURE_COORDS % (value[0], 1.0 - value[1]))  # TODO allow to take value directly or make the adjustment via command line flag
    elif input_type == InputType.html:
        df = pd.read_html(path, header=None)[0]
        print("#", df.shape)
        if data_type == DataType.indices:
            if mode == DrawElementsMode.TRIANGLE_STRIP:
                for i, row in df.iterrows():
                    if i < 2:
                        pass
                    else:
                        v0, v1, v2 = (df[1][i - 2] + 1, df[1][i - 1] + 1, df[1][i] + 1)
                        if v0 == v1 or v1 == v2 or v0 == v2:
                            pass
                        if i % 2:
                            print("f %i %i %i" % (v2, v1, v0))
                        else:
                            print("f %i %i %i" % (v0, v1, v2))
            elif mode == DrawElementsMode.TRIANGLES:
                for i in range(0, df.shape[0], 3):
                    v0, v1, v2 = (df[1][i] + 1, df[1][i + 1] + 1, df[1][i + 2] + 1)
                    print("f %i %i %i" % (v0, v1, v2))
        elif data_type == DataType.positions:
            for i, row in df.iterrows():
                print("v %f %f %f" % (row[1], row[2], row[3]))
    else:
        print("Not valid input type")
