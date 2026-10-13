"""Splits parts of an IQM mesh into new meshes of the same file: the same vertices, joints,
poses and frames; only the order of the triangles inside each mesh changes, and a few
mesh-table entries are added (24 bytes each). A part is the triangles whose three vertices
are skinned (rigidly) to one of the given joints. Then a MODELDEF SurfaceSkin can show or
hide that part on its own (models_iqm.cpp draws each mesh's FirstTriangle..NumTriangles
range; the vertex range of a mesh is not used to draw).

BD22 Sniper (hk416.iqm in RS_BD22_Models_v8.pk3, the mesh the pack ships):
  mesh 8 (mag.bmp, rounds) and 9 (Magpul_Diffuse.bmp, the PMAG): the seated magazine is
  skinned to j_mag1 (joint 61), the parked new one to j_mag2 (62)  -> new meshes 13, 14
  mesh 3 (1.bmp): the charging handle, skinned to j_charginghandle (63) -> new mesh 15

usage: iqm_split.py <in.iqm> <out.iqm>
"""
import struct, sys
import numpy as np

HDR = ('magic16 ver fsize flags ntext otext nmesh omesh nva nvert ova ntri otri oadj njoint ojoint '
       'npose opose nanim oanim nframe nchan oframe obounds ncom ocom next oext').split()[1:]

SNIPER = [(8, {61}), (9, {61}), (3, {63})]


def header(d):
    return dict(zip(HDR, struct.unpack_from('<27I', d, 16)))


def split(src, dst, rules):
    d = bytes(open(src, 'rb').read())
    assert d[:16] == b'INTERQUAKEMODEL\0'
    h = header(d)
    nmesh, omesh, ntri, nvert = h['nmesh'], h['omesh'], h['ntri'], h['nvert']
    meshes = [list(struct.unpack_from('<6I', d, omesh + i * 24)) for i in range(nmesh)]
    tris = np.frombuffer(d, dtype='<u4', count=ntri * 3, offset=h['otri']).reshape(ntri, 3).copy()
    adj = np.frombuffer(d, dtype='<u4', count=ntri * 3, offset=h['oadj']).reshape(ntri, 3).copy()
    arrays = {}
    for i in range(h['nva']):
        typ, fl, fmt, size, off = struct.unpack_from('<5I', d, h['ova'] + i * 20)
        if typ in (4, 5):
            assert fmt == 1
            arrays[typ] = np.frombuffer(d, dtype='u1', count=nvert * size, offset=off).reshape(nvert, size)
    joint = arrays[4][:, 0].astype(int)
    rigid = arrays[5][:, 0] == 255
    perm = np.arange(ntri)
    new_meshes = []
    report = []
    for m, joints in rules:
        name, mat, fv, nv, ft, nt = meshes[m]
        rng = np.arange(ft, ft + nt)
        tv = tris[perm[rng]]
        inpart = np.isin(joint[tv], list(joints)) & rigid[tv]
        moved = inpart.all(1)
        mixed = int((inpart.any(1) & ~moved).sum())
        if mixed:
            raise SystemExit('mesh %d: %d triangles only partly on joints %s' % (m, mixed, joints))
        order = np.concatenate([rng[~moved], rng[moved]])
        perm[rng] = perm[order]
        kept = int((~moved).sum())
        meshes[m][5] = kept
        new_meshes.append([name, mat, fv, nv, ft + kept, int(moved.sum())])
        report.append((m, sorted(joints), kept, int(moved.sum()), len(meshes) + len(new_meshes) - 1))
    inv = np.empty(ntri, dtype=np.int64)
    inv[perm] = np.arange(ntri)
    tris2 = tris[perm]
    adj2 = adj[perm].astype(np.int64)
    none = adj2 == 0xFFFFFFFF
    adj2 = np.where(none, 0xFFFFFFFF, inv[np.where(none, 0, adj2)]).astype('<u4')
    # rebuild: mesh table grows by 24 bytes per new mesh, everything after it moves up
    allm = meshes + new_meshes
    grow = 24 * len(new_meshes)
    at = omesh + 24 * nmesh
    out = bytearray(d[:at]) + bytearray(grow) + bytearray(d[at:])
    for i, mm in enumerate(allm):
        struct.pack_into('<6I', out, omesh + i * 24, *mm)
    h2 = dict(h)
    h2['nmesh'] = len(allm)
    h2['fsize'] = len(out)
    for k in ('otext', 'ova', 'otri', 'oadj', 'ojoint', 'opose', 'oanim', 'oframe', 'obounds', 'ocom', 'oext'):
        if h2[k] and h2[k] >= at:
            h2[k] += grow
    struct.pack_into('<27I', out, 16, *[h2[k] for k in HDR])
    for i in range(h['nva']):
        p = h2['ova'] + i * 20
        typ, fl, fmt, size, off = struct.unpack_from('<5I', out, p)
        if off >= at:
            struct.pack_into('<5I', out, p, typ, fl, fmt, size, off + grow)
    out[h2['otri']:h2['otri'] + ntri * 12] = tris2.astype('<u4').tobytes()
    out[h2['oadj']:h2['oadj'] + ntri * 12] = adj2.tobytes()
    # checks: every other block is byte-identical, every triangle is still there once
    for k, n in (('ojoint', 48 * h['njoint']), ('opose', 88 * h['npose']), ('oframe', 2 * h['nchan'] * h['nframe']),
                 ('obounds', 32 * h['nframe']), ('otext', h['ntext'])):
        assert out[h2[k]:h2[k] + n] == d[h[k]:h[k] + n], k
    assert sorted(map(tuple, tris2.tolist())) == sorted(map(tuple, tris.tolist()))
    open(dst, 'wb').write(out)
    return report, len(d), len(out)


if __name__ == '__main__':
    rep, a, b = split(sys.argv[1], sys.argv[2], SNIPER)
    for m, j, kept, moved, nm in rep:
        print('mesh %d: %d triangles stay, %d (joints %s) -> new mesh %d' % (m, kept, moved, j, nm))
    print('size %d -> %d (+%d bytes)' % (a, b, b - a))
