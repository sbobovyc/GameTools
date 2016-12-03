# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import csv
import mathutils
from bpy_extras.io_utils import unpack_list, unpack_face_list, axis_conversion
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       )
from collections import OrderedDict

bl_info = {
    "name": "PIX CSV",
    "author": "Stanislav Bobovych",
    "version": (1, 0, 0),
    "blender": (2, 7, 8),
    "location": "File > Import-Export",
    "description": "Import PIX csv dump of mesh. Import mesh, normals and UVs.",
    "category": "Import"}


class PIX_CSV_Operator(bpy.types.Operator):
    bl_idname = "object.pix_csv_importer"
    bl_label = "Import PIX csv"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob = StringProperty(default="*.csv", options={'HIDDEN'})
    mirror_x = bpy.props.BoolProperty(name="Mirror X",
                                      description="Mirror all the vertices across X axis",
                                      default=True)
                                      
    vertex_order = bpy.props.BoolProperty(name="Change vertex order",
                                      description="Reorder vertices in counter-clockwise order",
                                      default=True)
    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='Z')

    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
                )

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob"))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        print(keywords)
        importCSV(**keywords)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Import options")

        row = col.row()
        row.prop(self, "mirror_x")
        row = col.row()
        row.prop(self, "vertex_order")
        layout.prop(self, "axis_forward")
        layout.prop(self, "axis_up")


def make_mesh(verteces, faces, normals, uvs, global_matrix):
    mesh = bpy.data.meshes.new('name')
    mesh.vertices.add(len(verteces))
    mesh.vertices.foreach_set("co", unpack_list(verteces))
    mesh.tessfaces.add(len(faces))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(faces))

    index = 0
    for vertex in mesh.vertices:
        vertex.normal = normals[index]
        index += 1

    uvtex = mesh.tessface_uv_textures.new()
    uvtex.name = "UV"

    for face, uv in enumerate(uvs):
        data = uvtex.data[face]
        data.uv1 = uv[0]
        data.uv2 = uv[1]
        data.uv3 = uv[2]
    mesh.update(calc_tessface=False, calc_edges=False)

    obj = bpy.data.objects.new('name', mesh)
    # apply transformation matrix
    obj.matrix_world = global_matrix
    bpy.context.scene.objects.link(obj)  # link object to scene


def importCSV(filepath=None, mirror_x=False, vertex_order=True, global_matrix=None):
    if global_matrix is None:
        global_matrix = mathutils.Matrix()

    if filepath == None:
        return
    vertex_dict = {}
    normal_dict = {}

    vertices = []
    faces = []
    normals = []
    uvs = []

    with open(filepath) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
#        face_count = sum(1 for row in reader) / 3
#        print(face_count)

        f.seek(0)
        reader = csv.reader(f)
        next(reader)  # skip header

        current_face = []
        current_uv = []
        i = 0
        x_mod = 1
        if mirror_x:
            x_mod = -1
        for row in reader:
            vertex_index = int(row[0])
            vertex_dict[vertex_index] = (x_mod*float(row[2]), float(row[3]), float(row[4]))
                #TODO how are axis really ligned up?
#            x, y, z = (vertex_dict[vertex_index][0], vertex_dict[vertex_index][1], vertex_dict[vertex_index][2])
#            vertex_dict[vertex_index] = (x, z, y)
            normal_dict[vertex_index] = (float(row[6]), float(row[7]), float(row[8]))
            #TODO add support for changing the origin of UV coords
            uv = (float(row[9]), 1.0 - float(row[10]))  # modify V

            if i < 2:
                current_face.append(vertex_index)
                current_uv.append(uv)
                i += 1
            else:
                current_face.append(vertex_index)
                #TODO add option to change order of marching vertices
                if vertex_order:
                    faces.append((current_face[2], current_face[1], current_face[0]))
                else:
                    faces.append(current_face)
                current_uv.append(uv)
                uvs.append(current_uv)
                current_face = []
                current_uv = []
                i = 0

        for i in range(len(vertex_dict)):
            if i in vertex_dict:
                pass
            else:
    #            print("missing",i)
                vertex_dict[i] = (0, 0, 0)
                normal_dict[i] = (0, 0, 0)

        # dictionary sorted by key
        vertex_dict = OrderedDict(sorted(vertex_dict.items(), key=lambda t: t[0]))
        normal_dict = OrderedDict(sorted(normal_dict.items(), key=lambda t: t[0]))

        for key in vertex_dict:
            vertices.append(list(vertex_dict[key]))
    #        print(key,vertex_dict[key])
        for key in normal_dict:
            normals.append(list(normal_dict[key]))

    #    print(vertices)
    #    print(faces)
    #    print(normals)
    #    print(uvs)
        make_mesh(vertices, faces, normals, uvs, global_matrix)


def menu_func_import(self, context):
    self.layout.operator(PIX_CSV_Operator.bl_idname, text="PIX CSV (.csv)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
#    register()
#    These run the script from "Run script" button
    bpy.utils.register_class(PIX_CSV_Operator)
    bpy.ops.object.pix_csv_importer('INVOKE_DEFAULT')
