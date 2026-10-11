"""Topology signature of an md3: per surface (verts, tris, hash of triangles+texcoords).
Same signature = same mesh, whatever frames it carries."""
import struct, hashlib, sys, os
def sig(path):
    d = open(path, 'rb').read()
    if d[:4] != b'IDP3': return None
    nfr, ntag, nsurf = struct.unpack_from('<3i', d, 76)
    osurf, = struct.unpack_from('<i', d, 100)
    off = osurf; out = []
    for s in range(nsurf):
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        h = hashlib.md5(d[off+otri:off+otri+nt*12] + d[off+ost:off+ost+nv*8]).hexdigest()[:10]
        out.append((nv, nt, h))
        off += oend
    return nfr, tuple(out)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, sig(p))
