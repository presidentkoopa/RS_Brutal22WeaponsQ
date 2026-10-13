"""Which vertices of a surface move relative to the rest of it (rigid fit on the
vertices that stay put).  usage: md3parts.py file.md3 surf frame [refframe]"""
import sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from md3rel import load, rigid

path, si, f = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rf = int(sys.argv[4]) if len(sys.argv) > 4 else 0
nfr, surfs = load(path)
name, xyz = surfs[si]
A, B = xyz[f], xyz[rf]
keep = np.ones(len(A), bool)
for it in range(6):
    R, t = rigid(A[keep], B[keep])
    d = np.linalg.norm(A @ R.T + t - B, axis=1)
    keep = d < max(0.3, np.percentile(d, 60))
R, t = rigid(A[keep], B[keep])
dv = A @ R.T + t - B
d = np.linalg.norm(dv, axis=1)
mov = d > 0.5
print('%s surf %d frame %d vs %d: %d of %d verts move' % (name, si, f, rf, mov.sum(), len(A)))
if mov.any():
    print('  mean move', dv[mov].mean(0).round(2), ' max', d.max().round(2))
    print('  moving verts bbox (ref frame) min', B[mov].min(0).round(2), 'max', B[mov].max(0).round(2))
    print('  whole surf bbox min', B.min(0).round(2), 'max', B.max(0).round(2))
    np.save('/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/team/reload/tools/_moving.npy', np.where(mov)[0])
