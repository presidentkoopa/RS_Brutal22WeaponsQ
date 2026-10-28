"""bore.py: where each gun's DRAWN BARREL points, in the weapon controller's frame (F forward, L left, U up).

fix-accuracy (owner 2026-10-28, report item 31: "all the guns pull to the right"). Every shot in VR goes down the
engine's AttackDir, which is the CONTROLLER's forward (hw_vrmodes.cpp MapWeaponDir). The 2.0 hand ports turned every
gun in the hand (MODELDEF AngleOffset / PitchOffset / RollOffset, the approved pistol's r5 aim) and moved every table
that hangs off the gun (muzzle, scope Lens and Axis, casings, reload rows) -- but not the shot's direction.

This measures, per gun, from the MESH (ready frame, the shipped MD3 in src/models):
  1. the bore at the 1.92 placement (MODELDEF Offset 0 0 / ZOffset -5, no angle offsets): the barrel's cross-section
     centre (bounding-box midpoint in L and U) in thin slices along F over the front of the gun, a least-squares line
     through them; its yaw and pitch from the controller's forward;
  2. the same bore through the CURRENT MODELDEF placement (port record R, the gun's rigid move): R @ bore_192.
Chain: QZD 17.3 models.cpp RenderHUDModel (gunplace.to_local_ao, gunview.to_fl in tools/handfit/fbx_fitter).

Usage: python3 tools/accuracy/bore.py [Class ...]     (prints a table; --zs prints the RSQ_Muzzle.Bore rows)
"""
import os, sys, re, json, math, struct, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools', 'handfit', 'fbx_fitter'))
import gunplace, gunview

SRC = os.path.join(REPO, 'src')
# cls: md3 (under src), ready frame, 1.92 scale, 1.92 off, surfaces of the barrel (None: all), the front window (cm back from the tip)
GUNS = {
 'BrutalPistol':   ('models/bd/BrutalPistol/BrutalPistol.md3', 3, [-1, 1, 1], [0, 0, -5], None, 6),
 'BrutalSMG':      ('models/bd/BrutalSMG/BrutalSMG.md3', 3, [-1, 1, 1], [0, 0, -5], None, 8),
 'Rifle':          ('models/bd/Rifle/Rifle.md3', 3, [-1, 1, 1], [0, 0, -5], [4], 12),
 'Shot_Gun':       ('models/bd/ShotGun/Shotgun.md3', 4, [-1, 1, 1], [0, 0, -5], None, 12),
 'AssaultShotgun': ('models/bd/AssaultShotgun/AssaultShotgun.md3', 4, [-1, 1, 1], [0, 0, -5], None, 12),
 'SSG':            ('models/bd/SSG/SSG.md3', 1, [-1, 1, 1], [0, 0, -5], None, 8),
 'Minigun':        ('models/bd/Minigun/Minigun.md3', 4, [-1, 1, 1], [0, 0, -5], None, 15),
 'MG42':           ('models/bd/HitlersBuzzsaw/HitlersBuzzsaw.md3', 0, [-1, 1, 1], [0, 0, -5], None, 12),
 'Machinegun':     ('models/bd/Machinegun/Machinegun.md3', 4, [-1, 1, 1], [0, 0, -5], [5], 12),
 'RailGun':        ('models/bd/RailGun/RailGun.md3', 3, [-1, 1, 1], [0, 0, -5], None, 15),
 'Sniper':         ('models/bd/XM21/XM21.md3', 0, [-10.485, 10.485, 10.485], [-0.2816, -44.5467, -6.3157], [9], 15),
 'Plasma_Gun':     ('models/bd/Plasma_Gun/Plasma.md3', 4, [-1, 1, 1], [0, 0, -5], None, 12),
 'Revolver':       ('models/bd/Revolver/Revolver.md3', 0, [-1, 1, 1], [0, 0, -5], None, 6),
}
FITS = os.environ.get('RSQ_FITS_DIR', '/home/claude/rsq_weapondepot/sets/bd22q/handfit/fits')	# the Depot's port records (R per gun)
PISTOL = dict(off=[0.820, -8.333, -1.408], ao=(3.854, 3.363, 10.974))	# the approved pistol's r5 aim (port_gun.PISTOL_R5)

def frames(path):
    d = open(path, 'rb').read(); nsurf = struct.unpack_from('<i', d, 84)[0]; off = struct.unpack_from('<i', d, 100)[0]; out = []
    for s in range(nsurf):
        flags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, oend = struct.unpack_from('<10i', d, off + 68)
        out.append(np.frombuffer(d, '<i2', snfr * nv * 4, off + oxyz).reshape(snfr, nv, 4)[:, :, :3].astype(float) / 64.0); off += oend
    return out
def chain(scale, off, ao):
    it = dict(scale=list(scale), off=list(off), ao=tuple(ao))
    return lambda V: gunview.to_fl(gunplace.to_local_ao(np.atleast_2d(np.asarray(V, float)), it))
def affine(f):
    b = f(np.zeros(3))[0]; return np.stack([f(np.eye(3)[i])[0] - b for i in range(3)], 1), b
def rigid(scale, off0, off1, ao1):
    A0, b0 = affine(chain(scale, off0, (0, 0, 0))); A1, b1 = affine(chain(scale, off1, ao1)); R = A1 @ np.linalg.inv(A0); return R, b1 - R @ b0
def yp(v):
    v = np.asarray(v, float) / np.linalg.norm(v); return math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(v[2]))

def bore192(cls):
    md3, fr, sc, off, surf, win = GUNS[cls]
    S = frames(os.path.join(SRC, md3)); X = np.concatenate([s[fr] for k, s in enumerate(S) if surf is None or k in surf])
    V = chain(sc, off, (0, 0, 0))(X); tip = V[:, 0].max()
    # the barrel only: vertices inside the tip face's L/U box (+0.3 cm), over the window behind the tip
    T = V[V[:, 0] > tip - 0.3]; lo = T[:, 1:].min(0) - 0.3; hi = T[:, 1:].max(0) + 0.3
    V = V[(V[:, 1] >= lo[0]) & (V[:, 1] <= hi[0]) & (V[:, 2] >= lo[1]) & (V[:, 2] <= hi[1])]
    pts = []
    for f0 in np.arange(tip - win, tip - 0.4, 0.5):
        m = (V[:, 0] >= f0) & (V[:, 0] < f0 + 0.5)
        if m.sum() < 4: continue
        Q = V[m]; pts.append((f0 + 0.25, (Q[:, 1].min() + Q[:, 1].max()) / 2, (Q[:, 2].min() + Q[:, 2].max()) / 2))
    P = np.array(pts)
    kl = np.polyfit(P[:, 0], P[:, 1], 1); ku = np.polyfit(P[:, 0], P[:, 2], 1)
    d = np.array([1.0, kl[0], ku[0]]); d /= np.linalg.norm(d)
    rl = np.abs(np.polyval(kl, P[:, 0]) - P[:, 1]).max(); ru = np.abs(np.polyval(ku, P[:, 0]) - P[:, 2]).max()
    return d, len(P), max(rl, ru), tip

def R_now(cls):
    p = os.path.join(FITS, 'ported_%s.json' % cls)
    if os.path.exists(p):
        d = json.load(open(p)); return np.array(d['R']), 'port record ported_%s.json' % cls
    md3, fr, sc, off, surf, win = GUNS[cls]
    R, t = rigid(sc, off, PISTOL['off'], PISTOL['ao']); return R, "the approved pistol's r5 move (port_gun.PISTOL_R5)"

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cls', nargs='*'); ap.add_argument('--zs', action='store_true'); a = ap.parse_args()
    print('%-15s %5s %6s | %-26s | %-27s | %s' % ('gun', 'slices', 'fit cm', 'bore at 1.92 (yaw L, pitch U)', 'bore drawn now (F L U)', 'yaw L / pitch U now'))
    for c in (a.cls or GUNS):
        d, n, r, tip = bore192(c); R, src = R_now(c); b = R @ d
        y0, p0 = yp(d); y1, p1 = yp(b)
        print('%-15s %5d %6.2f | %+6.2f %+6.2f deg            | %.4f %+.4f %+.4f   | %+6.2f %+6.2f deg   (%s)' % (c, n, r, y0, p0, b[0], b[1], b[2], y1, p1, src))

def muzzle_row(md3, fr, sc, off, place, surf=None):
    """port_gun.muzzle's method for a gun with no RSQ_Muzzle row: the front-most face centre of the ready frame at the
    1.92 placement, moved with the gun (R, t from the 1.92 MODELDEF numbers to `place`, the 6 MODELDEF numbers now)."""
    S = frames(os.path.join(SRC, md3)); X = np.concatenate([s[fr] for k, s in enumerate(S) if surf is None or k in surf])
    V = chain(sc, off, (0, 0, 0))(X); f = V[:, 0].max(); T = V[V[:, 0] > f - 0.3]
    v = np.array([f, (T[:, 1].min() + T[:, 1].max()) / 2, (T[:, 2].min() + T[:, 2].max()) / 2])
    R, t = rigid(sc, off, place[:3], place[3:]); return v, R @ v + t
