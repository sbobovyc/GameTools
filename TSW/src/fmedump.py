import struct

#filename = "assault_rifle_ak_01.fme"
#filename = "assault_rifle_mp5_01.fme"
#filename = "assault_rifle_ak_01_enh1.fme"
filename = "assault_rifle_m16_03.fme"
offset = 0xA45
#offset = 0x14D70
offset = 0xA38
verteces = []
UVs = []
faces = []
with open(filename, "rb") as f:
    f.seek(offset)
    vertex_count, = struct.unpack("<I", f.read(4))
    print "# Vertex count", vertex_count    
    print "# filename", filename
    for i in range(0, vertex_count):
        x,y,z,w = struct.unpack("ffff", f.read(16))
        #f.read(0x14)
        f.read(0xC)
        u, v = struct.unpack("ff", f.read(8))
        verteces.append((x,y,z))
        UVs.append((u,v))
    print "# after reading verteces", hex(f.tell())

    triangle_count, = struct.unpack("<I", f.read(4))
    print "# Triangle count", triangle_count
    for i in range(0, triangle_count):
        idx0, idx1, idx2 = struct.unpack("<HHH", f.read(6))
        faces.append((idx0, idx1, idx2))

    print "# after reading face definitions", hex(f.tell())

# increment vertex index by 1 since obj indeces start at 1 instead of 0
i = 1 
for v in verteces:
    print "# ", i
    print "v %f %f %f" % (v[0], v[1], v[2])
    i += 1

for vt in UVs:
    print "vt %f %f" % (vt[0], 1.0 - vt[1])

for f in faces:
    print "f %i/%i %i/%i %i/%i" % (f[0]+1, f[0]+1, f[1]+1, f[1]+1, f[2]+1, f[2]+1)

