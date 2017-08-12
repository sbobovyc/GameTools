"""
Copyright (C) 2017 Stanislav Bobovych
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
import zlib
import os
import errno

CIPHER_KEY = 0xF69DA025


class AZP_Data:
    def __init__(self, name, offset, uncompressed_size, compressed_size):
        self.name = name
        self.offset = offset
        self.uncompressed_size = uncompressed_size
        self.compressed_size = compressed_size
        self.compressed_data = None


def symmetric_cipher(input_data, length, key):
    output_data = bytearray(length)

    # xor eax,eax
    # xor edx,edx
    eax = 0
    edx = 0
    # pop dx
    edx = 0x0000FFFF & key
    eax = 0x0000FFFF & (key >> 16)
    for i in range(0, length):
        # print(hex(edx), hex(eax))
        # mul dx
        temp = eax * edx
        eax = 0x0000FFFF & temp
        edx = 0x0000FFFF & (temp >> 16)
        # print(hex(eax), hex(edx))
        # dec ax
        eax -= 1
        # print(hex(eax))
        # xor eax,edx
        eax = eax ^ edx
        # print(hex(eax))
        # mov edx,FF
        edx = 0xFF
        # and edx,eax
        edx = edx & eax
        # print(hex(edx))
        # mov al,byte ptr ds:[edi]
        # print("ciph", ciphered_data)
        eax = (eax & 0x0000FF00) | input_data[i]
        # print(hex(eax))
        # xor edx,eax
        edx = edx ^ eax
        # print(hex(edx))
        # mov byte ptr ds:[edi],dl ; save clear data
        output_data[i] = edx & 0x000000FF
        # print("++++++++++++++")
    # shl eax,10
    eax = eax << 0x10
    # print(hex(eax))
    # or ax,dx
    eax = eax | edx
    # print(hex(eax))
    next_key = eax
    return output_data, next_key


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tool that can unpack 7.62 High Calibre and Man of Prey(Marauder) AZP files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filepath', nargs='?', help='AZP file')
    parser.add_argument('-e', '--extract', default=False, action='store_true', help="Unpack azp file")
    parser.add_argument('-l', '--list', default=False, action='store_true', help="List files in archive")
    parser.add_argument('-p', '--pack', default=False, action='store_true', help="Pack files into azp")
    parser.add_argument('-o', '--outdir', default=os.getcwd(), help='Output directory')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print info as files are unpacked')

    args = parser.parse_args()

    if args.list or args.extract:
        with open(args.filepath, "rb") as f:
            # read header
            header, ver = struct.unpack("3sb", f.read(4))
            print(header, ver)
            data_offset, game_version = struct.unpack("II", f.read(8))
            print("Data offset:", hex(data_offset))
            print("Game version:", game_version)
            num_files, = struct.unpack("I", f.read(4))
            print("Number of files:", num_files)

            next_key = CIPHER_KEY
            header = []

            # read table of contents
            for i in range(0, num_files):
                ciphered_data = f.read(4)
                clear_data, next_key = symmetric_cipher(ciphered_data, 4, next_key)
                filename_length, = struct.unpack("I", clear_data)
                if args.verbose:
                    print("File name length:", filename_length)

                ciphered_data = f.read(filename_length)
                clear_data, next_key = symmetric_cipher(ciphered_data, filename_length, next_key)
                filename = clear_data.decode("ascii")
                if args.verbose:
                    print("File name:", filename)

                ciphered_data = f.read(4)
                clear_data, next_key = symmetric_cipher(ciphered_data, 4, next_key)
                data_offset, = struct.unpack("I", clear_data)
                if args.verbose:
                    print("Data offset:", hex(data_offset))

                ciphered_data = f.read(4)
                clear_data, next_key = symmetric_cipher(ciphered_data, 4, next_key)
                compressed_size, = struct.unpack("I", clear_data)
                if args.verbose:
                    print("Compressed size:", compressed_size)

                ciphered_data = f.read(4)
                clear_data, next_key = symmetric_cipher(ciphered_data, 4, next_key)
                uncompressed_size, = struct.unpack("I", clear_data)
                if args.verbose:
                    print("Uncompressed size:", uncompressed_size)

                header.append(AZP_Data(filename, data_offset, uncompressed_size, compressed_size))

            if args.extract:
                for entry in header:
                    f.seek(entry.offset)
                    di = os.path.dirname(entry.name)
                    final_dir = os.path.join(args.outdir, di)

                    try:
                        os.makedirs(final_dir)
                    except OSError as err:
                        # Reraise the error unless it's about an already existing directory
                        if err.errno != errno.EEXIST or not os.path.isdir(final_dir):
                            raise

                    f.seek(entry.offset)
                    data = zlib.decompress(f.read(entry.compressed_size))

                    with open(os.path.join(final_dir, os.path.basename(entry.name)), "wb") as fo:
                        fo.write(data)
    elif args.pack:
        directory = args.filepath
        header = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if root == directory:
                    rel_dir_path = ""
                else:
                    rel_dir_path = os.path.relpath(root, start=directory)
                data = None
                with open(os.path.join(root, filename), "rb") as f:
                    data = f.read()
                entry = AZP_Data(os.path.join(rel_dir_path, filename), 0, os.path.getsize(os.path.join(root, filename)),
                                 0)
                entry.compressed_data = zlib.compress(data)
                entry.compressed_size = len(entry.compressed_data)
                print(entry.name, entry.uncompressed_size, entry.compressed_size)
                header.append(entry)

        # compressed data
        compressed_data = b''

        header_total_size = 0
        for entry in header:
            header_total_size += 4 + len(entry.name) + 4 + 4 + 4

        current_data_offset = 16 + header_total_size

        # create header
        with open(os.path.basename(args.filepath)+".azp", "wb") as f:
            f.write(struct.pack("3sbIII", "AZP".encode("ascii"), 0x1, current_data_offset, 0x6, len(header)))

            # create table of contents
            next_key = CIPHER_KEY
            for entry in header:
                clear_data = struct.pack("I", len(entry.name))
                print(entry.name)
                ciphered_data, next_key = symmetric_cipher(clear_data, len(clear_data), next_key)
                f.write(ciphered_data)

                clear_data = struct.pack("%is" % len(entry.name), entry.name.encode("ascii"))
                ciphered_data, next_key = symmetric_cipher(clear_data, len(clear_data), next_key)
                f.write(ciphered_data)

                clear_data = struct.pack("I", current_data_offset)
                ciphered_data, next_key = symmetric_cipher(clear_data, 4, next_key)
                f.write(ciphered_data)

                clear_data = struct.pack("I", entry.compressed_size)
                ciphered_data, next_key = symmetric_cipher(clear_data, 4, next_key)
                f.write(ciphered_data)

                clear_data = struct.pack("I", entry.uncompressed_size)
                ciphered_data, next_key = symmetric_cipher(clear_data, 4, next_key)
                f.write(ciphered_data)

                current_data_offset += entry.compressed_size
            for entry in header:
                f.write(entry.compressed_data)
    else:
        print("Unknown command")
        parser.print_help()
