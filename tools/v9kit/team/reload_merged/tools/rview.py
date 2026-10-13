"""Orthographic views of mesh parts in the controller frame (F L U cm), one colour per part."""
import math
import numpy as np
from PIL import Image, ImageDraw
VIEWS = {'side': ((0, 1), (2, 1), (1, -1)), 'bottom': ((0, 1), (1, 1), (2, -1)),
         'front': ((1, -1), (2, 1), (0, 1)), 'top': ((0, 1), (1, -1), (2, 1))}

def view(parts, out, kind='side', rng=None, px=8, marks=(), title=''):
    (hi, hs), (vi, vs), (di, ds) = VIEWS[kind]
    if rng is None:
        allv = np.concatenate([v for v, t, c in parts])
        hv, vv = allv[:, hi] * hs, allv[:, vi] * vs
        rng = (math.floor(hv.min() / 5) * 5 - 5, math.ceil(hv.max() / 5) * 5 + 5,
               math.floor(vv.min() / 5) * 5 - 5, math.ceil(vv.max() / 5) * 5 + 5)
    h0, h1, v0, v1 = rng
    W, H = int((h1 - h0) * px), int((v1 - v0) * px) + 18
    img = Image.new('RGB', (W, H), (60, 62, 78)); dr = ImageDraw.Draw(img)
    P = lambda h, v: ((h - h0) * px, H - (v - v0) * px)
    for g in range(int(h0), int(h1) + 1):
        if g % 5 == 0:
            x = P(g, 0)[0]; dr.line([(x, 18), (x, H)], fill=(95, 98, 120) if g % 10 else (120, 124, 150))
            if g % 10 == 0: dr.text((x + 2, 20), str(g), fill=(170, 170, 190))
    for g in range(int(v0), int(v1) + 1):
        if g % 5 == 0:
            y = P(0, g)[1]; dr.line([(0, y), (W, y)], fill=(95, 98, 120) if g % 10 else (120, 124, 150))
            if g % 10 == 0: dr.text((2, y - 12), str(g), fill=(170, 170, 190))
    L = np.array([0.4, 0.5, 0.75]); L /= np.linalg.norm(L)
    polys = []
    for v, tris, col in parts:
        a, b, c = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        n = np.cross(b - a, c - a); n /= (np.linalg.norm(n, axis=1)[:, None] + 1e-12)
        sh = np.abs(n @ L) * 0.7 + 0.3
        depth = (a[:, di] + b[:, di] + c[:, di]) / 3 * ds
        col = np.array(col, float)
        for i in range(len(a)):
            polys.append((depth[i], [P(p[hi] * hs, p[vi] * vs) for p in (a[i], b[i], c[i])], tuple(int(x) for x in col * sh[i])))
    polys.sort(key=lambda t: t[0])
    for _, pts, c in polys: dr.polygon(pts, fill=c)
    o = P(0, 0); dr.ellipse((o[0] - 4, o[1] - 4, o[0] + 4, o[1] + 4), outline=(255, 255, 0), width=2)
    for f, l, u, lab, col in marks:
        q = (f, l, u); x, y = P(q[hi] * hs, q[vi] * vs)
        dr.ellipse((x - 4, y - 4, x + 4, y + 4), outline=col, width=2); dr.text((x + 6, y - 6), lab, fill=col)
    dr.rectangle((0, 0, W, 17), fill=(30, 30, 40))
    dr.text((4, 3), '%s [%s] cm' % (title, kind), fill=(255, 255, 255))
    img.save(out)
    return rng
