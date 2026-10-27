"""Unmaker: put the skull IN Ermac's off hand and VISIBLE (owner, 2026-10-27: never hidden inside the fist).

python3 skull_hold.py [ermac ammo_hand dir] [pack src]
For each of Ermac's ammo_hand holds (frames 0-8, the hands we ship: models/rsq/ammo_hand.md3, drawn by
MODELDEF RSQ_Hands Scale -1 1 1 Offset 0 -24 -10), fit the skull (Unmaker_rsr.md3 surfaces 1+2, frame 0,
the HANDMAG layer's own placement Scale -1 1 1, ZOffset -5) onto the contact patch of HIS part in that
frame, translation only (vreload Place(HANDMAG) adds HandHook only; the skull keeps its seated
orientation). Scored on: contact gap (median, cm), hand vertices inside the skull (penetration) and,
the owner's rule, the share of the skull's surface that is INSIDE the hand mesh (buried = hidden).
Also scores the current rows (lane-b 1.99x, and the Vanilla Plus carry of plus_row.py) the same way.
Prints TopInHand / HandHook for the best visible hold. Every number is from the meshes (rgeo chain).
"""
import sys, numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/kit')
from rgeo import load_md3, to_flu, shift_hook
_A = sys.argv if __name__ == '__main__' else []
E = _A[1] if len(_A) > 1 else '/mnt/user-data/uploads/doom-force-unleashed_devbuild/models/ammo_hand/'
SRC = _A[2] if len(_A) > 2 else '/home/claude/lane_b_unm/src/'
PARTS = ['mag_pistol', 'shot_shell', 'shot_shell2', 'mag_chaingun', 'pod_rocket', 'mag_plasma', 'pod_bfg', 'pod_heat', 'flame_can']
HPL = ((-1, 1, 1), (0, -24, -10))           # RSQ_Hands ammo_hand placement
SC, OFF = (-1, 1, 1), (0, 0, -5)            # Unmaker HANDMAG placement
WELL = np.array([11.026, 0.794, 6.467])      # row 13 Well (plus_row.py), the skull's top seated

def tris(md3, surfs, fr, sc, off):
    V, T, n = [], [], 0
    for s in surfs:
        v = to_flu(md3[s]['xyz'][fr], sc, off); V.append(v); T.append(md3[s]['tris'] + n); n += len(v)
    return np.concatenate(V), np.concatenate(T)

def samples(V, T):
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    out = [V, (a + b + c) / 3]
    for w in (0.2, 0.5, 0.8):
        out += [a * w + b * (1 - w), b * w + c * (1 - w), c * w + a * (1 - w)]
    return np.concatenate(out)

def inside(P, V, T, dirn=np.array([0.577, 0.577, 0.577])):
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    e1 = b - a; e2 = c - a; h = np.cross(dirn, e2); det = (e1 * h).sum(1); ok = np.abs(det) > 1e-9
    a, e1, e2, h, det = a[ok], e1[ok], e2[ok], h[ok], det[ok]; inv = 1 / det
    cnt = np.zeros(len(P), int)
    for k in range(0, len(P), 128):
        p = P[k:k + 128][:, None, :]; s = p - a[None]; u = (s * h[None]).sum(2) * inv
        q = np.cross(s, e1[None]); v = (q * dirn).sum(2) * inv; t = (q * e2[None]).sum(2) * inv
        cnt[k:k + 128] = ((u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)).sum(1)
    return cnt % 2 == 1

H = load_md3(SRC + 'models/rsq/ammo_hand.md3')
U = load_md3(SRC + 'models/bd/Unmaker/Unmaker_rsr.md3')
SV, ST = tris(U, [1, 2], 0, SC, OFF); SS = samples(SV, ST); tree = cKDTree(SS)

def score(frame, t):
    hv, ht = tris(H, [0], frame, *HPL)
    hin = int(inside(hv - t, SV, ST).sum())              # hand vertices inside the skull
    buried = float(inside(SS + t, hv, ht).mean())        # skull surface inside the hand
    return hin, buried

def fit(frame):
    hv, ht = tris(H, [0], frame, *HPL)
    P = load_md3(E + PARTS[frame] + '.md3'); pv, pt = tris(P, range(len(P)), 0, *HPL); ps = samples(pv, pt)
    d, _ = cKDTree(ps).query(hv); C = hv[d < 1.5]
    if len(C) < 20:
        return None
    ext = SS.max(0) - SS.min(0); best = None
    starts = [ps.mean(0) - SS.mean(0)] + [ps.mean(0) - SS.mean(0) + np.eye(3)[ax] * sg * 0.5 * ext[ax] for ax in range(3) for sg in (-1, 1)]
    for t0 in starts:
        t = np.array(t0, float)
        for it in range(60):
            dd, idx = tree.query(C - t); k = np.argsort(dd)[:max(10, int(len(dd) * 0.8))]
            step = -(SS[idx[k]] - (C[k] - t)).mean(0)
            if it % 5 == 4:
                ins = inside(hv - t, SV, ST)
                if ins.any():
                    _, i2 = tree.query(hv[ins] - t); step += -0.5 * ((hv[ins] - t) - SS[i2]).mean(0)
            t += step
            if np.linalg.norm(step) < 1e-3 and it % 5 != 4:
                break
        dd, _ = tree.query(C - t); hin, buried = score(frame, t)
        sc = float(np.median(dd)) + 0.02 * hin + 10.0 * buried       # buried skull = hidden = refused
        if best is None or sc < best[0]:
            best = (sc, t.copy(), float(np.median(dd)), hin, buried)
    return best

def hook_of(t):
    top = WELL + t
    return top, shift_hook(SC, top - WELL)

if __name__ == '__main__':
    for name, top in [('lane-b 1.99x (frame 3)', np.array([-1.481, 4.252, -6.901]) - np.array([11.788, 0.614, 7.329]) + WELL),
                      ('Vanilla Plus row (frame 3)', np.array([-0.155, 4.838, -10.770]))]:
        t = top - WELL
        if name.startswith('lane-b'):        # the old row drew the skull by its own hook: shift = old TopInHand - old Well
            t = np.array([-1.481, 4.252, -6.901]) - np.array([11.788, 0.614, 7.329])
        hin, bur = score(3, t)
        print('%-28s hand verts in skull %4d, skull surface buried in the fist %.0f%%' % (name, hin, 100 * bur))
    rows = []
    for fr in range(9):
        b = fit(fr)
        if b:
            rows.append((b[0], fr, b[1], b[2], b[3], b[4]))
            print('frame %d (%s): gap %.2f cm, hand verts in skull %d, skull buried %.0f%%, shift %s' % (fr, PARTS[fr], b[2], b[3], 100 * b[4], np.round(b[1], 3)), flush=True)
    rows.sort(key=lambda r: r[0])
    sc, fr, t, gap, hin, bur = rows[0]
    top, hook = hook_of(t)
    print('\nBEST frame %d (%s): TopInHand (%.3f, %.3f, %.3f)  HandHook (%.3f, %.3f, %.3f)  gap %.2f cm  buried %.0f%%'
          % ((fr, PARTS[fr]) + tuple(top) + tuple(hook) + (gap, 100 * bur)))
