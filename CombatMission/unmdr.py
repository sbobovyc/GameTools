from __future__ import print_function

"""@package unmdr
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
import numpy as np


########
# object:
# face indices
# UVs,
# then,
# vertices (in object space?)
####

class MDR_Object:
    """MDR object
    """
    def __init__(self, name):
        """The constructor takes a model name as parameter. All other variables are set
        directly.
        """
        self.name = name
        self.index_array = []   # [ (i,i,i) ...]
        self.uv_array = []      # [ (f,f) ...]        
        self.vertex_array = []  # [ (f,f,f) ...]        
        self.texture_name = ""
        #TODO add meta data objects

    def make_wavefront_obj(self):
        """ Serialize mdr to obj format and return it as a string."""        
        string = ""
        string += "o %s\n" % self.name
        # write material info
        string += "mtllib %s\n" % self.name
        string += "usemtl Diffuse\n"

        # write vertex info
        for idx in self.index_array:
            string += "f %i/%i %i/%i %i/%i\n" % (idx[0]+1,idx[0]+1,idx[1]+1,idx[1]+1,idx[2]+1,idx[2]+1)
        for uv in self.uv_array:
            string += "vt %s %s\n" % (uv[0], uv[1])            
        for vert in self.vertex_array:
            string += "v %s %s %s\n" % (vert[0], vert[1], vert[2])

        return string

    def make_wavefront_mtl(self):
        """ Create a material definitin file."""
        string = ""
        string += "newmtl Diffuse\n"
        string += "Ka 0.5 0.5 0.5 # gray\n"   # ambient color
        string += "Kd 0.5 0.5 0.5 # gray\n"   # diffuse color
        string += "Ks 0.0 0.0 0.0\n"          # specular color, off
        string += "Ns 0.0\n"                  # specular exponent
        string += "d 1.0\n"                   # transparency        
        string += "illum 1\n"                 # Color on and Ambient on
        string += "map_Kd %s.bmp\n" % self.texture_name
        return string
    

def read4x4Matrix(f):
    matrix = np.zeros((4,4))
    matrix[3][3] = 1            
    for i in range(0, 4):
        for j in range(0, 3):
            value, = struct.unpack("f", f.read(4))
            print( "#",hex(f.tell()),i,value)
            matrix[i][j] = value
    print(matrix)
    print( "#End matrix", hex(f.tell()))


def dump_model(base_name, num_models, f, model_number, outdir, dump = True):
    print("# Start model ##############################################################"    )
    name_length, = struct.unpack("<H", f.read(2))
    #print "name length", name_length
    submodel_name = f.read(name_length)
    print("# submodel name", submodel_name)

    # output files
    obj_fout = None
    mtl_fout = None
    
    # object
    mdr_obj = None

    # logging to ease reversing
    logger = open("logger.txt", 'ab')
    
    if dump:
        obj_fout = open(os.path.join(outdir, "%s_%s.obj" % (base_name, submodel_name)), 'wb')
        mtl_fout = open(os.path.join(outdir, "%s_%s.mtl" % (base_name, submodel_name)), 'wb')
        mdr_obj = MDR_Object("%s_%s" % (base_name, submodel_name))
            
    f.read(1) # always 2?
    for i in range(0, 0xB0/4):
        unk, = struct.unpack("f", f.read(4))
        #print "#",i, unk
    print("# Finished unknown section", hex(f.tell()))


    ###############################################    
    print("# Start face vertex indices")
    face_count, = struct.unpack("<I", f.read(4))
    print("# Face count:", face_count/3)

    for i in range(0, face_count/3):        
        if not dump:
            f.read(6)
        else:
            v0, v1, v2 = struct.unpack("<HHH", f.read(6))
            #print("f %i/%i %i/%i %i/%i" % (v0+1,v0+1,v1+1,v1+1,v2+1,v2+1))
            mdr_obj.index_array.append((v0,v1,v2))
    print("# Finished face vertex indices", hex(f.tell()))
    ###############################################

    ###############################################
    print("# Start UVs")
    uv_in_section, = struct.unpack("<I", f.read(4))
    print("# UV in section:", uv_in_section)
        
    for i in range(0, uv_in_section/2):
        if not dump:
            f.read(8)
        else:
            u,v = struct.unpack("<ff", f.read(8))        
            #print("vt", u,v)
            mdr_obj.uv_array.append((u,v))                    
    print("# Finish UV section:", hex(f.tell()))
    ###############################################    

    print("# Start unknown section 1"   )
    unk, = struct.unpack("<I", f.read(4))
    print("# Unknown",unk)

    if model_number == 0:
        print("#Some matrix?")
        for i in range(0, 0x30/4):
            print("#",i,struct.unpack("ff", f.read(8)))
        
        print("# End unknown section", hex(f.tell()))

        print("# read 4 bytes, 0?", struct.unpack("<I", f.read(4))) # 0
        #TODO object_type is probably really count for some metadata
        object_type, = struct.unpack("<I", f.read(4)) # can be 0,1 or 2    
        print( "# read 4 bytes, object type?: ", object_type)

        if object_type == 0:
            print( "# Object type 1, reading some metadata of size 0x68")
            #print("%s, type 0, model_number=%i out of %i, %s" % (base_name, model_number, num_models, hex(f.tell())), file=logger)
            length, = struct.unpack("<H", f.read(2))
            read4x4Matrix(f)         
            length, = struct.unpack("<H", f.read(2))
            read4x4Matrix(f)            
            print("Unknown float", struct.unpack("f", f.read(4)))
            print("# end object type 0", hex(f.tell()))    
        elif object_type == 1:
            # This type seems to occur only in the first model.
            print( "# Object type 1, reading some metadata")
            length, = struct.unpack("<H", f.read(2))
            name = f.read(length) #TODO this is same as meta2 tags
            print( "# meta data name", name)
            #print("%s, type 1, model_number=%i out of %i, name=%s, %s" % (base_name, model_number, num_models, name, hex(f.tell())), file=logger)
            read4x4Matrix(f)         
            length, = struct.unpack("<H", f.read(2))
            read4x4Matrix(f)
            length, = struct.unpack("<H", f.read(2))
            read4x4Matrix(f)
            print("Unknown float", struct.unpack("f", f.read(4)))
            print("# end object type 1", hex(f.tell()))            
        elif object_type == 2:
            print( "# Object type 2")
            name_length, = struct.unpack("<H", f.read(2))
            model_class = f.read(name_length) #TODO this is same as meta2 tags
            #print("%s, type 2, model_number=%i out of %i, name=%s, %s" % (base_name, model_number, num_models, model_class, hex(f.tell())), file=logger)
            print( "#Some matrix?", model_class)
            read4x4Matrix(f)                            
            name_length, = struct.unpack("<H", f.read(2))
            model_class = f.read(name_length)
            print( "#Some matrix?", model_class)
            read4x4Matrix(f)
            
            print( "#Start some unknown")
            for i in range(0, 26):
                print( "#",i,struct.unpack("f", f.read(4)))
            print( "#End unknown", hex(f.tell()))        
        elif object_type == 14:
            print("# Is this a vehicle? Treat as error.")
            for i in range(0, 14):
                length, = struct.unpack("<H", f.read(2))
                print(f.read(length))
                read4x4Matrix(f)            
            f.read(2) # length, size?
            f.read(0x68)
            print("#End unknown", hex(f.tell()))
            sys.exit(0)
    else:
        length, = struct.unpack("<xxH", f.read(4))
        unknown_meta = f.read(length)
        print( "# unknown meta2", unknown_meta)
        if unknown_meta == "weapon" or \
           unknown_meta == "tripod" or \
           unknown_meta == "base" or \
           unknown_meta == "base2" or \
           unknown_meta == "base3" or \
           unknown_meta == "base3" or \
           unknown_meta == "clip" or \
           unknown_meta == "missile" or \
           unknown_meta == "grenade" or \
           unknown_meta == "day sight" or \
           unknown_meta == "m203" or \
           unknown_meta == "m320" or \
           unknown_meta == "day" or \
           unknown_meta == "cylinder01" or \
           unknown_meta == "ammo" or \
           unknown_meta == "bogus-weapon":
            print("Reading", unknown_meta)
            f.read(0x60)
            count, = struct.unpack("<I", f.read(4))
            print("# Count", count)
            if count == 0:
                f.read(0x68)
            else:
                for i in range(0, count):
                    length, = struct.unpack("<H", f.read(2))
                    unknown_meta2 = f.read(length)
                    print("Sub-meta", unknown_meta2)
                    if unknown_meta2 == "eject" or \
                       unknown_meta2 == "link" or \
                       unknown_meta2 == "muzzle":
                        f.read(0x30)
                        print("#End of sub-meta", hex(f.tell()))
                    elif length == 0:
                        print("#End of sub-meta", hex(f.tell()))
                    else:                        
                        f.read(0x30)
                        print("#Possible error! Report about it on the forum.")
                        sys.exit(0)                        
                        print("#End of sub-meta", hex(f.tell()))
                if unknown_meta == "weapon" or unknown_meta == "base2" or unknown_meta == "base3" or unknown_meta == "tripod":
                    f.read(0x68)
                else:
                    f.read(0x30)
                    print("#Possible error!")
                    sys.exit(0)
        else:
            f.read(0xCC)
            print("#Possible error! Report about it on the forum.")
            sys.exit(0)
        print( "# unknown meta finished", hex(f.tell()))        
        
    f.read(4) # 0
    name_length, = struct.unpack("<H", f.read(2))
    texture_name = f.read(name_length)
    print( "#Texture name", texture_name)
    if dump:
        mdr_obj.texture_name = texture_name

    f.read(1) # always 2?
    for i in range(0, 0xB0/4):
        unk, = struct.unpack("f", f.read(4))
        #print( unk)
    print( "#Finished unknown section", hex(f.tell()))

    ###############################################
    print( "#Start vertices")
    vertex_floats, = struct.unpack("<I", f.read(4))
    print( "#Vertices", vertex_floats/3)
    for i in range(0, vertex_floats/3):
        if not dump:
            f.read(12)
        else:
            x,y,z = struct.unpack("fff", f.read(12))
            #print( "v",x,y,z)
            mdr_obj.vertex_array.append((x,y,z))
    print( "#End vertices", hex(f.tell()))
    ###############################################
    
    print( "#Start unknown")
    count, = struct.unpack("<I", f.read(4))
    print( "# Unknown count", count)
    for i in range(0, count):
        unk, = struct.unpack("<H", f.read(2))
        #print( "#",i, unk)
    print( "#End unknown", hex(f.tell()))
    print( "# End model ##############################################################")
    f.read(4) # 0
    f.read(1)

    if dump: 
        print(mdr_obj.make_wavefront_obj(), file=obj_fout)
        print(mdr_obj.make_wavefront_mtl(), file=mtl_fout)
        obj_fout.close()
    logger.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool for experimenting with mdr files.')
    parser.add_argument('-p', '--parse-only', default=False, action='store_true', help='Only parse file, do not dump models')
    parser.add_argument('-o', '--outdir', default=os.getcwd(), help='Output path')
    parser.add_argument('file', nargs='?', help='Input file')
    args = parser.parse_args()

    filepath = None
    if args.file == None:
        print("Error, supply a file as parameter")
        sys.exit()
        #filepath = "simple\\ak-74-lod-2.mdr"    # type 2, 3 models
        #filepath = "simple\\ak-74.mdr"         # type 2, 3 models
        #filepath = "simple\\binoculars.mdr"    # type 0, 1 model
        #filepath = "simple\\rdg-2.mdr"          # type 0, 1 model
        #filepath ="simple\\grenade-anm8.mdr",   # type 0, 
        #filepath = r"simple\mines sign.mdr"    # type 0
        #filepath = "simple\\rpg-22-lod-3.mdr"  # type 0
        #filepath = "simple\\grenade-missile.mdr"# type 1, 
        #filepath = "simple\\at-3-missile.mdr"   # type 1, 
        #filepath = "simple\\rpo-m-atgm.mdr"   # type 1,
        #fileapath = "simple\\akms.mdr"          # type 2, 3 models, shockforce

        #filepath = "simple\\makarov.mdr"       # type 2, 2 models
        #filepath = "berettam9.mdr"              # type 2, 2 models
    else:
        filepath = args.file
    
    print( "#",filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    with open(filepath, "rb") as f:
        num_models, = struct.unpack("<Ix", f.read(5))
        print( "# number of models", num_models)
        for i in range(0, num_models):
            dump_model(base_name, num_models, f, i, args.outdir, not args.parse_only)

