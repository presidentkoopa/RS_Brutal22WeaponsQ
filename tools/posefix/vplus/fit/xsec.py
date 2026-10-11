"""Horizontal cross-sections (plane U = u) of gun and hands, drawn in F-L: is the grip inside the hand?"""
import sys, numpy as np
import vplus, guns
sys.path.insert(0, vplus.H)
import gunview, hudrender
from PIL import Image, ImageDraw
def segs(it, u, axis=2):
    out = []
    for tris, raw in gunview.item_mesh(it):
        v = gunview.to_fl(hudrender.to_local(np.asarray(raw, float), it))
        a, b, c = v[tris[:, 0]], v[tris[:, 1]], v[tris[:, 2]]
        da, db, dc = a[:, axis] - u, b[:, axis] - u, c[:, axis] - u
        for i in range(len(a)):
            pts = []
            for p, q, dp, dq in ((a[i], b[i], da[i], db[i]), (b[i], c[i], db[i], dc[i]), (c[i], a[i], dc[i], da[i])):
                if dp * dq < 0:
                    w = dp / (dp - dq); pts.append(p + (q - p) * w)
            if len(pts) == 2: out.append(pts)
    return out
def draw(items, us, out, rng, px=12, axis=2):
    f0, f1, l0, l1 = rng
    ims = []
    hv = {2: (0, 1), 0: (1, 2), 1: (0, 2)}[axis]
    for u in us:
        W, H = int((f1 - f0) * px), int((l1 - l0) * px) + 16
        im = Image.new('RGB', (W, H), (40, 42, 52)); d = ImageDraw.Draw(im)
        for g in range(int(f0), int(f1) + 1):
            if g % 5 == 0: d.line([((g - f0) * px, 16), ((g - f0) * px, H)], fill=(70, 72, 90))
        for g in range(int(l0), int(l1) + 1):
            if g % 5 == 0: d.line([(0, H - (g - l0) * px), (W, H - (g - l0) * px)], fill=(70, 72, 90))
        for it in items:
            col = tuple(it.get('color', (200, 200, 200)))
            for p, q in segs(it, u, axis):
                d.line([((p[hv[0]] - f0) * px, H - (p[hv[1]] - l0) * px), ((q[hv[0]] - f0) * px, H - (q[hv[1]] - l0) * px)], fill=col, width=2)
        d.text((3, 2), '%s = %.1f   (%s right, %s up)' % ('FLU'[axis], u, 'FLU'[hv[0]], 'FLU'[hv[1]]), fill=(255, 255, 255))
        ims.append(im)
    W = sum(i.width for i in ims) + 6 * len(ims); H = max(i.height for i in ims)
    O = Image.new('RGB', (W, H)); x = 0
    for i in ims: O.paste(i, (x, 0)); x += i.width + 6
    O.save(out)
