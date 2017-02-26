""" @author Stanislav Bobovych
@detail Tested with Blender 2.75
"""
import bpy

print("\n"*5)
bpy.ops.object.mode_set(mode = 'OBJECT')
if bpy.context.object.type == "MESH":    
    object = bpy.context.object
    # print all vertex groups for each object
    print(object.vertex_groups.keys())
    for group in object.vertex_groups:
        print("Group %i, name %s" % (group.index, group.name))

    for modifier in object.modifiers:
        if modifier.type == 'ARMATURE' and modifier.object:
            armature = modifier.object.data

            for bone in armature.bones:
                if bone.use_deform and bone.name in object.vertex_groups:
                    print("'%s' used for armature deformation" % (bone.name))
                    
    mesh = bpy.context.object.data
    selected_verts = [v for v in mesh.vertices if v.select]
    for v in selected_verts:
        print("Vertex index: %i," % v.index, "Coordinate:", v.co)
        for g in v.groups:
            print("\tGroup: %i," % g.group, object.vertex_groups[g.group].name, "Weight:", g.weight)
            
    selected_faces = [f for f in mesh.polygons if f.select]
    uv_layer = mesh.uv_layers.active.data
    for f in selected_faces:
        print("Face index: %i," % f.index, "vertex indices:", f.vertices[:])
        for li in f.loop_indices:
            vi = mesh.loops[li].vertex_index
            uv = uv_layer[li].uv
            print("    Loop index %i (Vertex %i) - UV %f %f" % (li, vi, uv.x, uv.y))    
else:
    print("Failed to select mesh")