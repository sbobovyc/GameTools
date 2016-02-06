""" @author Stanislav Bobovych
    @detail Tested with Blender 2.76
"""
# http://blenderartists.org/forum/showthread.php?115957-Exporting-vertex-tangents
# http://www.keithlantz.net/2011/10/tangent-space-normal-mapping-with-glsl/
# https://www.blender.org/api/blender_python_api_2_76_9/bpy.types.MeshLoop.html?highlight=normal#bpy.types.MeshLoop.normal

import bpy
import mathutils

obj = bpy.context.object 
me = bpy.context.object.data
    
# tangents have to be pre-calculated
# this will also calculate loop normal
me.calc_tangents()

uv_layer = me.uv_layers.active.data
if obj.type == "MESH":
    v = obj.data.vertices
    # loop faces
    for poly in me.polygons:
        print("Polygon", poly.index)
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uv = uv_layer[li].uv
            normal = me.loops[li].normal            
            tangent = me.loops[li].tangent
            bitangent = me.loops[li].bitangent
            print(" Loop index %i (Vertex %i) - UV %f %f" % (li, vi, uv.x, uv.y))
            print(" Vertex position", v[vi].co)
            print(" Vertex normal", v[vi].normal)
            print(" Local space normal", normal)
            print(" Local space tangent", tangent)
            print(" Local space bitangent", bitangent)                                  
            
            #bitangent = me.loops[li].bitangent_sign * normal.cross(tangent)
            #print("Bitangent", bitangent)
            print()
