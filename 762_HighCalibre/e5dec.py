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
import os
import sys

from azp import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tool that can decipher/cipher 7.62 High Calibre localized text files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filepath', nargs='?', help='AZP file')

    args = parser.parse_args()
    extension = os.path.splitext(args.filepath)[1][1:].strip()

    if extension == "TXT":
        new_path = args.filepath+".src"
    elif extension == "src":
        new_path = os.path.splitext(args.filepath)[0]
    else:
        print("File not TXT or src")
        sys.exit(0)

    print("Output:", new_path)
    with open(args.filepath, "rb") as f:
        original_data = f.read()
        processed_data, next_key = symmetric_cipher(original_data, len(original_data), CIPHER_KEY)
    with open(new_path, "wb") as f:
        f.write(processed_data)
