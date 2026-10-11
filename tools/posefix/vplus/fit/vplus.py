"""Vanilla VR Plus (1.0b_Weapons_VanillaVRPlus_v1.2, FILTER/DOOM) guns for the hand tools.
Placement and ready frames are read off the set's own MODELDEF (FILTER/DOOM/modeldef.weapons.txt,
Modeldef.Rifle / .Revolver / .shotty). Importing this module teaches guns.item() these classes."""
import sys, os
H = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/tool/hands'
sys.path.insert(0, H)
import guns
U = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2'
HUD = U + '/Models/Weapons/Hud/'
GUNS = U + '/FILTER/DOOM/models/weapons/hud/'
ONE = (-1.0, 1.0, 1.0)
# class: (mesh, ready frame, scale, offset, ready sprite)
ITEMS = {
    'Vanilla_Chaingun':       (HUD + 'Chaingun/chaingun.md3', 4, ONE, (0, 0, 0), 'CHGG A'),
    'Vanilla_RocketLauncher': (HUD + 'RPG/RPG.md3', 5, ONE, (0, 0, 0), 'MISG A'),
    'Vanilla_PlasmaRifle':    (HUD + 'PlasmaRifle/PlasmaRifle.md3', 4, ONE, (0, 0, 0), 'PLSG A'),
    'Vanilla_BFG9000':        (HUD + 'BFG9000/BFG.md3', 6, ONE, (0, 0, 0), 'BFGG A'),
    'Vanilla_Chainsaw':       (HUD + 'Chainsaw/Chainsaw.md3', 5, (-1.5, 1.5, 1.5), (0, 14, 0), 'SAWG C'),
    'VR_Rifle':               (GUNS + 'guns/m16.md3', 0, (1.35, 1.35, 1.35), (0, 0, 0), 'RIFL A'),
    'VR_Revolver':            (GUNS + 'gats/rev.md3', 0, (1.35, 1.35, 1.35), (0, 0, 0), 'REVL A'),
    'VR_Revolver2':           (GUNS + 'gats/rev.md3', 0, (1.35, 1.35, 1.35), (0, 0, 0), 'REVL A'),
    'VR_Shotgun':             (GUNS + 'guns/shotgun.md3', 0, (1.35, 1.35, 1.35), (0, 0, 0), 'SHTG A'),
    'VR_SuperShotgun':        (GUNS + 'guns/ssg.md3', 0, (1.35, 1.35, 1.35), (0, 0, 0), 'SHT2 A'),
}
# the BD22 gun whose mesh it is
SHARED = {'Vanilla_Chaingun': 'Minigun', 'Vanilla_RocketLauncher': 'Rocket_Launcher',
          'Vanilla_PlasmaRifle': 'Plasma_Gun', 'Vanilla_BFG9000': 'BIG_FUCKING_GUN'}

def vitem(cls, frame=None):
    p, f, sc, off, key = ITEMS[cls]
    return dict(path=p, frame=f if frame is None else frame, scale=list(sc), off=list(off), key=tuple(key.split()))

_orig = guns.item
def item(cls, spr=None, fr=None):
    if cls in ITEMS:
        return vitem(cls)
    return _orig(cls, spr, fr)
guns.item = item
