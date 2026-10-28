"""2.0.2 (owner item 34): rev_vr.md3 = the Moonlight's rev.md3 with its 41 frames kept IN THE HAND.

rev.md3's animation moves the whole gun as a desktop view model would: the shot kicks it (frames 4-14, the grip moves
~1 mesh unit) and the reload swings it 17-32 deg (frames 16-36, the grip moves up to 4.6 units). In VR the gun is held:
the drawn hand is pinned to the controller, so a gun that swings leaves the hand. Per frame, the gun BODY's rigid motion
(surface 0 python.004, frame and grip, fitted on its rigid vertices: the trigger moves inside it in frames 1-3) is
measured against frame 0 and:
  - shot frames 1-15: the body's turn is KEPT (the kick), pivoted about the grip centre, so the grip stays in the palm;
  - reload / draw frames 16-40: the body's motion is REMOVED, so the body stays exactly in the hand and only what moves
    ON the gun moves: the break-top (surfaces 1+3) opening, the six rounds ejecting, the speedloader, the hammer.
Every surface of a frame gets the same transform (its normals turned with it). Frame 0 is unchanged (the hand fit, the
pickup and rev_rsb.md3 all use it). usage: moon_bake.py [in rev.md3] [out rev_vr.md3]"""
import struct, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from moon_frames import kab, angax
D = os.path.join(HERE, '../../src/models/bd/Moonlight')
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'rev.md3')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, 'rev_vr.md3')
KICK_LAST = 15

def dec_n(n):
    lat = ((n >> 8) & 255) * 2 * np.pi / 255; lng = (n & 255) * 2 * np.pi / 255
    return np.c_[np.cos(lng) * np.sin(lat), np.sin(lng) * np.sin(lat), np.cos(lat)]

def enc_n(v):
    v = v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)
    lat = (np.degrees(np.arccos(np.clip(v[:, 2], -1, 1))) * 255 / 360).round().astype(int) & 255
    lng = (np.degrees(np.arctan2(v[:, 1], v[:, 0])) * 255 / 360).round().astype(int) & 255
    return (lat << 8) | lng

def body_fit(A, B):
    keep = np.ones(len(A), bool)
    for _ in range(4):
        R, t, e = kab(A[keep], B[keep])
        res = np.linalg.norm(A @ R.T + t - B, axis=1)
        keep = res < max(0.08, np.percentile(res, 60) * 2)
    return R, t, res[keep].max(), keep.sum()

d = bytearray(open(SRC, 'rb').read())
_, ver, _, _, nf, nt, ns, nsk, ofr, otg, osu, oeof = struct.unpack_from('<4si64siiiiiiiii', d, 0)
surfs = []; o = osu
for _ in range(ns):
    sid, sname, sfl, snf, nsh, nv, ntr, otri, osh, ost, oxyz, oend = struct.unpack_from('<4s64siiiiiiiiii', d, o)
    raw = np.frombuffer(bytes(d[o + oxyz:o + oxyz + snf * nv * 8]), '<i2').reshape(snf, nv, 4).copy()
    surfs.append(dict(o=o, oxyz=oxyz, nv=nv, raw=raw, xyz=raw[:, :, :3] / 64.0, n=raw[:, :, 3].astype(np.int32) & 0xFFFF))
    o += oend
body = surfs[0]['xyz']
low = body[0][:, 2] < np.percentile(body[0][:, 2], 25)
g = body[0][low].mean(0)				# the grip centre (lowest quarter of the body), mesh units
print('grip centre (mesh units, frame 0): %.2f %.2f %.2f' % tuple(g))
for f in range(1, nf):
    R, t, res, nk = body_fit(body[0], body[f])
    a, ax = angax(R)
    if f <= KICK_LAST:
        T = lambda X: X - (R @ g + t - g)		# keep the turn, pivot at the grip
        N = lambda V: V
        how = 'kick kept, pivot at the grip'
    else:
        Ri = R.T
        T = lambda X: (X - t) @ Ri.T			# body back where frame 0 has it
        N = lambda V: V @ Ri.T
        how = 'body held in the hand'
    gb = np.linalg.norm((R @ g + t) - g); ga = np.linalg.norm(T((R @ g + t)[None])[0] - g)
    for s in surfs:
        X = T(s['xyz'][f]); V = N(dec_n(s['n'][f]))
        assert np.abs(X).max() * 64 < 32767
        s['raw'][f, :, :3] = np.round(X * 64).astype('<i2')
        if f > KICK_LAST:
            s['raw'][f, :, 3] = enc_n(V).astype(np.uint16).view(np.int16)
    print('f%02d body turn %5.1f deg (fit on %d verts, %.2f) grip moved %.2f -> %.2f  %s' % (f, a, nk, res, gb, ga, how))
for s in surfs:
    d[s['o'] + s['oxyz']:s['o'] + s['oxyz'] + s['raw'].nbytes] = s['raw'].tobytes()
# frame bounds
allx = [np.concatenate([s['raw'][f, :, :3] / 64.0 for s in surfs]) for f in range(nf)]
for f in range(nf):
    mn, mx = allx[f].min(0), allx[f].max(0); c = (mn + mx) / 2
    struct.pack_into('<3f3f3ff', d, ofr + f * 56, *mn, *mx, *c, float(np.linalg.norm(mx - c)))
open(OUT, 'wb').write(bytes(d))
print('wrote', OUT)
