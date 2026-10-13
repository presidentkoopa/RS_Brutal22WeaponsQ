"""Chainsaw: right hand on the rear handle (Ermac's chainsaw grip, 29), left hand
overhand on the top bar of the front arch (Ermac's fist 91 turned so the bar runs
across it, thumb toward the body's middle, palm down)."""
import sys, json, numpy as np
import vplus, guns
sys.path.insert(0, vplus.H)
import align, ermac, support
import minigun_fit
ermac.SETS['chainsaw'] = ('chainsaw/chainsaw.md3', 0, 29, 14, 29)
OUT = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/vplus/'
# gun hand: the tube Ermac's chainsaw hand (29) closes round runs forward and up at
# about 38 degrees; this saw's rear handle tube runs straight back. Turn the hand
# about its left axis so the two tubes line up, and put the held part of Ermac's
# tube on the middle of this one.
gE1, hE1 = align.ermac_points('chainsaw', 1)
p1 = align.held_patch(gE1, hE1, r=2.5)
c1 = p1.mean(0); w1, v1 = np.linalg.eigh(np.cov((p1 - c1).T)); a1 = v1[:, -1] * np.sign(v1[0, -1])
pts0 = align.surface_points(guns.item('Vanilla_Chainsaw'))
tube = align.box(pts0, f=(-8, 6), l=(-2.5, 2.5), u=(-3, 3))
c2 = tube.mean(0); w2, v2 = np.linalg.eigh(np.cov((tube - c2).T)); a2 = v2[:, -1] * np.sign(v2[0, -1])
Rg = minigun_fit.frame(a2, (0, 1, 0)) @ minigun_fit.frame(a1, (0, 1, 0)).T
ghook, grot = minigun_fit.rot_hook(c1, c2, Rg)
print('gun hand: ermac tube', c1.round(2), a1.round(2), '-> rear tube', c2.round(2), a2.round(2), 'hook', ghook, 'rot', grot)
t = c2 - c1; err = 0.0
# Ermac's vertical-grip fist and the grip it holds
gE, hE = align.ermac_points('plasma', 2)
patch = align.held_patch(gE, hE)
c = np.array([25.0, -1.5, -5.2])   # the slot inside the fist (cross-sections at U -6..-8)
w, v = np.linalg.eigh(np.cov((patch - c).T)); ax = v[:, -1]
print('fist grip centre', c.round(2), 'axis', ax.round(2))
# the top bar of the front arch
pts = align.surface_points(guns.item('Vanilla_Chainsaw'))
bar = align.box(pts, f=(30, 40), l=(-1, 10), u=(23.5, 27.5))
tb = bar.mean(0)
w2, v2 = np.linalg.eigh(np.cov((bar - tb).T)); bax = v2[:, -1]
print('bar centre', tb.round(2), 'axis', bax.round(2), 'n', len(bar))
Rw = minigun_fit.frame((0, 1, 0), (1, 0, 0.25)) @ minigun_fit.frame((0, 0, -1), (1, 0, 0)).T
hook, ypr = minigun_fit.rot_hook(c, tb, Rw)
print('support hook', hook, 'rot', ypr)
f = json.load(open(OUT + 'vfits.json'))
f['Vanilla_Chainsaw'] = {'gun_set': 'chainsaw', 'gun_shift': t.round(2).tolist(), 'gun_hook': ghook, 'gun_rot': grot,
                         'sup_set': 'plasma', 'where': ['handlebar'], 'sup_hook': hook, 'sup_rot': ypr,
                         'target': tb.round(2).tolist()}
json.dump(f, open(OUT + 'vfits.json', 'w'), indent=1)
