import sys, json
import numpy as np
import vplus, guns
sys.path.insert(0, vplus.H)
import align, handfit, ermac, gunview, hudrender
from PIL import Image
OUT = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/vplus/out/'
RNG = {'VR_Revolver': ((-15, 35, -20, 15), (-15, 35, -12, 12)), 'VR_Shotgun': ((-35, 60, -18, 15), (-35, 60, -12, 12)),
       'VR_SuperShotgun': ((-35, 50, -18, 15), (-35, 50, -12, 12)), 'VR_Rifle': ((-35, 60, -22, 15), (-35, 60, -12, 12))}
def items_for(r, two=True):
    g, gf, h1, h2, h1one = ermac.SETS[r['gun_set']]
    if 'gun_hook' in r:
        out = [dict(path=ermac.E + 'hand/hand.md3', frame=h1 if two else h1one,
                    hook=r['gun_hook'], rot=r['gun_rot'], color=[225, 170, 135], **ermac.PL)]
    else:
        out = [dict(path=ermac.E + 'hand/hand.md3', frame=h1 if two else h1one,
                    hook=align.hook_from_shift(r['gun_shift']), color=[225, 170, 135], **ermac.PL)]
    if two:
        sg, sgf, sh1, sh2, _ = ermac.SETS[r['sup_set']]
        sframe = 91 if r['where'][0] in ('handlebar', 'handle') else sh2
        if 'sup_hook' in r:
            out.append(dict(path=ermac.E + 'hand/hand2.md3', frame=sframe, hook=r['sup_hook'], rot=r['sup_rot'],
                            color=[120, 200, 140], **ermac.PL))
        else:
            out.append(dict(path=ermac.E + 'hand/hand2.md3', frame=sframe, hook=align.hook_from_shift(r['sup_shift']),
                            color=[120, 200, 140], **ermac.PL))
    return out
def sheet(c, r, out):
    it = guns.item(c); it['color'] = [150, 155, 170]
    hs = items_for(r)
    a, b, cc = OUT + 'ta.png', OUT + 'tb.png', OUT + 'tc.png'
    r1, r2 = RNG.get(c, (None, None))
    mk = [tuple(r['target']) + ('S', (255, 255, 0))]
    gunview.view([it] + hs, a, 'side', px=5, rng=r1, marks=mk, title=c)
    gunview.view([it] + hs, b, 'bottom', px=5, rng=r2, marks=mk, title=c)
    hudrender.render([it] + hs, cc, eye=[-0.22, 0.20, 0.32], look=[0, -0.04, -0.2], W=460, H=330, fov=60, title=c + ' (player)')
    A, B, C = Image.open(a), Image.open(b), Image.open(cc)
    W = max(A.width, B.width) + C.width + 10; H = max(A.height + B.height, C.height)
    O = Image.new('RGB', (W, H)); O.paste(A, (0, 0)); O.paste(B, (0, A.height)); O.paste(C, (max(A.width, B.width) + 10, 0)); O.save(out)
if __name__ == '__main__':
    f = json.load(open(OUT + '../vfits.json'))
    for c in (sys.argv[1:] or f):
        sheet(c, f[c], OUT + 'fit_%s.png' % c); print(c)
