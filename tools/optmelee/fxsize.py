"""MEASURE (2.0.2, owner r3 item 36: the melee hit flash is "way, way too large"). The visible size of each melee hit
flash's art (zscript/rsq/bash.zs RSQ_FX_*): the bounding box, over every frame, of the pixels whose brightest channel x
alpha is above 40 (the effects are drawn additive, so that is what shows), and the map units it covers at a given
Scale. python3 tools/optmelee/fxsize.py [target_map_units]"""
import os, sys, glob
import numpy as np
from PIL import Image
SPR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'sprites')
OLD = {'RSS3': 0.384, 'RSU1': 1.6, 'RSU4': 6.4, 'RSU5': 0.857, 'RSH0': 1.0}	# 1.97 .. 2.0.1 scales
target = float(sys.argv[1]) if len(sys.argv) > 1 else 13.0
for pre, old in OLD.items():
    mx = 0
    for f in sorted(glob.glob(os.path.join(SPR, pre + '*.png'))):
        a = np.asarray(Image.open(f).convert('RGBA')).astype(float)
        lum = a[..., :3].max(-1) * a[..., 3] / 255
        ys, xs = np.where(lum > 40)
        if len(xs):
            mx = max(mx, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    print('%s visible %3d px | 2.0.1 scale %.3f = %5.1f map units | scale for %.0f units: %.4f' % (pre, mx, old, mx * old, target, target / mx))
