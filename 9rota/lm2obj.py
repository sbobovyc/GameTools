import struct

filename = "Roketa_RPG7_missle.lm"
vertices = 82
faces = 92
with open(filename, "rb") as f:
    f.seek(0x22E)
    print hex(f.tell())
    for i in range(0, vertices):
        x,y,z,nx,ny,nz,u,v,tx,ty,tz,tw, = struct.unpack("<ffffffffffff", f.read(48))
        print i,x,y,z
    print hex(f.tell())
    for i in range(0, faces):
        v1, v2, v3 = struct.unpack("<HHH", f.read(6))
        print v1, v2, v3
    print hex(f.tell())
