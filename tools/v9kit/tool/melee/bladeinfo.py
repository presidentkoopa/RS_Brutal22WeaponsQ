"""Axe head / sword blade position relative to the controller (metres), from the held pose."""
import sys, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from handframe import frames, to_hand
import numpy as np

def analyse(path, f, label):
    F = frames(path)[f]
    surfs = sorted(set(s for s, *_ in F))
    allp = np.array([to_hand(x, y, z) for s, x, y, z in F])
    print(label, 'frame', f, 'verts', len(allp))
    for s in surfs:
        P = np.array([to_hand(x, y, z) for ss, x, y, z in F if ss == s])
        print('  surf %d n=%d min %s max %s centroid %s' % (s, len(P), P.min(0).round(3), P.max(0).round(3), P.mean(0).round(3)))
    # principal axis of whole model
    c = allp.mean(0)
    u, sv, vt = np.linalg.svd(allp - c, full_matrices=False)
    ax = vt[0]
    t = (allp - c) @ ax
    if ax @ (allp[t.argmax()] - c) < 0: ax = -ax
    t = (allp - c) @ ax
    print('  axis', ax.round(3), 'from', (c + ax * t.min()).round(3), 'to', (c + ax * t.max()).round(3), 'len', round(t.max() - t.min(), 3))
    # distance of points from the axis along length: slices
    for q in np.linspace(t.min(), t.max(), 9):
        sel = np.abs(t - q) < (t.max() - t.min()) / 16
        if sel.sum() == 0: continue
        sl = allp[sel]
        off = (sl - c) - np.outer((sl - c) @ ax, ax)
        print('   at %.2f: n=%4d width %.3f  mean %s' % (q, sel.sum(), np.linalg.norm(off, axis=1).max(), sl.mean(0).round(3)))

if __name__ == '__main__':
    # python bladeinfo.py BrutalAxe.md3 DSweap.md3   (the meshes as shipped in the pk3)
    analyse(sys.argv[1], 5, 'AXE ready (AXEG A)')
    analyse(sys.argv[2], 0, 'DS ready (DSLA A)')
