"""Measure the Moonlight revolver's 41-frame mesh for the break-open + speedloader reload.

usage: python3 measure_moonlight.py [rev.md3] [depot rev_wm.md3]
Needs the Depot's tools/kit/rgeo.py (the model chain: md3 -> weapon controller frame, cm F L U).
Prints: which surface is what, the frames of each phase, the MODELDEF placement that puts rev.md3
exactly where the Depot hand-fitted rev_wm.md3, the hinge, the opening angle, the chambers, the
cylinder and the speedloader seat. Every number comes off the mesh.
"""
import sys
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/kit')
import numpy as np
from rgeo import load_md3, to_flu

SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/rs_modelswapper/models/vplus/gats/rev.md3'
WM = sys.argv[2] if len(sys.argv) > 2 else \
    '/home/claude/rsq_weapondepot/sets/plus_0.7/src/models/vanilla/revolvers/Revolver/rev_wm.md3'
S = (1.35, 1.35, 1.35)
O_WM = (0.0262, -33.6102, -4.1887)   # Depot sets/plus_0.7 MODELDEF.wmq WM_Moonlight (hand-fitted)

a, b = load_md3(SRC), load_md3(WM)
M = lambda i, f: a[i]['xyz'][f]


def kab(A, B):
    ca, cb = A.mean(0), B.mean(0)
    U, s, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, cb - R @ ca, np.abs((A - ca) @ R.T + cb - B).max()


print('frames', M(0, 0).shape and a[0]['xyz'].shape[0], 'surfaces',
      [(i, s['name'], s['xyz'].shape[1]) for i, s in enumerate(a)])
vis = lambda i, f: np.ptp(M(i, f), 0).max() > 0.01
print('rounds 4-9 visible in frames', [f for f in range(41) if vis(4, f)])
print('surface 10 visible in frames', [f for f in range(41) if vis(10, f)])

# 1. placement: rev_wm.md3 is rev.md3 frame 0 moved rigidly; carry the Depot's fit across
A0 = np.vstack([M(i, 0) for i in range(4)]); B0 = np.vstack([b[i]['xyz'][0] for i in range(4)])
R, t, e = kab(A0, B0)
d = (to_flu(b[0]['xyz'][0], S, O_WM) - to_flu(M(0, 0), S, O_WM)).mean(0)
O = (O_WM[0] - d[1], O_WM[1] - d[0], O_WM[2] + d[2])
print('rev_wm = rev.md3 frame 0 moved by %s mesh units, rotation trace %.4f, residual %.4f'
      % (np.round(t, 2), np.trace(R), e))
print('MODELDEF for rev.md3: Scale 1.35 1.35 1.35  Offset %.4f %.4f  ZOffset %.4f' % O)
P = lambda i, f: to_flu(M(i, f), S, O)

# 2. the hinged part (surfaces 1 and 3) relative to the frame (surface 0), per frame
hinge = None
for f in (17, 18, 19, 20, 22, 26, 30, 31, 33, 36):
    R0, t0, e0 = kab(P(0, 0), P(0, f))
    R3, t3, e3 = kab(P(3, 0), P(3, f))
    Rr, tr = R0.T @ R3, R0.T @ (t3 - t0)
    p = np.linalg.lstsq(np.eye(3) - Rr, tr, rcond=None)[0]
    k = np.argmax(P(3, 0)[:, 0])                    # the muzzle vertex
    tip = R0.T @ (P(3, f)[k] - t0)
    v0 = P(3, 0)[k]
    if f == 26:
        hinge = p
    hp = hinge if hinge is not None else np.array([8.46, 0.0, -1.14])
    ang = np.degrees(np.arctan2(-(tip[2] - hp[2]), tip[0] - hp[0]) - np.arctan2(-(v0[2] - hp[2]), v0[0] - hp[0]))
    print('frame %2d: part turned %5.1f deg barrel-down about +L, axis point %s (fits: frame %.2f part %.2f)'
          % (f, ang, np.round(p, 2) if np.abs(p).max() < 100 else '-', e0, e3))


def to_closed(pts, f):
    R0, t0, _ = kab(P(0, 0), P(0, f))
    R3, t3, _ = kab(P(3, 0), P(3, f))
    return ((pts - t0) @ R0 - R0.T @ (t3 - t0)) @ (R0.T @ R3)


ch = np.array([to_closed(P(i, 20), 20).mean(0) for i in range(4, 10)])
c = ch.mean(0)
print('chambers (frame 20, closed part frame, cm):', np.round(ch, 2).tolist())
print('  their centre %s, radius %s' % (np.round(c, 2), np.round(np.linalg.norm((ch - c)[:, 1:], axis=1), 2)))
cy = P(1, 0)
print('cylinder (surface 1): F %.2f..%.2f, centre %s' % (cy[:, 0].min(), cy[:, 0].max(), np.round(cy.mean(0), 2)))
for f in (25, 26):
    q = to_closed(P(10, f), f); qc = q.mean(0); _, _, vt = np.linalg.svd(q - qc)
    print('speedloader frame %d (closed part frame): centre %s, axis %s, F %.2f..%.2f'
          % (f, np.round(qc, 2), np.round(vt[0], 3), q[:, 0].min(), q[:, 0].max()))
