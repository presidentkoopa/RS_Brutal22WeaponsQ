"""Unmaker: carry RS VR Weapons Vanilla Plus's skull reload row into BD22's drawn space.

Usage: python3 plus_row.py <plus unmaker_wm.md3> <bd22 Unmaker_rsr.md3> [plus_rsr_guns.zs] [depot tools/kit]

1. Vertex correspondence, matched by POSITION (nearest neighbour, not index): BD22's frame 0
   (the frame the gun and the reload draw, RQWM/RQWP A 0 0) = Plus's mesh + one translation
   in md3 units. Prints the translation, the scale fit and the residual.
2. The same correspondence in the weapon controller's frame (F L U cm, rgeo.to_flu: the
   QZD 17.3 HUD-model chain): d = BD22 drawn - Plus drawn, for both MODELDEF placements.
3. Plus's row (WM_VP_Unmaker, index 1 of the Plus pack's RSR_Guns) through d:
   Well, MagCentre: + d (the seat moves with the gun); Axis, Mouth, MagLen: unchanged (the travel);
   TopInHand: unchanged (the hand frame is the same Ermac RsrHold, RQHN I, ammo_hand.md3 frame 3,
   byte-identical in both packs), so the skull is drawn in the hand exactly where Plus draws it;
   HandHook = shift_hook(scale, TopInHand - Well_bd).
Every number comes from the two meshes, the two MODELDEF placements and Plus's parsed table.
"""
import sys, re
import numpy as np

PLUS, BD = sys.argv[1], sys.argv[2]
ZS = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/rsq_weapondepot/sets/plus_0.7/src/zscript/rsr/rsr_guns.zs'
KIT = sys.argv[4] if len(sys.argv) > 4 else '/home/claude/rsq_weapondepot/tools/kit'
sys.path.insert(0, KIT)
import rgeo
from scipy.spatial import cKDTree

# MODELDEF placements (Scale, (Offset x, y, ZOffset)), parsed by hand from the two MODELDEF.rsr blocks:
# Plus  WM_VP_Unmaker: Scale -1 1 1, Offset -0.0092 -53.6292 0, ZOffset -3.4367 (= its RSR_Guns Offset row 1)
# BD22  Unmaker:       Scale -1 1 1, Offset 0 0 0, ZOffset -5 (= MODELDEF.bd.txt and its RSR_Guns row 13)
P_SC, P_OFF = (-1.0, 1.0, 1.0), (-0.0092, -53.6292, -3.4367)
B_SC, B_OFF = (-1.0, 1.0, 1.0), (0.0, 0.0, -5.0)

mp, mb = rgeo.load_md3(PLUS), rgeo.load_md3(BD)
print('plus surfaces', [(s['name'], s['xyz'].shape[1]) for s in mp])
print('bd22 surfaces', [(s['name'], s['xyz'].shape[1]) for s in mb], 'frames', mb[0]['xyz'].shape[0])
A = np.vstack([s['xyz'][0] for s in mp])
B = np.vstack([s['xyz'][0] for s in mb])
t = B.mean(0) - A.mean(0)
# position match: every BD22 vertex to its nearest Plus vertex after the translation
dist, idx = cKDTree(A + t).query(B)
print('md3 translation (plus -> bd22): %.4f %.4f %.4f units' % tuple(t))
print('position match: max %.4f, mean %.5f units; index-identical: %s' % (dist.max(), dist.mean(), bool((idx == np.arange(len(B))).all()) or 'no: %d seam duplicates matched a twin at the same position' % (idx != np.arange(len(B))).sum()))
Ac, Bc = A - A.mean(0), B[idx * 0 + np.arange(len(B))] - B.mean(0)
s = (Ac * Bc).sum() / (Ac * Ac).sum()
print('scale fit %.6f' % s)

fp = rgeo.to_flu(A, P_SC, P_OFF)
fb = rgeo.to_flu(B, B_SC, B_OFF)
dd = fb - fp
d = dd.mean(0)
print('drawn-space translation d (F L U cm): %.3f %.3f %.3f  (spread %.4f cm)' % (tuple(d) + (np.abs(dd - d).max(),)))


def row(name, idx_):
    txt = open(ZS).read()
    m = re.search(r'static \w+ %s\(int i\)\s*\{(.*?)\n\t\}' % name, txt, re.S)
    c = re.search(r'case %d:\s*return \(?([^;]*?)\)?;' % idx_, m.group(1))
    v = [float(x) for x in c.group(1).split(',')]
    return np.array(v) if len(v) > 1 else v[0]


I = 1   # WM_VP_Unmaker in the Plus pack's RSR_Guns
well, axis, mouth, mlen = row('Well', I), row('Axis', I), row('Mouth', I), row('MagLen', I)
cen, top, hook = row('MagCentre', I), row('TopInHand', I), row('HandHook', I)
assert np.allclose(rgeo.shift_hook(P_SC, top - well), hook, atol=2e-3), 'Plus HandHook is not shift_hook(TopInHand - Well)'
# the skull in Plus's hand (F L U cm, off-hand frame) and in the gun
skull = np.vstack([mp[1]['xyz'][0], mp[2]['xyz'][0]])
sk_gun = rgeo.to_flu(skull, P_SC, P_OFF)
sk_hand = sk_gun + (top - well)
w2, c2 = well + d, cen + d
hook2 = rgeo.shift_hook(B_SC, top - w2)
# check through BD22's own mesh: its skull surfaces 1+2, drawn with the new hook, land on Plus's skull in the hand
skb = np.vstack([mb[1]['xyz'][0], mb[2]['xyz'][0]])
skb_hand = rgeo.to_flu(skb, B_SC, B_OFF, hook=hook2)
print('check: BD22 skull in hand vs Plus skull in hand: max %.4f cm' % np.abs(skb_hand - sk_hand).max())
skb_gun = rgeo.to_flu(skb, B_SC, B_OFF)
print('check: BD22 skull seated vs Plus seat + d: max %.4f cm' % np.abs(skb_gun - (sk_gun + d)).max())
f = lambda v: '(%.3f, %.3f, %.3f)' % tuple(v)
print('\nBD22 row 13 (Unmaker), from Plus row 1 through d:')
print('Well      %s\nAxis      %s\nMouth     %.2f\nMagLen    %.2f\nMagCentre %s\nTopInHand %s\nHandHook  %s' % (
    f(w2), f(axis), mouth, mlen, f(c2), f(top), f(hook2)))
print('skull in hand centre (F L U cm) %s, seated centre %s' % (f(sk_hand.mean(0)), f(skb_gun.mean(0))))
