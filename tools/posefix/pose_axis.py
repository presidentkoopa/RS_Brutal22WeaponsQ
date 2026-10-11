"""Per frame: centroid and principal (barrel) axis pitch/yaw of the whole mesh."""
import sys, numpy as np
sys.path.insert(0, '.')
from md3render import load
nfr, surfs = load(sys.argv[1])
for f in range(nfr):
    v = np.concatenate([xyz[f] for _, xyz in surfs])
    c = v.mean(0)
    u, s, vt = np.linalg.svd(v - c, full_matrices=False)
    a = vt[0]
    if a[0] < 0: a = -a
    pitch = np.degrees(np.arctan2(a[2], np.hypot(a[0], a[1])))
    yaw = np.degrees(np.arctan2(a[1], a[0]))
    print('%2d  centroid %7.2f %7.2f %7.2f   pitch %6.1f yaw %6.1f  min z %6.1f' % (f, c[0], c[1], c[2], pitch, yaw, v[:, 2].min()))
