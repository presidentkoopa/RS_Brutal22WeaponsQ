import sys, numpy as np
import vplus, guns
sys.path.insert(0, vplus.H)
import align, ermac, gunview
from PIL import Image
OUT = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/vplus/out/'
cls = sys.argv[1]; sets = sys.argv[2].split(','); rng = tuple(float(x) for x in sys.argv[3].split(','))
ims = []
for s in sets:
    t, err, _ = align.fit(cls, s, 1, dict(f=(-22, 6), l=(-5, 5), u=(-24, -1)))
    t = t + np.array([0, 0, -1.5])
    it = guns.item(cls); it['color'] = [150, 155, 170]
    g, gf, h1, h2, h1one = ermac.SETS[s]
    h = dict(path=ermac.E + 'hand/hand.md3', frame=h1, hook=align.hook_from_shift(t), color=[225, 170, 135], **ermac.PL)
    p = OUT + 'g_%s.png' % s
    gunview.view([it, h], p, 'side', px=10, rng=rng, title='%s %s err %.2f shift %s' % (cls, s, err, t.round(1)))
    ims.append(Image.open(p)); print(s, err, t.round(2))
W = max(i.width for i in ims); H = sum(i.height for i in ims)
O = Image.new('RGB', (W, H)); y = 0
for i in ims: O.paste(i, (0, y)); y += i.height
O.save(OUT + 'grip_%s.png' % cls)
