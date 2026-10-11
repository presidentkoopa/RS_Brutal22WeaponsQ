"""v4 pose data: hand families, level fixes, the 21 guns' remaining frames, and
the eight BD22 weapons that had no model at all.

Every number here is a frame of the SOURCE mesh (before stripping).
Phases were matched by looking at the BD22 sprite art next to the mesh frames
(tools/pose_axis.py gives each frame's position and barrel pitch).
"""


def letters(spec):
    """'A0 B1 [6 \\\\0' -> {'A': 0, 'B': 1, '[': 6, '\\\\': 0}"""
    return {tok[0]: int(tok[1:]) for tok in spec.split()}


def run(chars, pose):
    return {c: pose for c in chars}


ALL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]'

# ---------------------------------------------------------------------------
# Hand families. One letter map per family, shared by every colour variant
# (BD22 numbers its bloody copies: 1ONG red, 2ONG blue, 3ONG green, 4ONG
# vanilla, 5ONG berserk ...). The mesh is the authored BD21 one.
#
# fistclosed.md3: 0 fist ready | 1 drawn back | 2-5 jab out | 6-9 back
#   10-13 cross to the left | 14-21 open hand | 22-24 uppercut low
#   25-29 uppercut high | 30-34 coming down to a raised fist
#   35-44 knuckle crack (authored PUNS) | 45-50 throw (authored THRF)
#   51-56 reach and grip (authored PKUP) | 61-74 taunt (authored FUCK)
# ---------------------------------------------------------------------------
FIST_FAMILIES = [
    # taunt: authored A-O; Melee's own taunt runs on to S, back down the same way
    (('FUCK', 'VUCK', '1UCK', '2UCK', '3UCK', '4UCK'),
     letters('A61 B62 C63 D64 E64 F66 G67 H68 I69 J69 K71 L72 M73 N74 O74 P73 Q72 R71 S70')),
    # A ready | B-H left jab out and back | I J ready | K-O big cross
    # P-U fists lowering / raising | V-[ right jab | \ fists down (no art)
    (('PONG', '1ONG', '2ONG', '3ONG', '4ONG', '5ONG'),
     letters('A0 B1 C2 D3 E4 F5 G7 H9 I0 J0 K10 L11 M12 N13 O13 P0 Q0 R0 S0 T0 U0 '
             'V1 W2 X3 Y4 Z5 [6 \\0')),
    # A-K hook sweeping left | L-V uppercut up and down
    (('PUNG', '1UNG', '2UNG', '3UNG', '4UNG', '5UNG'),
     letters('A1 B9 C10 D11 E12 F13 G13 H13 I13 J13 K13 L23 M24 N25 O28 P29 Q30 R31 '
             'S32 T33 U34 V0')),
    # Melee idle / sprint bob: the bob comes from the psprite offsets
    (('FIST', '1IST', '22ST', '3IST', '5IST'), run(ALL, 0)),
    # knuckle crack: authored A-G, BD22's left-hand copy H-M takes the same poses
    (('PUNS',), letters('A35 B36 C37 D38 E39 F40 G41 H36 I37 J38 K39 L40 M41')),
    # grab: authored A-F, held on F
    (('PKUP', '1KUP', '2KUP', '3KUP'), letters('A51 B52 C53 D54 E55 F56 G56 H56 I56 J56 K56')),
    # throw: authored THRF order
    (('THRW', '1HRW', '2HRW', '3HRW', '5HRW'), letters('A45 B46 C47 D48 E49 F49 G49 H49 I49 J49')),
    # carried things (barrel, monsters, trophies, lost soul, head smash): the
    # gripping hand; the throw frames take the throw poses
    (('THRG', '1HRG', '2HRG', '3HRG'), run(ALL, 55)),
    (('GRZ1', 'GRZ2', 'GRZ3', 'GRZ4', 'GRZ5', 'GRZ6', 'GRZ7'), letters('A55 B55 C55 D45')),
    (('PTG1',), letters('B55 C55 D55 E55 F55 G45 H46 I47 J48 K49')),
    (('PTG2',), letters('A55 B55 C55 D45 E46 F47 G48')),
    (('PTG3',), letters('A55 B55 C55')),
    (('THEA',), letters('A52 B53 C54 D55 E55 F55 G55 H45 I46 J47 K48 L49 M55 N55 O55 P55 Q55')),
    (('IEHW',), dict(run('ABCDEFGHIJK', 55), **run('LMNOPQRST', 56))),
    # salute: BD22 ships no SALU art, so flat BD22 shows an empty screen here;
    # the fist rises into a raised fist and pumps (D E alternate)
    (('SALU',), letters('A30 B31 C32 D33 E34')),
]

# Boot.md3: authored BD21 numbers
_kick = {c: 20 + i for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTU')}
_kick.update(run('VWXYZ[\\]', 40))       # BD22's air kick runs past U: held on U
BOOT_FAMILIES = [
    (('KICK', '1ICK', '2ICK', '3ICK'), _kick),
    (('KIK1', '1IK1', '2IK1', '3IK1'), letters('A5 B6 C7 D8 E9')),
    (('KIK2', '1IK2', '2IK2', '3IK2'), letters('A10 B11 C12 D13 E14')),
    (('STOM', '1TOM', '2TOM', '3TOM'), letters('A53 B54 C55 D56 E57')),
    (('SLID', '1LID', '2LID', '3LID'), run('ABCDEFGHIJKLMN', 24)),   # leg out (KICK E)
]

# nade.md3: 0-2 raise to held | 3-5 pin | 6-10 held | 11-12 wind-up | 13-15 away
# A-M authored. N O P come after the release: the grenade stays gone (15),
# it does not come back to the hand (16-18 are the projectile's own tumble).
# HandGrenades' own frames: Q held (authored ready, 2) | V W X raise | R-U to the pin
NADE_FAMILIES = [
    (('GRTH', 'VGRN'), letters('A3 B4 C5 D6 E7 F8 G9 H10 I11 J12 K13 L14 M15 N15 O15 P15 '
                        'Q2 R2 S3 T4 U5 V0 W1 X2')),
]

HAND_SPECS = {
    'fistclosed.md3': FIST_FAMILIES,
    'Boot.md3': BOOT_FAMILIES,
    'nade.md3': NADE_FAMILIES,
}


def family_pose(families, spr, fr):
    for sprites, m in families:
        if spr in sprites:
            return m.get(fr)
    return None


def hand_mesh_for(spr):
    for mesh, fams in HAND_SPECS.items():
        if any(spr in s for s, _ in fams):
            return mesh
    return None


# ---------------------------------------------------------------------------
# Level fixes (user: "the railgun and the bfgs are not level")
# BFG.md3: 0-5 raise (barrel pitch -42 -> 0) | 6-11 level ready | 12-13 pushed
#   back | 14 kicked up 12 deg | 15 coming down. Authored BD21: BFGS A-F 0-5,
#   BFGN A 6, sprint 5. Every BD22 key sat on 0 (pitched 42 deg down).
# RailGun.md3: 0-3 raise (pitch -46 -> 0) | 3 level ready. Keys sat on 2 (-11).
# ---------------------------------------------------------------------------
BFG_LEVEL = {}
for _c, _p in letters('A0 B2 C3 D5 E5 F3 G2 H0').items():
    BFG_LEVEL[('BFGS', _c)] = _p                     # SelectAnimation ABCD, Deselect EFGH
for _c, _p in letters('A6 B5 C5 D5 E5 F6 G7 H8 I9 J10 K11 L7 M8 N9 O10 P11 Q7 R8').items():
    BFG_LEVEL[('BFGN', _c)] = _p                     # A ready, B-E swung aside, G-R charging
for _c, _p in letters('A12 B13 C14 D14 E15 F15 G6 H6 I6 J6 K6 L6').items():
    BFG_LEVEL[('BFGA', _c)] = _p                     # fire: back, kick up, settle
BFG_LEVEL[('BFUG', 'A')] = 6


def railgun_level(spr, fr, pose):
    if spr == 'RAIL' and fr in 'LKJI':
        return {'L': 0, 'K': 1, 'J': 2, 'I': 3}[fr]   # SelectAnimation LKJI
    if spr == 'RAIL' and fr in 'EFGH':
        return {'E': 3, 'F': 2, 'G': 1, 'H': 0}[fr]   # Deselect EFGH
    return 3 if pose == 2 else pose


# ---------------------------------------------------------------------------
# The 21 guns: frames BD22 can show that were never keyed. A colour/purist/
# dual copy takes the pose its base sprite has for the same letter; with no
# such key, the gun's ready pose.
# ---------------------------------------------------------------------------
READY = {
    'AssaultShotgun': 4, 'BIG_FUCKING_GUN': 6, 'BrutalAxe': 5, 'BrutalPistol': 7, 'BrutalSMG': 7,
    'Chain_saw': 15, 'DSweap': 0, 'FlameCannon': 0, 'Flamethrower2': 0, 'HellishMissileLauncher': 0,
    'GrenadeLauncher': 3, 'MP40': 2, 'Minigun': 4, 'Plasma_Gun': 4, 'Rocket_Launcher': 5,
    'RailGun': 3, 'Revolver': 0, 'Rifle': 3, 'SSG': 0, 'Shot_Gun': 4, 'Unmaker': 0,
}
SIBLING = {
    'AssaultShotgun': {'2SAS': 'USAS'},
    'BrutalAxe': {'1XEA': 'AXEA', '2XEA': 'AXEA', '3XEA': 'AXEA', '4XEA': 'AXEA', '5XEA': 'AXEA',
                  '1XEG': 'AXEG', '2XEG': 'AXEG', '3XEG': 'AXEG', '4XEG': 'AXEG', '5XEG': 'AXEG'},
    'BrutalPistol': {'2IST': 'PIST', 'PI2G': None},
    'BrutalSMG': {'2MGF': 'SMGF', 'SM2S': 'SMGS'},
    'Chain_saw': {'1AWF': 'SAWF', '2AWF': 'SAWF', '3AWF': 'SAWF', 'PAWF': 'SAWF',
                  '1AWG': 'SAWG', '2AWG': 'SAWG', '3AWG': 'SAWG', 'PAWG': 'SAWG',
                  '1AWS': 'SAWS', '2AWS': 'SAWS', '3AWS': 'SAWS',
                  '2AWB': '1AWB', '3AWB': '1AWB'},
    'FlameCannon': {'2LMG': 'FLMG', 'DUFL': None, 'FLMG': None},
    'Flamethrower2': {'2LMT': 'FLMT'},
    'HellishMissileLauncher': {'PVCG': 'RVCG'},
    'GrenadeLauncher': {'2RL2': 'GRL2', '2RLN': 'GRLN'},
    'MP40': {'PP40': 'MP40', 'MP42': None},
    'Minigun': {'CHAE': 'CHAG', 'CHAV': 'CHAG', 'CHAG': None},
    'Plasma_Gun': {'2RSG': 'PRSG', 'DUPR': None},
    'Rocket_Launcher': {'2ISF': 'MISF', 'MISF': None},
    'RailGun': {'2AIF': 'RAIF'},
    'Revolver': {'2EVO': 'REVO', 'REVU': None},
    'Rifle': {'1IG2': None, 'RIG2': None, 'RIGL': None, '1IGL': None, 'RIFF': None, 'RI2F': None,
              '2IFF': 'RIFF', 'DURR': None},
    'SSG': {'VSSG': 'SHT2', 'VSHZ': 'SHTZ', 'V5HZ': None},
    'Shot_Gun': {'2HTA': 'SHTA', '2HTN': 'SHTN'},
    'Unmaker': {'2NHF': 'UNHF', '2NHG': 'UNHG'},
}


# ---------------------------------------------------------------------------
# The eight BD22 weapons that had no model. Placement is each source pack's
# own (authored for VR). 'src' is the file in the user's VR_WeaponSetRebuild
# folder (or the original pk3 for BFG_10k / the hand meshes).
# ---------------------------------------------------------------------------
def _k(spr, spec):
    return {(spr, c): p for c, p in letters(spec).items()}


def _merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


NEW = {
    # BD21 VR's own model for this gun (BR_VR B35 'HitlersBuzzsaw', same HBUS
    # sprites): 0 ready, 1-2 recoil. L-O raise, P-S lower, G-K swung aside.
    'MG42': [dict(
        path='models/bd/HitlersBuzzsaw', mesh='HitlersBuzzsaw.md3', skins={0: 'HitlersBuzzsaw.png'},
        src='b35:HitlersBuzzsaw', placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'ZOffset -5'],
        keys=_merge(_k('HBUS', 'A0 B1 C2 F1 G0 H0 I0 J0 K0 L0 M0 N0 O0 P0 Q0 R0 S0'),
                    _k('PBUS', 'A0 B1 C2 F1')))],
    # BD21 VR's own model (Modeldef.BFG10k.def). BFG_10k.md3: 0-5 raise,
    # 6 ready, 7-10 barrel spin (authored charge), 12-13 back, 14-20 settle.
    # Lit skin (BFG_10k2) where the BD22 art glows; dark skin raise/lower/empty.
    'BFG10k': [
        dict(path='models/bd/BFG', mesh='BFG_10k.md3', skins={0: 'BFG_10k2.png'}, src='pk3',
             placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'ZOffset -5'],
             keys=_merge(_k('BG2G', 'A6 B6 C6 D6 E6 F6 G7 H8 I9 J10 K7 L8 M12 N13 O13 P14 Q16 R19'),
                         _k('BG3G', 'A5 B5 C5 D5'))),
        dict(path='models/bd/BFG', mesh='BFG_10k.md3', skins={0: 'BFG_10k.png'}, src='pk3',
             placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'ZOffset -5'],
             keys=_merge(_k('BG2G', 'S0 T2 U4 V5 W5 X4 Y2 Z0 [6'),
                         _k('BG3G', 'E5 F5 G5 H5'))),
    ],
    # XM21 sniper on the Breach HK416 (owner's pick: a modern rifle to match the
    # XM21's sound and rate of fire). IQM, 360 frames, frame = Breach's own
    # MODELDEF numbering (MK18 A = 0 ... MK31): 25 ready | 26-28 fire | 63-148
    # magazine reload (mag out 89, mag in 101) | 149-343 inspect, whose second
    # half is the bolt: bolt back 299, bolt released 317, done 343.
    # Skins are Breach's (Model HK416S) except mesh 0, its view arms.
    'Sniper': [dict(
        path='models/bd/HK416', mesh='hk416.iqm',
        skins={0: 'nohands.png', 1: 'SUP.bmp', 2: 'Grip2.bmp', 3: '1.bmp', 4: '9.bmp', 5: 'cock.bmp',
               6: 'marg-ris.bmp', 7: 'f1.bmp', 8: 'mag.bmp', 9: 'Magpul_Diffuse.bmp', 10: 'eotech553.bmp',
               11: 'glass.png', 12: 'anpaq.bmp'},
        src='Breach-weapons/models/weapons/hk416',
        # VR seat, not Breach's flat-screen one. Breach draws its own arms on
        # mesh 0: skinned fully transparent (HUD models are alpha-tested,
        # hw_weapon.cpp gl_mask_threshold), so only the rifle shows. Scale:
        # the same signs as every other gun here (-1 1 1); 1.35 = the BD22
        # rifle's size (trigger to muzzle 61.8 vs 47.1, trigger to mag floor
        # 15.3 vs 10.7 file units).
        # models.cpp RenderHUDModel scales AFTER the jDoom 90 degree turn, so
        # MODELDEF Scale y is the mesh's length axis: v4-v7 had -1.35 there,
        # which turned the rifle round and put it 69 cm behind the hand (not
        # visible). Offset puts the HK416's trigger (21.03, 5.09, -11.63 at
        # frame 25, RS_Modern tools/points/hk416s.json) on the BD22 rifle's
        # trigger, both through the same chain (melee/hudrender.to_local).
        placement=['Scale -1.35 1.35 1.35', 'Offset 6.499 -3.835 10.913'],
        keys=_merge(_k('X21G', 'A25 B25 C25 D25 E25 F25'), _k('X21F', 'A26 B27 C28'), _k('P21F', 'A26 B27 C28'),
                    _k('P21G', 'A25'), _k('X21A', 'A25 B25 C25'), _k('X21S', 'A25 B25 C25 D25 E25 F25 G25 H25'),
                    _k('SNIP', 'A25 B25 C25 D25'), _k('SINP', 'D25'), _k('DEAG', 'A25'),
                    # reload: B opens and (in the finish) closes, so it is the
                    # reload's first frame, which is the ready pose; Sniper/MagOut
                    # after the second I -> 89, Sniper/MagIn after U -> 101
                    _k('X21R', 'A25 B63 C67 D70 E73 F76 G79 H82 I88 J90 K91 L92 M93 N94 O95 P96 '
                               'Q97 R98 S99 T100 U101 V102 W103 X104 Y110 Z114 [118 \\124 ]130'),
                    # finish + bolt: X22R A-C settle, D-J hand to the bolt, K bolt back
                    # (Sniper/BoltBack), L M held, Sniper/BoltForward, N-S release and settle
                    _k('X22R', 'A134 B138 C142 D286 E288 F290 G292 H294 I296 J298 K299 L302 M305 '
                               'N317 O322 P327 Q332 R337 S343'),
                    # empty-reload start (and the unload's end, reversed)
                    _k('X23R', 'A67 B70 C73 D76 E79 F82 G25 H25 I25 J25 K25 L25 M25')))],
    # M32 six-shot (Robocop Retribution VR) for the M202: 0 ready, 2 full kick.
    'IncendiaryLauncher': [dict(
        path='models/bd/M32', mesh='m32.md3',
        skins={0: 'm32_tex1.png', 1: 'm32_tex2.png', 2: 'm32_tex1.png', 3: 'm32_tex1.png',
               4: 'm32_tex2.png', 5: 'm32_tex2.png', 6: 'm32_tex1.png', 7: 'm32_tex2.png',
               8: 'm32_tex1.png'},
        src='Robocop-Retribution/models/weapons/m32',
        placement=['Scale -0.62 0.62 0.62', 'Offset 0.0 -30.0 -8.0', 'NoInterpolation'],
        keys=_k('M202', 'A0 B2'))],
    # HacX Nuker (VR) for the nuke launcher: 0 ready, 5 fired, 4-1 settling.
    'NukeLauncher': [dict(
        path='models/bd/Nuker', mesh='Nuker.md3', skins={0: 'Nuker.png'}, src='HacX/MODELS/Nuker',
        placement=['Scale -1.1 1.1 1.1', 'Offset 0.0 0.0 0.0', 'ZOffset -5'],
        keys=_merge(_k('NKLG', 'A0 B0 C0 D0 E0'), _k('NKLS', 'A0 B0 C0 D0 E0 F0 G0 H0'),
                    _k('NKLF', 'A5 B5 C5 D5 E4 F4 G3 H3 I2 J2 K1 L1')))],
    # Sidewinder (Cola 3 VR) for the Devastator: 0 ready, 1-13 recoil and back.
    'Devastator': [dict(
        path='models/bd/Sidewinder', mesh='sidewinder.md3',
        skins={0: 'smr.png', 1: 'smr.png', 2: 'smr.png', 3: 'smr.png', 4: 'smr_ext1.png', 5: 'smr_plate.png'},
        src='Cola-3-VR-Weapons/models/weapons/sidewinder',
        placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 -13.0 0.0'],
        keys=_k('DEVA', 'A0 B1 C3 D5 E6 F8 G10 H12 I13 J1 K3 L5 M6 N8 O10 P12 Q13 '
                        'R0 S0 T0 U0 V0 W0 X0 Y0 Z0'))],
}

# Fists and grenade weapons: their own model IS the hand block (authored
# Modeldef.Fist.def / Modeldef.Grenade.def placement for the main block).
HAND_WEAPONS = {
    'Melee_Attacks': ('fistclosed.md3', ['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'ZOffset -5',
                                         'NoInterpolation']),
    'HandGrenades': ('nade.md3', ['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'NoInterpolation',
                                  'ZOffset -5']),
}


# ---------------------------------------------------------------------------
# v4.1: hand-made per-gun tables (gun_tables/<Class>.py, TABLE = {(spr, letter):
# source mesh frame}). Each maps every frame BD22 shows on that gun to the mesh
# frame of the same moment, anchored on BD22's reload sounds / ammo / casings;
# the docstring of each file has the frame meanings and the pose lists.
# ---------------------------------------------------------------------------
import importlib as _il, os as _os, sys as _sys
_here = _os.path.dirname(_os.path.abspath(__file__))
if _here not in _sys.path:
    _sys.path.insert(0, _here)
GUN_TABLES = {}
for _f in sorted(_os.listdir(_os.path.join(_here, 'gun_tables'))):
    if _f.endswith('.py') and _f != '__init__.py':
        GUN_TABLES[_f[:-3]] = _il.import_module('gun_tables.' + _f[:-3]).TABLE

# the thrown / dropped grenade in the world: the authored BD21 blocks
# (Modeldef.Grenade.def), nade.md3 16-26 tumbling
_GRND = {('GRND', c): 16 + i for i, c in enumerate('ABCDEFGHIJK')}
WORLD = {c: [dict(path='models/bd/Grenade', mesh='nade.md3', skins={0: 'nade.png'}, src='pk3',
                  placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'NoInterpolation'], keys=dict(_GRND))]
         for c in ('HandGrenade', 'HandGrenadeDroped', 'HandGrenadeAlt')}
for _c in WORLD:
    WORLD[_c][0]['comment'] = 'thrown grenade in the world, authored BD21 block'

# the axe in the world (VR melee): BrutalAxe.md3 frame 5 (the held pose, AXEG A)
# at true size -- 0.35 = the hand model's 1 cm per unit * vr_weaponScale 1.02 *
# 34 map units per metre -- so it looks the same out of the hand as in it.
# Placements measured from the mesh (bbox centre (34.1, 0, 4.8) in its own units).
_AXE = dict(path='models/bd/BrutalAxe', mesh='BrutalAxe.md3', skins={0: 'BrutalAxe.png'}, src='pk3')
_AXE_FLY = ['Scale 0.35 0.35 0.35', 'Offset -11.93 0.0 2.31', 'NoInterpolation',
            'Rotating', 'Rotation-Speed -11.4', 'Rotation-Vector 0 0 1', 'Rotation-Center 0 4 0']
WORLD['ThrowedAxe'] = [dict(_AXE, comment='thrown axe: spins end over end, 2 turns a second, '
                            'about its middle', placement=_AXE_FLY,
                            keys={('AXET', c): 5 for c in 'ABCDEFGH'})]
WORLD['ThrowedAxeStrong'] = [dict(_AXE, comment='thrown axe (berserk): same', placement=_AXE_FLY,
                                  keys={('AXET', c): 5 for c in 'ABCDEFGH'})]
WORLD['BrutalAxeOnWall'] = [dict(_AXE, comment='axe stuck in a wall: head forward (pitched down 51) '
                                 'into the wall, handle toward the thrower',
                                 placement=['Scale 0.35 0.35 0.35', 'Offset -4.68 0.0 12.46', 'PitchOffset -51',
                                            'NoInterpolation'],
                                 keys={('AXET', 'A'): 5})]
WORLD['BrutalAxe'] = [dict(_AXE, comment='axe pickup: lying flat on the floor',
                           placement=['Scale 0.35 0.35 0.35', 'Offset -11.93 1.69 0.5', 'RollOffset 90',
                                      'NoInterpolation'],
                           keys={('AXE9', 'A'): 5})]
