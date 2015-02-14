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

import argparse
import os
import re
from pylab import *
import sys

parser = argparse.ArgumentParser(description='Tool that recursively scans directories and visualizes file sizes.', \
                                epilog='')

parser.add_argument('path', nargs='?', help='Root directory to scan.')
parser.add_argument('--filt', default='', help='Regex expression used to filter out directories or files.')
parser.add_argument('--ext-only', default=False, action='store_true', help='Only do file extension analysis')

args = parser.parse_args()
path = args.path
filt = re.compile(args.filt)

num_files = 0
total_size = 0
file_dict = {}
ext_dict = {}
for root, dir, files in os.walk(path):
    if re.search(filt, root) == None or args.filt == '':
        for f in files:
            if not args.ext_only:
                fpath = os.path.join(root,f)
                num_files += 1
                fsize = os.path.getsize(fpath)
                total_size += fsize
                file_dict[fpath] = fsize

            ext = os.path.splitext(f)[1]
            if ext_dict.has_key(ext):
                ext_dict[ext] = ext_dict[ext] + 1
            else:
                ext_dict[ext] = 1

print ext_dict
if not args.ext_only:    
    files_counts = sorted(file_dict.items(), key=lambda x:x[1], reverse=True)     # list of tuples (path, size)
    paths,sizes = zip(*files_counts)

    # plotting
    labels = map(lambda x: os.path.basename(x), paths)
    figure(1, figsize=(6,6))
    ax = axes([0.1, 0.1, 0.8, 0.8])
    pie(sizes, labels=labels)
    title("Directory: %s, file count: %s, total size(mb): %s" % (path, num_files, total_size/1024))
    show()
