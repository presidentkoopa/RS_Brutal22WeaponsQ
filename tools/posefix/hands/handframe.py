"""Where a HUD model's vertices sit relative to the VR controller (QZD 17.3).

Chain (models.cpp RenderHUDModel + hw_vrmodes GetWeaponTransform):
  hand(m) * S(.01) * T(0,5,30) * S(xs,zs,ys) * T(off/scale) * Ry(90) * S(vr_weaponScale) * v_render
with v_render = (fx, fz, fy) (models_md3.cpp). Local frame of the hand transform:
x = right, y = up, -z = forward (MapWeaponDir), units = metres.
Prints per frame: forward (m), right (m), up (m) of chosen points.
"""
import struct, sys, math

def frames(path):
    d = open(path, 'rb').read()
    nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
    out = [[] for _ in range(nfr)]
    off = osurf
    for s in range(nsurf):
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        for f in range(snfr):
            base = off + oxyz + f * nv * 8
            for v in range(nv):
                x, y, z = struct.unpack_from('<3h', d, base + v * 8)
                out[f].append((s, x / 64., y / 64., z / 64.))
        off += oend
    return out

def to_hand(fx, fy, fz, xs=-1, ys=1, zs=1, xo=0, yo=0, zo=-5, ws=1.02):
    # p = Ry(90) * ws * (fx, fz, fy) = ws*(fy, fz, -fx); then scale (xs, zs, ys) + offsets
    lx = 0.01 * (ws * xs * fy + xo)
    ly = 0.01 * (ws * zs * fz + zo + 5)
    lz = 0.01 * (ws * ys * -fx + yo + 30)
    return (-lz, lx, ly)   # forward, right, up

if __name__ == '__main__':
    path = sys.argv[1]
    fr = [int(a) for a in sys.argv[2].split(',')]
    F = frames(path)
    for f in fr:
        pts = [to_hand(x, y, z) for s, x, y, z in F[f]]
        fw = [p[0] for p in pts]; rt = [p[1] for p in pts]; up = [p[2] for p in pts]
        far = max(pts, key=lambda p: math.sqrt(p[0]**2 + p[1]**2 + p[2]**2))
        print('frame %d: fwd %.2f..%.2f  right %.2f..%.2f  up %.2f..%.2f  farthest %s (%.2f m)' % (
            f, min(fw), max(fw), min(rt), max(rt), min(up), max(up),
            tuple(round(c, 2) for c in far), math.sqrt(sum(c*c for c in far))))
