import struct

#filepath = ".\\out\\terrain\\flavor objects\\bin\\bin2.mdr"
#filepath = ".\\out\\terrain\\flavor objects\\bin\\bin1.mdr"
filepath = ".\\out\\vehicles\jeep\jeep-unarmed.mdr"
#vertex_offset = 0xBE
vertex_offset = 0xB8
print "mdr model"

with open(filepath, "rb") as f:
    f.seek(vertex_offset)
    for j in range(0,1):
        f.read(4)
        vertex_count, = struct.unpack("<I", f.read(4))
        print "Vertex count:", vertex_count
        for i in range(0, vertex_count/3):
            v0, v1, v2 = struct.unpack("<HHH", f.read(6))
            #print v0,v1,v2
        print hex(f.tell())
        verts_in_section, = struct.unpack("<I", f.read(4))
        print "Verts in section:", verts_in_section/5    
        for i in range(0, verts_in_section/5):
            #print hex(f.tell())
            f1,f2,f3 = struct.unpack("<fff", f.read(12))            
            u,v = struct.unpack("<ff", f.read(8))
            print "C", f1,f2,f3
            #print u,v
    
