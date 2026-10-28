"""Measure every frame of the Moonlight mesh (src/models/bd/Moonlight/rev.md3): per surface, its rigid motion from
frame 0 (rotation angle and axis, translation, fit residual) and whether it is shown (collapsed = hidden).
Mesh units, the md3's own frame (x forward, y left, z up). usage: moon_frames.py [rev.md3]"""
import struct, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '../../src/models/bd/Moonlight/rev.md3')

def load_md3(p):
    d = open(p, 'rb').read()
    ident, ver, name, flags, nf, nt, ns, nsk, ofr, otg, osu, oeof = struct.unpack_from('<4si64siiiiiiiii', d, 0)
    out = []; o = osu
    for _ in range(ns):
        sid, sname, sfl, snf, nsh, nv, ntr, otri, osh, ost, oxyz, oend = struct.unpack_from('<4s64siiiiiiiiii', d, o)
        xyz = np.frombuffer(d, '<i2', snf * nv * 4, o + oxyz).reshape(snf, nv, 4)[:, :, :3] / 64.0
        out.append(dict(name=sname.split(b'\0')[0].decode(), xyz=xyz.astype(float)))
        o += oend
    return out, nf

def kab(A, B):
    ca, cb = A.mean(0), B.mean(0)
    U, s, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    dd = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, dd]) @ U.T
    return R, cb - R @ ca, np.abs((A - ca) @ R.T + cb - B).max()

def angax(R):
    a = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
    ax = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    n = np.linalg.norm(ax)
    return a, (ax / n if n > 1e-9 else ax)

if __name__ == '__main__':
    S, nf = load_md3(SRC)
    print('rev.md3: %d frames, %d surfaces: %s' % (nf, len(S), ', '.join('%d %s (%d v)' % (i, s['name'], s['xyz'].shape[1]) for i, s in enumerate(S))))
    for f in range(nf):
        row = []
        for i, s in enumerate(S):
            A, B = s['xyz'][0], s['xyz'][f]
            shown = np.ptp(B, 0).max() > 0.01
            if not shown:
                row.append('%d:hidden' % i); continue
            if np.ptp(A, 0).max() <= 0.01:
                row.append('%d:shown c(%.1f %.1f %.1f)' % ((i,) + tuple(B.mean(0)))); continue
            R, t, e = kab(A, B)
            a, ax = angax(R)
            mv = np.abs(B - A).max()
            if mv < 0.02: row.append('%d:rest' % i); continue
            row.append('%d:rot %.1f ax(%.2f %.2f %.2f) mv %.2f fit %.2f' % (i, a, ax[0], ax[1], ax[2], mv, e))
        print('f%02d  ' % f + ' | '.join(row))
