from __future__ import print_function
"""
Created on September 31, 2014
@author: sbobovyc
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

import os
import re
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool that stitches JAF map tiles into one map.')
    parser.add_argument('inputdir', nargs='?', help='Input directory')
    parser.add_argument('outfile', nargs='?', help='Output file')


    args = parser.parse_args()
    inputdir = args.inputdir
    outfile = args.outfile
    
    if inputdir != None:
    
        onlyfiles = [ f for f in os.listdir(inputdir) if os.path.isfile(os.path.join(inputdir,f)) ]


        # filter for map tiles
        pattern = "^[a-z][0-9]*\.png"
        test = re.compile(pattern)
        files = filter(test.search, onlyfiles)

        #print(files)
        max_row = ord(max(files)[0]) - ord('a')
        columns = map(lambda x: int(x[1:].split('.')[0]), files)
        max_column = max(columns)
        print("max col: ", max_column)

        im = Image.open('a1.png')
        width, height = im.size

        new_im = Image.new("RGB", (int(width*(max_column)), int(height*max_row)), None)
        for row in range(0, max_row):
            for column in range(0, max_column+1):
                f = chr(row+ord('a'))+str(column)+'.png'
                if os.path.isfile(f):
                    print(f, ((column-1)*width, row*height))
                    im = Image.open(f)
                    new_im.paste(im, ((column-1)*width, row*height))
        new_im.save(outfile)

    else:
        parser.print_help()
