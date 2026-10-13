import numpy as np
from rgeo import *
from rview import view
V='/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/guns/m16.md3'
O='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/team/reload/tools/'
m = load_md3(V)
sc, off = (1.35, 1.35, 1.35), (0, 0, 0)
np.set_printoptions(precision=2, suppress=True)
mov = np.load(O+'_moving.npy')
b0 = m[0]['xyz'][0]
keep = np.setdiff1d(np.arange(len(b0)), mov)
for f in (0, 35, 36, 37, 38, 39, 40, 11, 21, 30, 34):
    d = m[0]['xyz'][f][keep] - b0[keep]
    h = m[0]['xyz'][f][mov] - b0[mov]
    print('f%d body abs move max %.3f  handle move' % (f, np.abs(d).max()), h.mean(0))
for si, s in enumerate(m):
    p = surf_flu(m, si, 0, sc, off)
    print(si, s['name'], 'c', p.mean(0), 'min', p.min(0), 'max', p.max(0))
hp = to_flu(m[0]['xyz'][0][mov], sc, off)
print('handle verts FLU c', hp.mean(0), 'min', hp.min(0), 'max', hp.max(0))
for f in (21, 27, 30, 32, 33, 34, 0):
    print('mag f%d' % f, surf_flu(m, 3, f, sc, off).mean(0))
cols=[(190,190,180),(255,220,60),(120,200,255),(90,230,120)]
for fr in (0, 37):
    parts=[(surf_flu(m, i, fr, sc, off), s['tris'], cols[i]) for i, s in enumerate(m)]
    hv = to_flu(m[0]['xyz'][fr][mov], sc, off)
    view(parts, O+'m16_side_f%d.png'%fr, 'side', rng=(-20,90,-30,20), px=7, title='V+ M16 f%d (mag green, casing yellow)'%fr,
         marks=[(hv[:,0].mean(), hv[:,1].mean(), hv[:,2].mean(), 'handle', (255,80,80))])
parts=[(surf_flu(m, i, 0, sc, off), s['tris'], cols[i]) for i, s in enumerate(m)]
view(parts, O+'m16_top.png', 'top', rng=(-20,90,-10,10), px=7, title='V+ M16 top', marks=[(hp[:,0].mean(), hp[:,1].mean(), hp[:,2].mean(), 'handle', (255,80,80))])
