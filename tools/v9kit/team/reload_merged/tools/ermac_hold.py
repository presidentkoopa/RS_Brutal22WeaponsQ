import numpy as np
from rgeo import *
from rview import view
S='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
O=S+'/team/reload/tools/'
R=S+'/tool/vrmelee/models/rsq/'
np.set_printoptions(precision=2, suppress=True)
hand = load_md3(R+'ammo_hand.md3'); mag = load_md3(R+'mag_chaingun.md3'); hnd = load_md3(R+'hand.md3')
print('ammo_hand frames', hand[0]['xyz'].shape, 'surfs', [s['name'] for s in hand], 'mag surfs', [s['name'] for s in mag], mag[0]['xyz'].shape)
sc, off = (-1, 1, 1), (0, -24, -10)
hp = np.concatenate([surf_flu(hand, i, 3, sc, off) for i in range(len(hand))])
mp = np.concatenate([surf_flu(mag, i, 0, sc, off) for i in range(len(mag))])
print('hand f3 c', hp.mean(0), hp.min(0), hp.max(0))
c, vt, s = pca(mp)
print('ermac mag c', c, 'min', mp.min(0), 'max', mp.max(0)); print(' axes', vt, s)
for fr in range(hand[0]['xyz'].shape[0]):
    p = np.concatenate([surf_flu(hand, i, fr, sc, off) for i in range(len(hand))]); print(' ammo_hand fr', fr, p.mean(0))
for fr in range(hnd[0]['xyz'].shape[0]):
    p = np.concatenate([surf_flu(hnd, i, fr, sc, off) for i in range(len(hnd))]); print(' hand fr', fr, p.mean(0))
parts=[(surf_flu(hand, i, 3, sc, off), s['tris'], (225,170,135)) for i, s in enumerate(hand)]
parts+=[(surf_flu(mag, i, 0, sc, off), s['tris'], (90,230,120)) for i, s in enumerate(mag)]
for k in ('side','front','top'):
    view(parts, O+'ermac_hold_%s.png'%k, k, px=10, title='Ermac ammo_hand 3 + mag_chaingun (off controller frame)')
