import numpy as np, sys
from rgeo import *
S='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
m = load_md3(S+'/team/reload_survey/_v8x/models/bd/Rifle/Rifle.md3')
sc, off = (-1, 1, 1), (0, 0, -5)
np.set_printoptions(precision=2, suppress=True)
for si, s in enumerate(m):
    p = surf_flu(m, si, 3, sc, off)
    print(si, s['name'][:10], 'c', p.mean(0), 'min', p.min(0), 'max', p.max(0))
# magazine insertion: frames 12,13,14 -> 15 (seated); axis in FLU
lip = 3
for f in (9, 10, 11, 12, 13, 14, 15):
    print('lipas f%d' % f, surf_flu(m, lip, f, sc, off).mean(0), ' body', surf_flu(m, 4, f, sc, off).mean(0))
