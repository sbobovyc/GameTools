from __future__ import print_function

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


########
# perhaps:
# object
# UVs
# face indices
# then,
# object
# vertices (in object space)
####

is_dump = True


        
def dump_model(base_name, f, model_number):    
    print("# Start model ##############################################################"    )
    name_length, = struct.unpack("<H", f.read(2))
    #print "name length", name_length
    submodel_name = f.read(name_length)
    print("# submodel name", submodel_name)

    # output file
    fout = open("%s_%s.obj" % (base_name, submodel_name), 'wb')
    
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
        v0, v1, v2 = struct.unpack("<HHH", f.read(6))
        if is_dump: print("f %i/%i %i/%i %i/%i" % (v0+1,v0+1,v1+1,v1+1,v2+1,v2+1), file=fout)
    print("# Finished face vertex indices", hex(f.tell()))
    ###############################################

    ###############################################
    print("# Start UVs")
    uv_in_section, = struct.unpack("<I", f.read(4))
    print("# UV in section:", uv_in_section)
        
    for i in range(0, uv_in_section/2):     
        u,v = struct.unpack("<ff", f.read(8))        
        if is_dump: print("vt", u,v, file=fout)
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
        object_type, = struct.unpack("<I", f.read(4)) # can be 0,1 or 2    
        print( "# read 4 bytes, object type?: ", object_type)

        if object_type == 1:
            print( "# Object type 1, reading some metadata")
            length, = struct.unpack("<H", f.read(2))
            print( "# meta data name", f.read(length))
            f.read(0x98)                
        elif object_type == 2:
            print( "# Object type 2")
            name_length, = struct.unpack("<H", f.read(2))
            model_class = f.read(name_length)
            print( "#Some matrix?", model_class)
            for i in range(0, 0x30/4):
                print( "#",hex(f.tell()),i,struct.unpack("f", f.read(4)))
            print( "#End matrix", hex(f.tell()))

            name_length, = struct.unpack("<H", f.read(2))
            model_class = f.read(name_length)
            print( "#Some matrix?", model_class)
            for i in range(0, 0x30/4):
                print( "#",i,struct.unpack("f", f.read(4)))
            print( "#End matrix", hex(f.tell()))

            print( "#Start some unknown")
            for i in range(0, 26):
                print( "#",i,struct.unpack("f", f.read(4)))
            print( "#End unknown", hex(f.tell()))
        elif object_type == 0:
            print( "# Object type 1, reading some metadata of size 0x68")
            f.read(0x68)        
    else:
        length, = struct.unpack("<xxH", f.read(4))
        print( "# unknown meta", f.read(length))
        f.read(0xCC)
        print( "# unknown meta finished", hex(f.tell()))
        
    f.read(4) # 0
    name_length, = struct.unpack("<H", f.read(2))
    texture_name = f.read(name_length)
    print( "#Texture name", texture_name)

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
        x,y,z = struct.unpack("fff", f.read(12))
        if is_dump: print( "v",x,y,z, file=fout)
    print( "#End vertices", hex(f.tell()))
    ###############################################
    
    print( "#Start uknown")
    count, = struct.unpack("<I", f.read(4))
    print( "# Uknown count", count)
    for i in range(0, count):
        unk, = struct.unpack("<H", f.read(2))
        #print( "#",i, unk)
    print( "#End uknown", hex(f.tell()))
    print( "# End model ##############################################################")
    f.read(4) # 0
    f.read(1)

    fout.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool for experimenting with mdr files.')
    parser.add_argument('file', nargs='?', help='Input file')
    args = parser.parse_args()

    filepath = None
    if args.file == None:            
        #filepath = "simple\\ak-74-lod-2.mdr"    # type 2, 3 models
        filepath = "simple\\ak-74.mdr"         # type 2, 3 models
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
            dump_model(base_name, f, i)
