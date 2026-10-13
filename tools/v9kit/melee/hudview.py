"""Plot HUD models in the controller's local frame (QZD RenderHUDModel chain).
local: x right, y up, z back (toward the player); metres.
"""
import sys, math, struct
sys.path.insert(0, __import__('os').path.dirname(__file__))
from handframe import frames
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def local(path, frame, scale=(1,1,1), off=(0,0,0), hook=(0,0,0), ws=1.02, surf=None):
    F = frames(path)[frame]
    V = np.array([(x, y, z) for s, x, y, z in F if surf is None or s in surf])
    xs, ys, zs = scale                    # MODELDEF Scale x y z (file axes)
    r = np.stack([V[:,0], V[:,2], V[:,1]], 1) * ws        # render (fx, fz, fy)
    p = np.stack([r[:,2], r[:,1], -r[:,0]], 1)            # Ry(90): (z, y, -x)
    p = p + np.array(hook)
    S = np.array([xs, zs, ys])                            # scale(xs, zs, ys)
    xo, yo, zo = off                                      # MODELDEF Offset x y z(=ZOffset)
    p = p * S + np.array([xo, zo, yo])
    return 0.01 * (p + np.array([0, 5, 30]))

if __name__ == '__main__':
    import json
    items = json.loads(sys.argv[2])
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    cols = ['tab:gray', 'tab:red', 'tab:blue', 'tab:green', 'tab:orange']
    for i, it in enumerate(items):
        P = local(it['path'], it['frame'], tuple(it.get('scale', (1,1,1))), tuple(it.get('off', (0,0,0))), tuple(it.get('hook', (0,0,0))))
        step = max(1, len(P)//4000)
        P = P[::step]
        c = cols[i % len(cols)]
        ax[0].scatter(-P[:,2], P[:,1], s=0.3, c=c)   # side: forward (-z) right, up
        ax[1].scatter(P[:,0], P[:,1], s=0.3, c=c)    # front (from behind): right, up
        ax[2].scatter(P[:,0], -P[:,2], s=0.3, c=c)   # top: right, forward
    for a, t in zip(ax, ['side: fwd -> , up', 'from behind: right ->, up', 'top: right ->, fwd ^']):
        a.set_title(t); a.set_aspect('equal'); a.grid(True); a.axhline(0, c='k', lw=0.5); a.axvline(0, c='k', lw=0.5)
    plt.savefig(sys.argv[1], dpi=80)
