import argparse
import sys
import struct

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool that\'s used to read apitrace raw data dumps of vertex data and print wavefront obj vertices. It can also be used with any other raw data.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', nargs='?', help='Raw file')
    parser.add_argument('-o', '--offset', default=0, help='Offset into file')
    parser.add_argument('-c', '--count', default=sys.maxint, help='Number of vertices')
    
    args = parser.parse_args()    
    path = args.file
    offset = args.offset
    count = args.count
    if len(sys.argv) >= 3:
        offset = int(sys.argv[2], 16)
    if len(sys.argv) == 4:
        count = int(sys.argv[3])*3*4
        
    byte_count = 0
    with open(path, 'rb') as f:
        f.seek(offset)
        while byte_count < count:
            buf = f.read(3*4)
            if not buf: break
            f1,f2,f3 = struct.unpack("fff", buf)
            print "v",f1,f2,f3
            byte_count += 3*4

    print "# number of bytes", byte_count

