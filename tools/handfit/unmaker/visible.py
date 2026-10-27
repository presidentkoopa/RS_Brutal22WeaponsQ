"""How much of the skull the player SEES while it is carried (owner: visible in the hand, never hidden).
Renders Ermac's hand frame + the skull from the player's eye with the Depot kit's hudrender (painter's
order, the RenderHUDModel chain) and counts skull pixels with the hand drawn vs without it. Searches small
moves of the frame-6 fit (skull_hold.py) for the most visible skull that still TOUCHES the fingers
(nearest hand vertex <= 0.6 cm, hand vertices inside the skull <= 40).
python3 visible.py frame fx fy fz   (fit shift F L U cm from skull_hold.py)"""
import sys, numpy as np, itertools
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/kit'); sys.path.insert(0, __import__('os').path.dirname(__file__))
import hudrender
from rgeo import shift_hook, load_md3, to_flu
from scipy.spatial import cKDTree
SRC = '/home/claude/lane_b_unm/src/'
U = SRC + 'models/bd/Unmaker/Unmaker_rsr.md3'
_load = hudrender.load
hudrender.load = lambda p: _load(p)[1:] if p == U else _load(p)
fr = int(sys.argv[1]); base = np.array([float(x) for x in sys.argv[2:5]])
# The engine draws the OFF hand mirrored in x (left hand = the right-hand mesh mirrored: on the rig the
# knuckles face the player's left, where hudrender shows the palm), and the head is on the hand's
# inner side, so the player's eyes sit at mesh-local -x: above-behind, above-inside, inside.
EYES = [((-0.06, 0.30, 0.40), (0, 0, 0)), ((-0.20, 0.30, 0.35), (0, 0, 0)), ((-0.30, 0.15, 0.20), (0, 0, 0))]
import skull_hold as sh
hv, ht = sh.tris(sh.H, [0], fr, *sh.HPL)
htree = cKDTree(hv)
def vis(hook):
    out = []
    for eye, look in EYES:
        items = [dict(path=SRC + 'models/rsq/ammo_hand.md3', frame=fr, scale=(-1, 1, 1), off=(0, -24, -10), color=(0, 0, 255)),
                 dict(path=U, frame=0, scale=(-1, 1, 1), off=(0, 0, -5), hook=hook, color=(255, 0, 0))]
        hudrender.render(items, '/tmp/_v1.png', eye=eye, look=look, W=160, H=120, fov=60)
        hudrender.render(items[1:], '/tmp/_v2.png', eye=eye, look=look, W=160, H=120, fov=60)
        a = np.asarray(__import__('PIL.Image').Image.open('/tmp/_v1.png')).astype(int)
        b = np.asarray(__import__('PIL.Image').Image.open('/tmp/_v2.png')).astype(int)
        red = lambda im: ((im[:, :, 0] > 60) & (im[:, :, 2] < 40)).sum()
        out.append(red(a) / max(1, red(b)))
    return out
best = None
for d in itertools.product((0, 2, 4), (0, 2, 4, 6), (-2, 0, 2, 4)):
    t = base + np.array(d, float)
    gap = htree.query(sh.SS + t)[0].min()
    hin, bur = sh.score(fr, t)
    if gap > 0.6 or hin > 40:
        continue
    v = vis(shift_hook((-1, 1, 1), t))
    s = min(v)
    print('d %s gap %.2f hin %d buried %.0f%% visible %s' % (d, gap, hin, 100 * bur, ['%.0f%%' % (100 * x) for x in v]), flush=True)
    if best is None or s > best[0]:
        best = (s, d, t, v)
s, d, t, v = best
print('\nBEST d %s: shift %s  TopInHand %s  HandHook %s  visible %s' % (d, np.round(t, 3), np.round(sh.WELL + t, 3),
      np.round(shift_hook((-1, 1, 1), t), 3), ['%.0f%%' % (100 * x) for x in v]))
