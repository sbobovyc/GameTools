import struct
import os
import errno
import sys

class brz_file(object):
    def __init__(self, name, path, offset):
        self.name = name
        self.dir = path
        self.offset = offset

filepath = "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission Battle for Normandy DEMO\Data\Normandy Demo v100.brz"            
#filepath = "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission Battle for Normandy DEMO\Data\Normandy Demo v110.brz"
#filepath = "C:\Users\sbobovyc\Documents\Battlefront\Combat Mission Battle for Normandy DEMO\Data\Normandy Demo v110B.brz"

outdir = "out"
brz = []
with open(filepath, "rb") as f:
    u1,count = struct.unpack("<II", f.read(8))
    print u1,count
    for i in range(0,count):
        offset, = struct.unpack("<I", f.read(4))
        name_len, = struct.unpack("<H", f.read(2))
        file_name, = struct.unpack("%is" % name_len, f.read(name_len))        
        dir_len, = struct.unpack("<H", f.read(2))
        dir_name, = struct.unpack("%is" % dir_len, f.read(dir_len))
        #print "offset", hex(offset)
        #print "name", file_name
        #print "dir", dir_name        
        #print
        brz.append(brz_file(file_name, dir_name, offset))
    #print "here", hex(f.tell())
    

    for i in range(0, count):
        directory = os.path.join("out", brz[i].dir)
        try: os.makedirs(directory)
        except OSError, err:
            # Reraise the error unless it's about an already existing directory 
            if err.errno != errno.EEXIST or not os.path.isdir(directory): 
                raise        
        with open(os.path.join("out", brz[i].dir, brz[i].name), "wb") as f_new:
            f.seek(brz[i].offset)
            if i != count-1:
                file_length = brz[i+1].offset - brz[i].offset
                f_new.write(f.read(file_length))
            else:
                f_new.write(f.read())
            
            
