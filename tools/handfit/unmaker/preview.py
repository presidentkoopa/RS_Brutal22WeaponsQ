"""Offline preview (Depot kit hudrender.py, the RenderHUDModel chain): Ermac's off hand + the Unmaker skull
at a given HandHook, seen from the player's eye and from the side. python3 preview.py out.png frame hx hy hz [label]"""
import sys, numpy as np
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/kit')
import hudrender
from PIL import Image
SRC = '/home/claude/lane_b_unm/src/'
U = SRC + 'models/bd/Unmaker/Unmaker_rsr.md3'
_load = hudrender.load
hudrender.load = lambda p: _load(p)[1:] if p == U else _load(p)        # the skull = surfaces 1 + 2
out, fr, hook = sys.argv[1], int(sys.argv[2]), [float(x) for x in sys.argv[3:6]]
lab = sys.argv[6] if len(sys.argv) > 6 else ''
items = [dict(path=SRC + 'models/rsq/ammo_hand.md3', frame=fr, scale=(-1, 1, 1), off=(0, -24, -10), color=(60, 60, 64)),
         dict(path=U, frame=0, scale=(-1, 1, 1), off=(0, 0, -5), hook=hook, color=(225, 150, 140))]
ims = []
for k, (eye, look) in enumerate([((0.06, 0.30, 0.40), (0.0, 0.0, 0.0)), ((-0.40, 0.05, 0.02), (0.0, 0.0, 0.0)), ((0.40, 0.05, 0.02), (0.0, 0.0, 0.0))]):
    p = out + '.%d.png' % k
    hudrender.render(items, p, eye=eye, look=look, W=360, H=300, fov=50, title=lab + ['  player eye', '  left side', '  right side'][k])
    ims.append(Image.open(p))
W = Image.new('RGB', (360 * 3, 300))
for k, im in enumerate(ims):
    W.paste(im, (360 * k, 0))
W.save(out)
import os
for k in range(3): os.remove(out + '.%d.png' % k)
