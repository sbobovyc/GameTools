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
import json
from pprint import pprint


def float2string(f):
    return "{0:.12f}".format(f)


def short2float(value):
    return float(value + 2**15) / 2**15 - 1.0

########
# object:
# face indices
# UVs,
# then,
# vertices (in object space?)
# then,
# normals
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
        self.vertex_normal_array = []  # [ (i16,i16,i16) ...]
        self.texture_name = ""
        self.material = None
        #TODO add meta data objects

    def make_wavefront_obj(self):
        """ Serialize mdr to obj format and return it as a string."""        
        string = ""
        string += "o %s\n" % self.name
        # write material info
        string += "mtllib %s\n" % self.name
        string += "usemtl %s\n" % self.name

        use_Blender_order = True
        # write vertex info
        if use_Blender_order:
            for vert in self.vertex_array:
                string += "v %s %s %s\n" % ( float2string(vert[0]), float2string(vert[1]), float2string(vert[2]))
            for uv in self.uv_array:
                string += "vt %s %s\n" % (uv[0], uv[1])
            for norm in self.vertex_normal_array:
                string += "vn %s %s %s\n" % (short2float(norm[0]), short2float(norm[1]), short2float(norm[2]))
            for idx in self.index_array:
                string += "f %i/%i/%i %i/%i/%i %i/%i/%i\n" % (
                idx[0] + 1, idx[0] + 1, idx[0] + 1, idx[1] + 1, idx[1] + 1, idx[1] + 1, idx[2] + 1, idx[2] + 1,
                idx[2] + 1)
        else:
            for idx in self.index_array:
                string += "f %i/%i/%i %i/%i/%i %i/%i/%i\n" % (
                idx[0] + 1, idx[0] + 1, idx[0] + 1, idx[1] + 1, idx[1] + 1, idx[1] + 1, idx[2] + 1, idx[2] + 1,
                idx[2] + 1)
            for uv in self.uv_array:
                string += "vt %s %s\n" % (uv[0], uv[1])            
            for vert in self.vertex_array:
                string += "v %s %s %s\n" % ( float2string(vert[0]), float2string(vert[1]), float2string(vert[2]))
            for norm in self.vertex_normal_array:
                string += "vn %s %s %s\n" % (short2float(norm[0]), short2float(norm[1]), short2float(norm[2]))

        return string

    def make_wavefront_mtl(self):
        """ Create a material definition file."""
        string = ""
        string += "newmtl %s\n" % self.name
        if self.material is None:
            string += "Ka 0.5 0.5 0.5 # gray\n"   # ambient color
            string += "Kd 0.5 0.5 0.5 # gray\n"   # diffuse color
            string += "Ks 0.0 0.0 0.0\n"          # specular color, off
            string += "Ns 0.0\n"                  # specular exponent
        else:
            string += "Ka %f %f %f\n" % (self.material["ambient_color"])
            string += "Kd %f %f %f\n" % (self.material["diffuse_color"])
            string += "Ks %f %f %f\n" % (self.material["specular_color"])
            string += "Ns %f\n" % (self.material["specular_exponent"])
        string += "d 1.0\n"                   # transparency        
        string += "illum 1\n"                 # Color on and Ambient on
        string += "map_Kd %s.bmp\n" % self.texture_name
        return string
    

def read_matrix(f):
    print("# Start reading metadata", "0x%x" % f.tell())
    meta = [3*[0] for i in range(4)]
    for i in range(0, 4):
        for j in range(0, 3):
            value, = struct.unpack("f", f.read(4))
            print("# 0x%x [%i] %f" % (f.tell()-4, i, value))
            meta[i][j] = value
    pprint(meta)
    transform_matrix = [ 4*[0] for i in range(4)]
    for i in range(0, 4):
        for j in range(0, 3):
            transform_matrix[j][i] = meta[i][j]
    transform_matrix[3][3] = 1.0
    print("# This is mostly likely this transform matrix:")
    pprint(transform_matrix)
    print("# End metadata", "0x%x" % f.tell())
    return meta


def read_material(f):
    print("# Start reading material", "0x%x" % f.tell())
    unknown_constants = struct.unpack("ff", f.read(8))
    print("# Unknown constants", unknown_constants)
    ambient_color = struct.unpack("fff", f.read(4 * 3))
    print("# Ambient color", ambient_color)
    diffuse_color = struct.unpack("fff", f.read(4 * 3))
    print("# Diffuse color", diffuse_color)
    specular_color = struct.unpack("fff", f.read(4 * 3))
    print("# Specular color", specular_color)
    specular_exponent, = struct.unpack("f", f.read(4))
    print("# Specular exponent", specular_exponent)
    print("# End material", "0x%x" % f.tell())

    material = {}
    material["unknown_constants"] = unknown_constants
    material["ambient_color"] = ambient_color
    material["diffuse_color"] = diffuse_color
    material["specular_color"] = specular_color
    material["specular_exponent"] = specular_exponent
    return material


def dump_model(base_name, num_models, f, model_number, outdir, dump = True, verbose=False):
    print("# Start model", "0x%x" % f.tell(), "##############################################################")
    name_length, = struct.unpack("<H", f.read(2))
    print("# submodel name length", name_length)
    submodel_name = f.read(name_length).decode("ascii")
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

    unk, = struct.unpack("b", f.read(1))
    print("# Read unknown byte (always 2?):", unk)
    print("# Start unknown section", "0x%x" % f.tell())    
    for i in range(0, int(0xB0/4)):
        unk, = struct.unpack("f", f.read(4))
        if verbose:
            print("# [%i] %f" % (i, unk))
    print("# Finished unknown section", "0x%x" % f.tell())


    ###############################################
    print("# Start face vertex indices")
    face_count, = struct.unpack("<I", f.read(4))
    print("# Face count:", face_count/3)
    manifest = {u'model' : base_name, u'sub_model': submodel_name, u'vertex_index_offset' : f.tell()}    
    
    for i in range(0, int(face_count/3)):
        if not dump:
            f.read(6)
        else:
            v0, v1, v2 = struct.unpack("<HHH", f.read(6))
            #print("f %i/%i %i/%i %i/%i" % (v0+1,v0+1,v1+1,v1+1,v2+1,v2+1))
            mdr_obj.index_array.append((v0,v1,v2))
    print("# Finished face vertex indices", "0x%x" % f.tell())
    ###############################################

    ###############################################
    print("# Start UVs")
    uv_in_section, = struct.unpack("<I", f.read(4))
    print("# UV in section:", uv_in_section/2)

    manifest[u'uv_offset'] = f.tell()    
    
    for i in range(0, int(uv_in_section/2)):
        if not dump:
            f.read(8)
        else:
            u,v = struct.unpack("<ff", f.read(8))        
            #print("vt", u,v)
            mdr_obj.uv_array.append((u,v))                    
    print("# Finish UV section:", "0x%x" % f.tell())
    ###############################################

    print("# Start unknown section 1")
    unk, = struct.unpack("<I", f.read(4))
    print("# Unknown", "0x%x" % unk)

    if model_number == 0:
        print("# Some matrix?")
        for i in range(0, int(0x30/4)):
            unk1,unk2 = struct.unpack("ff", f.read(8))
            if verbose:
                print("# [%i] %f, %f" % (i, unk1, unk2))
        
        print("# End unknown section", "0x%x" % f.tell())
        unk, = struct.unpack("<I", f.read(4))
        print("# Read 4 bytes (always 0?)", unk)
        #TODO object_type is probably really count for some metadata
        object_type, = struct.unpack("<I", f.read(4))
        print("# Read 4 bytes, object type?: ", object_type)

        if object_type == 0: #TODO not object type, but count of meta data?
            print( "# Object type 0, reading some metadata of size 0x68")
            #print("%s, type 0, model_number=%i out of %i, %s" % (base_name, model_number, num_models, hex(f.tell())), file=logger)
            manifest[u'material'] = []
            length, = struct.unpack("<H", f.read(2))
            meta0_offset = f.tell()
            # first set of meta data is some kind of text, probably random garbage
            print("# random garbage? ", "0x%x" % f.tell())
            unk = f.read(48)
            length, = struct.unpack("<H", f.read(2))
            meta1_offset = f.tell()
            meta1 = read_material(f)
            if dump:
                mdr_obj.material = meta1
            manifest[u'material'].append( ( {u'offset': meta1_offset}, meta1) )
            print("# Unknown float", struct.unpack("f", f.read(4)))
            print("# end object type 0", "0x%x" % f.tell())
        elif object_type == 1:
            # This type seems to occur only in the first model.
            print("# Object type 1, reading some metadata")
            length, = struct.unpack("<H", f.read(2))
            name = f.read(length) #TODO this is same as meta2 tags
            print("# Meta data name", name)
            #print("%s, type 1, model_number=%i out of %i, name=%s, %s" % (base_name, model_number, num_models, name, hex(f.tell())), file=logger)
            manifest[u'material'] = []
            manifest[u'type1'] = []
            meta0_offset = f.tell()
            meta0 = read_matrix(f)
            manifest[u'type1'].append( ( {u'offset': meta0_offset}, meta0) )
            length, = struct.unpack("<H", f.read(2))
            meta1_offset = f.tell()
            meta1 = read_matrix(f)
            manifest[u'type1'].append( ( {u'offset': meta1_offset}, meta1) )
            length, = struct.unpack("<H", f.read(2))
            meta2_offset = f.tell()
            meta2 = read_material(f)  #TODO needs to be tested
            if dump:
                mdr_obj.material = meta2
            manifest[u'material'].append(({u'offset': meta2_offset}, meta2))
            print("# Unknown float", struct.unpack("f", f.read(4)))
            print("# End object type 1","0x%x" % f.tell())
        elif object_type == 2:
            print("# Object type 2")
            name_length, = struct.unpack("<H", f.read(2))
            model_class = f.read(name_length) #TODO this is same as meta2 tags
            print("# Some meta?", model_class)
            manifest[u'material'] = []
            manifest[u'type2'] = []
            meta0_offset = f.tell()
            meta0 = read_matrix(f)
            manifest[u'type2'].append(({u'offset': meta0_offset}, meta0))
            name_length, = struct.unpack("<H", f.read(2))
            model_class = f.read(name_length)
            print("# Some meta?", model_class)
            meta1_offset = f.tell()
            meta1 = read_matrix(f)
            manifest[u'type2'].append(({u'offset': meta1_offset}, meta1))

            print("# Start some unknown")
            print("# Unknown", "0x%x" % struct.unpack("I", f.read(4)))
            meta2_offset = f.tell()
            meta2 = read_matrix(f)
            manifest[u'type2'].append(({u'offset': meta2_offset}, meta2))
            meta3_offset = f.tell()
            meta3 = read_material(f) #TODO needs to be tested
            if dump:
                mdr_obj.material = meta3
            manifest[u'material'].append(({u'offset': meta3_offset}, meta2))
            print("# Unknown", "0x%x" % struct.unpack("I", f.read(4)))
            print("#End unknown", "0x%x" % f.tell())
        elif object_type >= 14:
            for i in range(0, object_type):
                name_length, = struct.unpack("<H", f.read(2))
                print(f.read(name_length))
                read_matrix(f)
            f.read(0x68)
            print("# End unknown", "0x%x" % f.tell())
    else:
        length, = struct.unpack("<xxH", f.read(4))
        unknown_meta = f.read(length).decode("ascii")
        print("# unknown meta2", unknown_meta)
        valid_weapon_meta_list = ["weapon", "tripod", "base", "clip", "mortar", "missile", "grenade", "day sight",
                                  "m1a2", "m203", "m320", "day", "cylinder01", "ammo", "bogus-weapon", "periscope_circle",
                                  "mgbracket", "crows_structure", "launcher support"]
        valid_building_meta_list = ["junkdebris", "level", "roof", "wall"]
        valid_vehicle_meta_list = ["canvas", "gear", "hull", "hatch", "loadershield", "mount", "muzzle", "turret", "wheel"]
        valid_meta_list = valid_weapon_meta_list + valid_building_meta_list + valid_vehicle_meta_list
        
        if True in map(lambda x: unknown_meta.startswith(x), valid_meta_list):
            print("# Reading", unknown_meta)
            f.read(0x60)
            count, = struct.unpack("<I", f.read(4))
            print("# Count", count)
            if count == 0:
                f.read(0x68)
            else:
                for i in range(0, count):
                    length, = struct.unpack("<H", f.read(2))
                    unknown_meta2 = f.read(length).decode("ascii")
                    print("Sub-meta", unknown_meta2)
                    valid_sub_meta = ["commander", "eject", "gunner", "leader", "loader", "link", "muzzle",
                                      "firespot", "smoke", "weapon"]
                    print(map(lambda x: unknown_meta2.startswith(x), valid_sub_meta))
                    if True in map(lambda x: unknown_meta2.startswith(x), valid_sub_meta):
                        read_matrix(f)
                        print("#End of sub-meta", "0x%x" % f.tell())
                    elif length == 0:
                        print("#End of sub-meta", "0x%x" % f.tell())
                    else:                        
                        read_matrix(f)
                        print("#Possible error0 in %s! (%s) Report about it on the forum." % (f.name, unknown_meta2))
                        print("#End of sub-meta", "0x%x" % f.tell())
                        sys.exit(0)
                special_meta_list = ["weapon", "base", "tripod", "launcher support", "mount", "hull", "turret"]
                if True in map(lambda x: unknown_meta.startswith(x), special_meta_list):
                    f.read(0x68)
                else:
                    print("# Possible error1 in %s! (%s) Report about it on the forum." % (f.name, unknown_meta))
                    sys.exit(0)
        else:
            print("#Possible error2 in %s! (%s) Report about it on the forum." % (f.name, unknown_meta))
            sys.exit(0)
        print("# Unknown meta finished", "0x%x" % f.tell())

    unk, = struct.unpack("<I", f.read(4))
    print("# Read 4 bytes (always 0?)", unk)

    name_length, = struct.unpack("<H", f.read(2))
    texture_name = f.read(name_length).decode("ascii")
    print("# Texture name", texture_name)
    if dump:
        mdr_obj.texture_name = texture_name

    unk, = struct.unpack("b", f.read(1))
    print("# Read unknown byte (always 2?):", unk)

    print("# Start unknown section of 176 bytes", "0x%x" % f.tell())
    for i in range(0, int(0xB0/4)):
        unk, = struct.unpack("f", f.read(4))
        if verbose:
            print("# [%i] %i" % (i, unk))
    print("# Finished unknown section", "0x%x" % f.tell())

    ###############################################
    print("# Start vertices")
    vertex_floats, = struct.unpack("<I", f.read(4))
    print("# Vertices", vertex_floats/3)
    manifest[u'vertex_offset'] = f.tell()
    
    for i in range(0, int(vertex_floats/3)):
        if not dump:
            f.read(12)
        else:
            x, y, z = struct.unpack("fff", f.read(12))
            mdr_obj.vertex_array.append((x, y, z))
    print("# End vertices", "0x%x" % f.tell())
    ###############################################
    
    print("# Start vertex normals")
    count, = struct.unpack("<I", f.read(4))
    print("# Normals count", count/3) # 3 per vertex
    for i in range(0, int(count/3)):
        if not dump:
            f.read(6)
        else:
            nx, ny, nz = struct.unpack("<HHH", f.read(6))
            if verbose:
                print("# [%i] %i %i %i" % (i, nx, ny, nz))
            mdr_obj.vertex_normal_array.append((nx, ny, nz))
    print("# End normals", "0x%x" % f.tell())
    print("# End model ##############################################################")
    unk, = struct.unpack("<I", f.read(4))
    print("# Read 4 bytes, at end of model (always 0?)", unk)
    f.read(1)

    if dump:
        obj_fout.write(mdr_obj.make_wavefront_obj().encode("ascii"))
        mtl_fout.write(mdr_obj.make_wavefront_mtl().encode("ascii"))
        obj_fout.close()
        mtl_fout.close()
    logger.close()
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool for experimenting with mdr files.')
    parser.add_argument('-p', '--parse-only', default=False, action='store_true',
                        help='Only parse file, do not dump models')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Print more info useful for debugging')
    parser.add_argument('-o', '--outdir', default=os.getcwd(), help='Output path')
    parser.add_argument('file', nargs='?', help='Input file')
    args = parser.parse_args()

    filepath = None
    if args.file is None:
        print("Error, supply a file as parameter")
        sys.exit()
    else:
        filepath = args.file
    
    print("# ", filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    model_manifests = []
    with open(filepath, "rb") as f:
        num_models, = struct.unpack("<Ix", f.read(5))
        print("# number of models", num_models)
        for i in range(0, num_models):
            manifest = dump_model(base_name, num_models, f, i, args.outdir, not args.parse_only, args.verbose)
            model_manifests.append(manifest)

    if not args.parse_only:
        with open(os.path.join(args.outdir, "%s_manifest.json" % base_name), "w") as f:
            json.dump([u'%s' % base_name, model_manifests], f, indent=4)
