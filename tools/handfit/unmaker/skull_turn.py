"""Unmaker: turn the carried skull in the off hand the way RS VR Reload holds it (owner 2026-10-27 19:40:
"clearly visible while carried, like RS VR Reload").

python3 skull_turn.py <pack src> [out.png]

SOURCE (parsed, not typed): RS VR Reload's CVARINFO.txt (E:\\DOOMWork\\RS_VR_Reload, staged read-only at
/mnt/user-data/uploads/DOOMWork/RS_VR_Reload), the Unmaker's hand set `bfg` (zscript/wm/handprofile.zs
AmmoPrefix wm_ha_<profile>_<slot>), slot off_mag: wm_ha_bfg_off_mag_yaw / _pitch / _roll.
CONVENTION (stated, GZDoom's, which DoomXR's placement keeps): yaw positive turns left (F toward L),
pitch positive tips the nose DOWN, roll about the forward axis; applied yaw, then pitch, then roll, in the
off controller's frame (F L U), about the skull's own centre -- RS VR Reload's skull model is re-origined
on its centroid (wm_unmaker_skull.md3, RS_VR_Weapons WMCARD magcenter), so its angles turn it in place.
The skull's centre stays where lb-r8 fitted it (rsr row 13 HandHook, visible.py), so the turn changes how
it faces, not where the hand holds it. Then: the hook rotation + translation for vreload Place(HANDMAG)
(rgeo.solve_hook, the RenderHUDModel chain), hand penetration / burial (skull_hold.py's scores) and the share
of the skull seen from three head positions, before and after (visible.py's measure).
"""
import os, re, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/kit'); sys.path.insert(0, HERE)
SRC = os.path.abspath(sys.argv[1]) + '/'
OUT = sys.argv[2] if len(sys.argv) > 2 else None
sys.argv = [sys.argv[0], '/mnt/user-data/uploads/doom-force-unleashed_devbuild/models/ammo_hand/', SRC]
import skull_hold as sh
import hudrender
from rgeo import solve_hook, shift_hook, to_flu, flu_to_loc, loc_to_flu
from scipy.spatial import cKDTree

RVR = '/mnt/user-data/uploads/DOOMWork/RS_VR_Reload/CVARINFO.txt'
cv = dict(re.findall(r'(wm_ha_bfg_off_mag_(?:yaw|pitch|roll))\s*=\s*(-?[\d.]+)', open(RVR).read()))
YAW, PITCH, ROLL = (float(cv['wm_ha_bfg_off_mag_' + k]) for k in ('yaw', 'pitch', 'roll'))
print('RS VR Reload %s: off_mag yaw %.1f pitch %.1f roll %.1f' % (RVR, YAW, PITCH, ROLL))

def Rz(a):
    c, s = np.cos(np.radians(a)), np.sin(np.radians(a)); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def Ry(a):
    c, s = np.cos(np.radians(a)), np.sin(np.radians(a)); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rx(a):
    c, s = np.cos(np.radians(a)), np.sin(np.radians(a)); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
# F L U: yaw about U (+ = F toward L), pitch about L (+ = nose down: Ry(+) takes F to -U), roll about F
RD = Rz(YAW) @ Ry(PITCH) @ Rx(ROLL)

FR = 6								# Ermac's pod hold (vreload HoldState(13) = RsrHoldPod)
txt = open(SRC + 'zscript/rsr/rsr_guns.bd.zs').read()
def row(fn):
    m = re.search(r'static Vector3 %s\(int i\).*?case 13:\s*return \(([^)]*)\)' % fn, txt, re.S)
    return np.array([float(x) for x in m.group(1).split(',')])
H0 = row('HandHook')
SC, OFF = sh.SC, sh.OFF
t0 = loc_to_flu(H0 * np.array([SC[0], SC[2], SC[1]]))		# shift_hook inverted: the F L U move of the hook
assert np.allclose(shift_hook(SC, t0), H0, atol=1e-6)
SV0 = sh.SV						# skull at hook 0 (F L U cm)
c0 = SV0.mean(0); c1 = c0 + t0
h, ypr = solve_hook(SC, OFF, RD, c0, c1)
P_after = to_flu(sh.U[1]['xyz'][0], SC, OFF, hook=h, ypr=ypr)
P_after = np.vstack([P_after, to_flu(sh.U[2]['xyz'][0], SC, OFF, hook=h, ypr=ypr)])
P_want = (SV0 - c0) @ RD.T + c1
DSHIFT = np.array([float(x) for x in os.environ.get('SKULL_SHIFT', '0 0 0').split()])
if DSHIFT.any():			# the chosen re-seat (the --search result): 'after' below is the turned AND re-seated skull
    h, ypr = solve_hook(SC, OFF, RD, c0, c1 + DSHIFT)
    P_after = np.vstack([to_flu(sh.U[s]['xyz'][0], SC, OFF, hook=h, ypr=ypr) for s in (1, 2)])
    P_want = P_want + DSHIFT
print('HandHook now %s (F L U move %s); skull centre %s' % (np.round(H0, 3), np.round(t0, 3), np.round(c1, 3)))
print('turned: hook translation %s, hook rotation (yaw, pitch, roll) %s; chain check max %.4f cm'
      % (np.round(h, 4), np.round(ypr, 4), np.abs(P_after - P_want).max()))

hv, ht = sh.tris(sh.H, [0], FR, *sh.HPL)
htree = cKDTree(hv)
EYES = [((-0.06, 0.30, 0.40), (0, 0, 0)), ((-0.20, 0.30, 0.35), (0, 0, 0)), ((-0.30, 0.15, 0.20), (0, 0, 0)), ((0.15, 0.25, 0.30), (0, 0, 0))]
U = SRC + 'models/bd/Unmaker/Unmaker_rsr.md3'
_load = hudrender.load
hudrender.load = lambda p: _load(p)[1:] if p == U else _load(p)
def vis(hook, rot):
    out = []
    for eye, look in EYES:
        items = [dict(path=SRC + 'models/rsq/ammo_hand.md3', frame=FR, scale=(-1, 1, 1), off=(0, -24, -10), color=(0, 0, 255)),
                 dict(path=U, frame=0, scale=SC, off=OFF, hook=hook, rot=rot, color=(255, 0, 0))]
        hudrender.render(items, '/tmp/_st1.png', eye=eye, look=look, W=160, H=120, fov=60)
        hudrender.render(items[1:], '/tmp/_st2.png', eye=eye, look=look, W=160, H=120, fov=60)
        a = np.asarray(__import__('PIL.Image').Image.open('/tmp/_st1.png')).astype(int)
        b = np.asarray(__import__('PIL.Image').Image.open('/tmp/_st2.png')).astype(int)
        red = lambda im: ((im[:, :, 0] > 60) & (im[:, :, 2] < 40)).sum()
        out.append(red(a) / max(1, red(b)))
    return out
def scores(P):
    from skull_hold import inside, samples
    T = np.concatenate([sh.U[1]['tris'], sh.U[2]['tris'] + len(sh.U[1]['xyz'][0])])
    S = samples(P, T)
    hin = int(inside(hv, P, T).sum())
    bur = float(inside(S, hv, ht).mean())
    gap = htree.query(S)[0].min()
    return hin, bur, gap
for lab, hook, rot, P in (('before (lb-r8, seated orientation)', H0, (0, 0, 0), SV0 + t0), ('after (turned, re-seated %s)' % DSHIFT, h, tuple(ypr), P_after)):
    hin, bur, gap = scores(P)
    v = vis(hook, rot)
    print('%-36s hand verts inside %3d, skull buried %4.1f%%, nearest hand %.2f cm, seen from 4 heads %s'
          % (lab, hin, 100 * bur, gap, ['%.0f%%' % (100 * x) for x in v]))
if OUT:
    from PIL import Image
    ims = []
    for k, (hook, rot) in enumerate(((H0, (0, 0, 0)), (h, tuple(ypr)))):
        for e, (eye, look) in enumerate(EYES[:3]):
            p = '/tmp/_stp%d%d.png' % (k, e)
            hudrender.render([dict(path=SRC + 'models/rsq/ammo_hand.md3', frame=FR, scale=(-1, 1, 1), off=(0, -24, -10), color=(70, 70, 76)),
                              dict(path=U, frame=0, scale=SC, off=OFF, hook=hook, rot=rot, color=(225, 150, 140))],
                             p, eye=eye, look=look, W=300, H=240, fov=55, title=['before', 'after'][k] + ' head %d' % e)
            ims.append(Image.open(p))
    W = Image.new('RGB', (900, 480))
    for i, im in enumerate(ims):
        W.paste(im, ((i % 3) * 300, (i // 3) * 240))
    W.save(OUT); print(OUT)

# ---- re-seat the TURNED skull in the hand (translation only, F L U cm steps), the visible.py rule: it must
# still touch the fingers (nearest hand point <= 0.6 cm, <= 40 hand vertices inside it); the best is the one
# whose WORST head view shows the most of it.
if '--search' in os.environ.get('SKULL_TURN', ''):
    import itertools
    best = None
    T = np.concatenate([sh.U[1]['tris'], sh.U[2]['tris'] + len(sh.U[1]['xyz'][0])])
    for d in itertools.product((-4, -2, 0, 2, 4), (-4, -2, 0, 2, 4), (-2, 0, 2, 4, 6)):
        dd = np.array(d, float)
        hin, bur, gap = scores(P_after + dd)
        if gap > 0.6 or hin > 40:
            continue
        hk, yp = solve_hook(SC, OFF, RD, c0, c1 + dd)
        v = vis(hk, tuple(yp))
        print('d %s hin %d buried %.1f%% gap %.2f seen %s' % (d, hin, 100 * bur, gap, ['%.0f%%' % (100 * x) for x in v]), flush=True)
        if best is None or min(v) > best[0]:
            best = (min(v), d, hk, yp, v, hin, bur, gap)
    s, d, hk, yp, v, hin, bur, gap = best
    print('BEST shift %s: HandHook %s HandRot %s; hand verts inside %d, buried %.1f%%, nearest %.2f cm, seen %s'
          % (d, np.round(hk, 4), np.round(yp, 4), hin, 100 * bur, gap, ['%.0f%%' % (100 * x) for x in v]))

# ---- the rows for vreload (row 13): the hook and turn of the HANDMAG layer, and where the skull's top and
# its insertion axis are in the off hand's frame (MagAtWell), for a re-seat shift SKULL_SHIFT="F L U"
if os.environ.get('SKULL_SHIFT'):
    dd = np.array([float(x) for x in os.environ['SKULL_SHIFT'].split()])
    hk, yp = solve_hook(SC, OFF, RD, c0, c1 + dd)
    well = sh.WELL; axis = np.array([0.0, 0.0, -1.0])
    top = RD @ (well - c0) + c1 + dd
    ax = RD @ axis
    Pk = np.vstack([to_flu(sh.U[s]['xyz'][0], SC, OFF, hook=hk, ypr=yp) for s in (1, 2)])
    print('ROWS shift (%.0f, %.0f, %.0f): HandHook (%.3f, %.3f, %.3f) HandRot (%.3f, %.3f, %.3f) TopInHand (%.3f, %.3f, %.3f) AxisInHand (%.4f, %.4f, %.4f); chain check %.4f cm'
          % (tuple(dd) + tuple(hk) + tuple(yp) + tuple(top) + tuple(ax) + (np.abs(Pk - ((SV0 - c0) @ RD.T + c1 + dd)).max(),)))
    # the old TopInHand reproduces from the old hook: WELL + t0
    print('check: old TopInHand = WELL + t0 = %s (row %s)' % (np.round(well + t0, 3), np.round(row('TopInHand'), 3)))
