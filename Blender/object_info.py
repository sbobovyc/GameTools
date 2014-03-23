""" @author Stanislav Bobovych
    @detail Tested with Blender 2.69
"""
import bpy

v  = bpy.context.object.data.vertices
for i in range(0, len(v)):
    print("Vertex index",v[i].index, "Coordinate", v[i].co, "Normal", v[i].normal)

f = bpy.context.object.data.polygons
for i in range(0, len(f)):
    print("Face index",f[i].index, "Vertices", *f[i].vertices)

me = bpy.context.object.data
uv_layer = me.uv_layers.active.data
for poly in me.polygons:
    print("Polygon", poly.index)
    for li in poly.loop_indices:
        vi = me.loops[li].vertex_index
        uv = uv_layer[li].uv
        print("    Loop index %i (Vertex %i) - UV %f %f" % (li, vi, uv.x, uv.y))
