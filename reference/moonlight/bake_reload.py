"""Bake the Moonlight's hand-driven reload mesh and print its RSB rows (lane B moon-reload, 2026-10-27).

usage: python3 bake_reload.py [rev.md3] [out rev_rsb.md3]
Needs the Depot's tools/kit/rgeo.py. Builds on /home/claude/lane_b_r4/moon/bake.py (the loader at
its seat). Every number below comes off rev.md3 (41 frames, sha1 81e48872):

rev_rsb.md3 = rev.md3 with two frames rewritten (nothing else uses them; firing uses rev.md3):
  frame 1: the six rounds (surfaces 4-9) in their chambers, the speedloader (10) on its seat,
           both carried from the loading frames into the CLOSED gun's frame (the hinged part's
           pose in frame 0), so the RSB hinge turn opens them with the part;
  frame 2: the speedloader on its seat with its six rounds collapsed (the empty cage);
  frame 3: the speedloader's six rounds only, seated (the cage collapsed): what the cylinder holds
           after a speedloader load. Its rounds sit flush (rear F 1.72-1.75, cylinder face 1.85).
  Per-round mode: surfaces 4-9 are carried from frame 20 (the ejector already moving them) and
  slid along their own axis until the rear sits where the loader's rounds sit (F 1.74).
  Every other surface in frames 1-2 = frame 0. Normals of every moved vertex turned with it.
"""
import sys, struct
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/kit')
import numpy as np
from rgeo import load_md3, to_flu

SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/rs_modelswapper/models/vplus/gats/rev.md3'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'rev_rsb.md3'
S = (1.35, 1.35, 1.35); O = (0.0262, 0.9224, 0.5878)   # MODELDEF.rsqmoon (measure_moonlight.py)
a = load_md3(SRC)
M = lambda i, f: a[i]['xyz'][f]


def kab(A, B):
    ca, cb = A.mean(0), B.mean(0)
    U, s, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, cb - R @ ca


def closed(f):
    """mesh frame f -> the closed gun (frame 0), for a point riding the hinged part: x -> x @ A + b"""
    R0, t0 = kab(M(0, 0), M(0, f)); R3, t3 = kab(M(3, 0), M(3, f))
    Rr, tr = R0.T @ R3, R0.T @ (t3 - t0)
    return R0 @ Rr, -(t0 @ R0 + tr) @ Rr        # (x - t0) @ R0 - tr) @ Rr


flu = lambda p: to_flu(np.atleast_2d(p), S, O)

# --- the hinge, frame 26 (the loading pose): the part's fixed point relative to the frame
R0, t0 = kab(M(0, 0), M(0, 26)); R3, t3 = kab(M(3, 0), M(3, 26))
Rr, tr = R0.T @ R3, R0.T @ (t3 - t0)
hm = np.linalg.lstsq(np.eye(3) - Rr, tr, rcond=None)[0]
hm[1] = 0.0                                       # on the axis line: the mesh's centre plane
H = flu(hm)[0]
ang = np.degrees(np.arccos(np.clip((np.trace(Rr) - 1) / 2, -1, 1)))

# --- frame 1 / 2 positions
A20, b20 = closed(20); A26, b26 = closed(26)
rounds = [M(i, 20) @ A20 + b20 for i in range(4, 10)]   # seated, closed (frame 20: rounds in, gun open)
loader = M(10, 26) @ A26 + b26                          # seated, closed
# the loader's six rounds: its 18-vertex components (the cage is 112 + 37)
tri = a[10]['tris']
par = list(range(len(loader)))
def fnd(x):
    while par[x] != x:
        par[x] = par[par[x]]; x = par[x]
    return x
for t in tri:
    par[fnd(t[0])] = fnd(t[1]); par[fnd(t[0])] = fnd(t[2])
X = M(10, 26)
for i in range(len(X)):
    for j in range(i):
        if np.abs(X[i] - X[j]).max() < 1e-4:
            par[fnd(i)] = fnd(j)
comp = {}
for i in range(len(X)):
    comp.setdefault(fnd(i), []).append(i)
lr = [v for v in comp.values() if len(v) == 18]
assert len(lr) == 6, [len(v) for v in comp.values()]
cage_only = loader.copy()
knob = loader[max(comp.values(), key=len)].mean(0)
for v in lr:
    cage_only[v] = knob                             # collapsed, the mesh's own way of hiding
rounds_only = loader.copy()
inr = set(i for v in lr for i in v)
rc = loader[lr[0]].mean(0)
for i in range(len(loader)):
    if i not in inr:
        rounds_only[i] = rc

# --- table values (cm, F L U, the controller's frame)
LF = flu(loader)
rear = np.mean([LF[v][:, 0].min() for v in lr])
for k in range(6):
    q = flu(rounds[k]); ax = np.linalg.svd(q - q.mean(0))[2][0]; ax *= np.sign(ax[0])
    dF = rear - q[:, 0].min()                       # cm along F; move along the round's own axis
    dm = (flu(rounds[k][:1] + np.array([[1e-3, 0, 0]])) - flu(rounds[k][:1]))[0] / 1e-3   # cm per mesh x
    vm = np.linalg.lstsq(np.vstack([(flu(rounds[k][:1] + e[None] * 1e-3) - flu(rounds[k][:1]))[0] / 1e-3 for e in np.eye(3)]).T, ax * dF / ax[0], rcond=None)[0]
    rounds[k] = rounds[k] + vm
RF = [flu(r) for r in rounds]
lrF = np.vstack([LF[v] for v in lr])                # the loader's rounds, seated
axis = np.linalg.svd(lrF - lrF.mean(0))[2][0]; axis *= np.sign(axis[0])
cen = lrF.mean(0)
cyl = flu(M(1, 0))
tip = cen + axis * (lrF[:, 0].max() - cen[0]) / axis[0]
base = cen + axis * (LF[:, 0].min() - cen[0]) / axis[0]
depth = lrF[:, 0].max() - cyl[:, 0].min()
print('hinge (frame 26) %s, axis +L, open %.1f deg' % (np.round(H, 4), ang))
print('cylinder F %.2f..%.2f' % (cyl[:, 0].min(), cyl[:, 0].max()))
print('loader seat: base %s tip %s bore %s depth %.4f' % (np.round(base, 4), np.round(tip, 4), np.round(axis, 4), depth))
print('loader centre (whole) %s, its rounds rear F %.4f' % (np.round(LF.mean(0), 4), rear))
for k, r in enumerate(RF):
    c = r.mean(0); ax = np.linalg.svd(r - c)[2][0]; ax *= np.sign(ax[0])
    b_ = c + ax * (r[:, 0].min() - c[0]) / ax[0]; t_ = c + ax * (r[:, 0].max() - c[0]) / ax[0]
    print('round %d (surface %d): base %s tip %s bore %s' % (k, k + 4, np.round(b_, 4), np.round(t_, 4), np.round(ax, 4)))
print('casing ring centre %s' % np.round(np.mean([r.mean(0) for r in RF], 0), 4))
# world blocks: Offset = -s * centre (x, y), ZOffset = -s * z / 1.2 (MODELDEF.rsb's own Revolver round)
sw = 1.35 * 0.3468
for nm, pts in (('round', rounds[0]), ('loader', loader), ('cage', cage_only)):
    c = pts.mean(0)
    print('world %s: Scale %.4f  Offset %.4f %.4f  ZOffset %.4f' % (nm, sw, -sw * c[0], -sw * c[1], -sw * c[2] / 1.2))
# muzzle: surface 3 (barrel and top strap), the frontmost ring
b3 = flu(M(3, 0)); fm = b3[:, 0].max(); ring = b3[b3[:, 0] > fm - 0.3]
print('muzzle: F %.2f, ring centre L %.2f U %.2f (%d verts, L %.2f..%.2f U %.2f..%.2f)' % (
    fm, ring[:, 1].mean(), ring[:, 2].mean(), len(ring), ring[:, 1].min(), ring[:, 1].max(), ring[:, 2].min(), ring[:, 2].max()))


# --- write rev_rsb.md3
def dec(n):
    lat, lng = (n >> 8) & 255, n & 255
    lat *= 2 * np.pi / 255; lng *= 2 * np.pi / 255
    return np.array([np.cos(lat) * np.sin(lng), np.sin(lat) * np.sin(lng), np.cos(lng)])


def enc(v):
    v = v / (np.linalg.norm(v) or 1)
    if abs(v[0]) < 1e-9 and abs(v[1]) < 1e-9:
        return 0 if v[2] > 0 else 128
    lat = int(round(np.arctan2(v[1], v[0]) * 255 / (2 * np.pi))) & 255
    lng = int(round(np.arccos(np.clip(v[2], -1, 1)) * 255 / (2 * np.pi))) & 255
    return (lat << 8) | lng


d = bytearray(open(SRC, 'rb').read())
nfr, ntag, nsurf, nskin, ofr, otag, osurf, oeof = struct.unpack_from('<8i', d, 76)
moved = {i + 4: (rounds[i], A20) for i in range(6)}
off = osurf
for s in range(nsurf):
    flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
    f0 = [struct.unpack_from('<3hH', d, off + oxyz + v * 8) for v in range(nv)]
    for fr in (1, 2, 3):
        base_ = off + oxyz + fr * nv * 8
        for v in range(nv):
            x, y, z, n = f0[v]
            if s in moved or s == 10:
                if s == 10:
                    P = (loader if fr == 1 else cage_only if fr == 2 else rounds_only)[v]; A = A26
                    src = struct.unpack_from('<3hH', d, off + oxyz + 26 * nv * 8 + v * 8)
                else:
                    P = moved[s][0][v]; A = moved[s][1]
                    src = struct.unpack_from('<3hH', d, off + oxyz + 20 * nv * 8 + v * 8)
                x, y, z = (np.round(P * 64)).astype(int)
                n = enc(dec(src[3]) @ A)
            struct.pack_into('<3hH', d, base_ + v * 8, x, y, z, n)
    off += oend
open(OUT, 'wb').write(d)
print('wrote', OUT)
