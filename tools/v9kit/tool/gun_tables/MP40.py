"""MP40 (BD22) -> MP40.md3 (14 frames).

MESH FRAME MEANINGS (BD21 def Modeldef.MP40.def + Mp40.txt + parts.py ref 2)
  surfaces: 0 bolt/cocking handle ("zamek") | 1 body | 10 magazine ("magazynek") | rest static
  0-1   raise (0 lowest, 40 deg down, out of view; 1 = 20 deg down) [BD21 MP4S A B];
        1 = authored sprint pose [BD21 M40S A]
  2     ready [BD21 MP40 A; also the ADS pose MP4D / MP41 A]
  3-6   fire: bolt cycles 3.9 / 7.9 / 6.0 / 1.9 back [BD21 MP40 B C D E]
  7     reload start = ready (vertex-identical to 2)                [BD21 MP4R A]
  8     tilt 9 deg + bolt half back (8.4) + mag unlatched 1.5         [MP4R B]
  9     tilt 18 deg + bolt fully back (16.8) + mag dropped 5.6 (still in the well)
                                                                       [MP4R C]
  10-13 mag slides out: 11.5 (half out of the housing) | 17.9 (top at the mouth) |
        23.0 (clear) | 25.0 (clear, away); bolt stays back          [MP4R D E F G]
  BD21 played MP4R A-F (7..12), EmptyClipSpawn, then G G F E D D C C B A
  (13 13 12 11 10 10 9 9 8 7): the NEW mag goes in by running 13->9 backwards and
  the bolt goes forward + gun untilts on 9->8->7. In this mesh tilt, bolt-back and
  mag-unlatch are welded together on 7->8->9: there is no "bolt back, mag seated"
  pose and no "tilted, bolt forward" pose. Frame 9 is the hub: bolt back, gun in
  the reload posture, mag in the well (5.6 low).

BD22 SEQUENCES -> POSES (self-check, generated from TABLE by seqcheck.py)
Select:
    MP40 I0 H1 G1 F2 | MP40 A2
Deselect:
    MP40 A2 | MP40 J2 K1 L1 M0
Fire:
    MP40 A2 | MP40 B3 D5 E6 | MP40 A2
Fire purist:
    PP40 A2 | PP40 B3 D5 E6 | PP40 A2
ADS in/fire/out:
    MP40 A2 | MP40 N2 O2 P2 | MP40 P2 | MP40 Q4 R5 S6 | MP40 P2 P2 P2 | MP40 P2 O2 N2 | MP40 A2
Sprint:
    MP40 A2 | MP40 T2 U1 V1 | MP40 W1 W1 W1 W1 | MP40 V1 U1 T2 | MP40 A2
KickFlash:
    MP40 T2 U1 V1 W1 X1 | MP40 X1 | MP40 X1 W1 V1 U1 T2
Reload (empty) + FullReload:
    MP40 A2 | MP4R A7 B7 C7 D7 E7 F7 F7 G7 G7 G7 | <Bolt1 bolt back> | MP4R H8 I9 I9 J9 K9 K9 K9 K9 L9 L9 M9 N9 O9 O9 P9 Q9 | <Weapon/Empty> | MP4R Q9 Q9 R9 S9 T9 U9 U9 V9 V9 V9 | <Reload1 mag out> | MP4R W10 W10 X11 Y12 Z13 | <EmptyClip2Spawn> | MP4R [13 \\13 ]13 | 2P4R A13 B13 | 2P4R C13 C13 C13 C13 C13 C13 D13 E12 F11 G10 H9 H9 H9 | <Reload2 seat> | <give ammo> | 2P4R I9 J9 K9 L9 | MP4R V9 V9 V9 V9 V9 V9 U9 | 2P4R N9 | MP4R P9 O9 O9 N9 M9 L9 L9 K9 K9 K9 K9 | <Bolt2 bolt fwd> | MP4R J9 I9 I9 H8 G7 G7 G7 F7 F7 E7 D7 C7 B7 A7 | MP40 A2
ReloadNotEmpty (tactical):
    MP40 A2 | MP4R A7 B7 | 2P4R O8 P8 Q9 R9 R9 | <Weapon/Empty> | 2P4R S9 S9 S9 T9 U9 V9 W9 X9 X9 X9 Y9 | <Reload1 mag out> | 2P4R Z10 | 2P4R [11 \\12 ]13 | <EmptyClip2Spawn> | 3P4R A13 B13 C13 D13 E13 E13 E13 E13 E13 E13 E13 F12 G12 H11 I10 I10 J9 J9 J9 | <Reload2 seat> | <give ammo> | 3P4R K9 L9 M9 N9 N9 O9 O9 O9 O9 P9 | 2P4R U9 T9 R9 Q9 P8 O8 | MP4R B7 A7 | MP40 A2
ReloadAfterUnload + FullReload:
    MP40 A2 | MP4R A7 B7 | 3P4R Q8 R8 S9 T9 | 2P4R C13 C13 C13 C13 C13 C13 D13 E12 F11 G10 H9 H9 H9 | <Reload2 seat> | <give ammo> | 2P4R I9 J9 K9 L9 | MP4R V9 V9 V9 V9 V9 V9 U9 | 2P4R N9 | MP4R P9 O9 O9 N9 M9 L9 L9 K9 K9 K9 K9 | <Bolt2> | MP4R J9 I9 I9 H8 G7 G7 G7 F7 F7 E7 D7 C7 B7 A7 | MP40 A2
Unload:
    MP40 A2 | MP4R A7 B7 C7 D7 E7 F7 F7 G7 G7 G7 | <Bolt1> | MP4R H8 I9 I9 J9 K9 K9 K9 K9 L9 L9 M9 N9 O9 O9 P9 Q9 | <Weapon/Empty> | MP4R Q9 Q9 R9 S9 T9 U9 U9 V9 V9 V9 | <Reload1 mag out> | <take ammo> | MP4R W10 W10 X11 Y12 Z13 | MP4R [13 \\13 ]13 | 2P4R A13 B13 B13 B13 B13 B13 | 3P4R T9 T9 S9 R8 Q8 | MP4R B7 A7 | MP40 A2
Fidget / Bolt:
    MP40 A2 | MP4R A7 B7 C7 D7 E7 F7 F7 G7 G7 G7 | <Bolt1> | MP4R H8 I9 I9 J9 K9 K9 K9 K9 K9 | <Bolt2> | MP4R J9 I9 I9 H8 G7 G7 G7 F7 F7 E7 D7 C7 B7 A7 | MP40 A2
FirstSelect:
    3P4R U0 V1 | 5P4R E1 F7 G8 H9 | 3P4R E13 E13 E13 E13 E13 E13 F12 G12 H11 I10 I10 J9 J9 J9 J9 J9 J9 J9 | <Reload2 seat> | 3P4R K9 L9 M9 N9 N9 O9 O9 O9 O9 O9 P9 P9 | 2P4R U9 T9 R9 Q9 P8 O8 | MP4R B7 A7 | MP40 A2
SelectDual:
    MP42 V2 U2 T2 S2 | <MP40/Draw> | MP42 R2 Q2 P2 O2 | MP40 A2

  Read: bolt back on Bolt1 (H half, I full), held through the walk to the magazine;
  mag pulled on Reload1 (W 10 -> Z 13), new mag up 13 -> 9 (C..H) and in the well at
  Reload2; bolt goes forward and the gun untilts after Bolt2 (H 8, G 7) exactly where
  BD22's hand rides the handle forward. Mag out once, in once; no dip to ready.

JUDGEMENT CALLS
  - MP4R C..G (BD22 tilts the gun and puts the hand on the cocking handle): 7. Any
    tilted frame already has the bolt back, so tilting there would pull the bolt
    before the Bolt1 sound. Tilt + pull happen on H (8) / I (9).
  - MP4R H I J K are shown going out (after Bolt1: pull) and coming back (after
    Bolt2: release). J I = 9, H = 8, G = 7 reads right both ways: BD22's own art
    keeps the hand on the handle for J I I H after Bolt2, so the bolt reaching home
    on H/G matches the art.
  - Same for 2P4R O P Q R (tactical turn-in, and U T R Q P O turn-out) and 3P4R Q R S T
    (after-unload turn-in, and T S R Q turn-out): O P / Q R = 8 (half tilt), the rest 9.
  - After the new mag goes in (Reload2), the gun holds 9 until Bolt2: the mag sits
    5.6 low (in the well) until the bolt goes forward, as the authored BD21 reload did.
    Seating fully needs the bolt forward in this mesh.
  - Tactical reload (ReloadNotEmpty) and fidget also show the bolt going back: the
    mesh cannot tilt or drop the mag without it. Fidget shows the mag unlatch 5.6
    and return with the bolt.
  - Mesh has a mag at ready, BD22's unloaded gun has none: after Unload the mag pops
    back up into the well at 3P4R T (25 -> 5.6 in one tic, gun still tilted, body
    static) and seats as the gun turns back. ReloadAfterUnload pops it down at 2P4R C
    (gun static) and inserts it once. Animating it in/out instead would show a fake
    extra insert/removal.
  - FirstSelect: 3P4R U V + 5P4R E F rise on the select frames (0 1 1) to 7, 5P4R G H
    turn into the posture (8 9), 3P4R E empty well (13, mag pops away one tic), then
    one insertion F..J (12 12 11 10 9) and the turn-out.
  - Fire B D E: authored letters (B 3, D 5, E 6; BD22 skips C). Aimed fire Q R S:
    BD21's aimed recoil (4 5 6). ADS N O P / hold P: BD21 aim pose = ready 2.
  - T front -> 2; U V W X swung aside (sprint / kick / slide) -> authored sprint pose 1.
  - MP42 (dual -> single switch: the kept gun stays up) -> ready 2. PP40 = purist MP40.
"""


def _expand(spec):
    """'MP4R': 'A7 B7 ...' -> {('MP4R','A'): 7, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A ready | B-D raise | E F front | G-I raise | J-M lower | N O P ADS (aim = ready)
    # Q R S aimed fire | T front | U-X swung aside (sprint pose)
    'MP40': 'A2 B3 D5 E6 F2 G1 H1 I0 J2 K1 L1 M0 N2 O2 P2 Q4 R5 S6 '
            'T2 U1 V1 W1 X1',
    'PP40': 'A2 B3 D5 E6',
    # A-G hand to the cocking handle (bolt still home) | H pull (Bolt1) | I-K held back
    # L-V hand to the magazine, bolt back (hub 9) | W X Y Z mag pulled & dropped
    # (Reload1) | [ \ ] mag gone. Reversed in FullReload / Bolt after Bolt2.
    'MP4R': 'A7 B7 C7 D7 E7 F7 G7 H8 I9 J9 K9 L9 M9 N9 O9 P9 Q9 R9 S9 T9 U9 V9 '
            'W10 X11 Y12 Z13 [13 \\13 ]13',
    # A B empty well | C-H new mag rising, in the well at H (Reload2) | I-N hand on mag
    # O P Q R turn in (tactical) / out (U T R Q P O) | S-Y hand at mag
    # Z [ \ ] tactical mag out (Reload1 before Z)
    '2P4R': 'A13 B13 C13 D13 E12 F11 G10 H9 I9 J9 K9 L9 N9 O8 P8 Q9 R9 '
            'S9 T9 U9 V9 W9 X9 Y9 Z10 [11 \\12 ]13',
    # A-E empty well | F-J new mag rising, in the well at J (Reload2) | K-P hand on mag
    # Q R S T turn (after unload in / unload end out) | U V first-pickup rise
    '3P4R': 'A13 B13 C13 D13 E13 F12 G12 H11 I10 J9 K9 L9 M9 N9 O9 P9 '
            'Q8 R8 S9 T9 U0 V1',
    # first pickup: E F rising, G H turning into the reload posture
    '5P4R': 'E1 F7 G8 H9',
    # dual -> single switch: the kept gun is at ready throughout
    'MP42': 'O2 P2 Q2 R2 S2 T2 U2 V2',
})

MESH_FRAMES = 14
