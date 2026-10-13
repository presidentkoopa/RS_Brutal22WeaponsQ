"""Rifle (BD22 class Rifle) -> meshes/Rifle.md3 (32 frames).

MESH (BD21 Modeldef.Rifle.def + Rifle.txt + parts.py ref 3; surfaces: Runko =
body, Lipas = magazine, liikkuvat + ejectport = charging handle/bolt and dust
cover; 'cant' = roll of the body that turns the magwell toward the player):
   0-2  raise (0 lowest)                  3  READY
   4    fire: gun kicked back 2           5  bolt back, port open (ejection)
   6    returning (bolt closed)           7  = ready (reload start, BD21 RIFR A)
   8    cant 0.6 deg, mag in
   9    OLD MAG OUT: magazine 36 units below the well (dropped), cant 2
  10-14 new magazine rising: 19.5, 17.7, 16.9, 12.8, 4.1 below; cant 4 -> 16
  15    MAG SEATED, cant 18               16  cant peak 20     17  cant 18
  18-24 charging handle: back 0.6, 2.4, 4.7, 6.5, 7.1 (full, 22), forward
        5.4 (23), 1.7 (24) while the cant returns 16 -> 1.4
  25    bolt home, cant 0.4               26  = ready
  27-29 zoom (RIFZ A-C) = ready geometry  30  sprint pose (yaw 45, lowered)
  31    yaw 45 at ready height (between ready and the sprint pose)
  The only canted poses with magazine seated and bolt closed are 15-17 (and 18,
  bolt 0.6).  Between them and level there are only the charging frames, so a
  level <-> canted change without a bolt pull has to be one step (see SNAP).

BD22 SPRITES: RIFG A ready, B-E lower (B lowest), F-I raise (I lowest), J-N
  swing aside (sprint/kick).  RIFF A/D fire (alternating flash), B C recover,
  E-I grenade shot.  RI2G/RI2F = aimed copies, RIFZ A-C aim in.  2IFG/2IFF =
  purist copies.  RIFR A-F roll the gun over, G H empty magwell (EmptyClipSpawn
  after G G), I-P new mag brought up, Q going in, R seated, S-X hand holds the
  seated mag, Y Z [ roll back.  2IFR A-H hand to the charging handle, I J pull
  (J held back), K-O release, P upright.  3IFR A-F first-pickup raise with an
  EMPTY magwell.  RIGL/RIG2 underbarrel grenade reload (gun on its side, mag
  in); 1IGL/1IG2 the same with the rifle unloaded.  DURR J-Q switch from dual
  rifles back to one.

ANCHORS: Rifle/Reload1 (RIFLER1) rattle runs D..H, EmptyClipSpawn after G G
  -> mesh 9 from G.  Rifle/Reload2 (RIFLER2) starts at the first O and peaks
  5-6 tics later = Q R -> Q14, R15 seated.  Rifle/Bolt1 at 2IFR I (J is the
  held-back pose, InspectHold holds J) -> J22; Rifle/Bolt2 at K, peak at L ->
  K23, L25 bolt home.  RifleCaseSpawn on RIFF B -> 5 (port open).

MAPPING
  RIFR  A7 B8 C8 D8 E8 F8 | G9 H9 | I10 J10 K11 L11 M12 N13 O13 P13 Q14 R15 |
        S15 T15 U16 V16 W16 X16 Y17 Z18 | [8
        N O P (and the N after O O) all hold 13: BD22's N-O-N-P jiggle at the
        well entrance stays in one posture, no reversal.
  2IFR  A-H 25 | I24 J22 K23 L25 M25 N25 O25 P26  (charge near level: pull
        25->24->22, release 22->23->25)
  RIFG  A3 | lower E3 D2 C1 B0 | raise I0 H1 G2 F3 | aside J3 K3 L31 M30 N30
  RIFF  A4 D4 B5 C6 | grenade E4 F4 G6 H6 I3 (kick, no bolt cycle)
  RI2F  same letters as RIFF; RI2G A3; RIFZ A27 B28 C29; 2IFG A3; 2IFF as RIFF
  3IFR  A0 B1 C2 D9 E9 F9 (raise, then the empty magwell from D)
  RIGL  A7 B8 C8 D18 E17 F-Z16; RIG2 A-E 16; 1IGL/1IG2 = RIGL/RIG2 (the mesh
        cannot hide its magazine)
  DURR  Q P O N M L 31 (gun turned 45 deg), K J 3

SHARED LETTERS (one pose must read right everywhere):
  RIFR B opens every reload (A B C) and also sits between [ and the bolt pull
  (empty reload) or B A (round chambered), and in Unload (A B [ / C B A).
  Only a level pose works in the opening, so B = 8, and therefore [ = 8 too:
  if [ were canted the empty reload would flick canted -> level -> canted.
  Y Z [ also open the Unload in reverse ([ Z Y X W V) and still read in order.
  RIFR C-F are also the end of Unload (mag already out); they keep the
  magazine (8) because the reload needs it in until G.

SNAP: Z18 -> [8 (15.6 -> 0.6 deg cant) in every reload, [8 -> Z18 in Unload,
  C8 <-> D18 in the grenade reload: one-tic, one-way steps where BD22's art
  makes its fastest roll (side view <-> rear view).  The mesh has no
  canted-and-bolt-closed frames between those two cants.

SELF-CHECK (pose lists in BD22 order):
  Fire          4 5 6 3            Fire aimed   4 5 6 3 3x10
  Grenade shot  4 4 6 6 3          aim in 27 28 29 3 / out 28 27 3
  Reload, empty (Reload -> FinishReloading):
    7 8 8 8 8 8 9 9 | 9x3 | 10 10 11 11 12 13 13 13 | 13 13 13 13 14 15 |
    15 15 16 16 16x3 16 16 17 18 | 8 8 | 25x7 25x3 | 24 22 22 22 | 23 23 25 25
    25 25 26 -> 3
  Reload, round chambered (-> FullReload):
    ... 14 15 | 15 15 16 16 16x3 16 16 17 18 | 8 8 8 7 -> 3
  First pickup (Tacticalselect):
    0 1 2 9 9 9 | 9 9 9x2 | 10 10 11 11 12 13 13 13 | 13 13 13 13 14 15 15 15
    16 16 | 16x3 16 16 17 18 | 8 8 | 25x7 25x3 | 24 22 22 22 | 23 23 25 25 25
    25 26 -> 3
  Unload  7 8 8 18 17 16 16 16x3 | 14 13 13 13 12 11 11 10 10 9 9 8 8 8 8 8 7
  Inspect 26 25 25 | 25x5 25x5 | 24 24 22 22 22x2 | 23 23 25 25 | 25x4 25 25 26
  Grenade reload 7 8 8 | 18 17 16 ... 16 | RIG2 16 | 16 ... 16 17 18 8 8 7
  Select 0 1 2 3   Deselect 3 2 1 0   Sprint 3 3 31 | 30 ... | 31 3 3
  Kick 3 3 31 30 30x10 30 31 3 3     Dual -> single 31 x6 3 3
  No reload sequence ever returns to 3/7/26 before its end, the magazine
  leaves once (G) and seats once (R), the bolt is pulled once (2IFR I-L).

JUDGEMENT CALLS
  * BD22 rolls the gun before the magazine comes out (A-F); the mesh only
    cants while the new magazine rises, so A-F stay level (7/8).
  * Round-chambered reload (no bolt pull in BD22) returns to level via the
    Z->[ snap; showing the mesh's canted charge there would be a bolt pull
    BD22 does not have, and in the empty reload it would be pulled twice.
  * Unload ends with C-F/B/A showing a magazine again (the mesh has no
    empty-magwell ready pose; Ready shows one anyway).
  * Grenade reload: the mesh has no launcher; the gun holds the canted,
    bolt-closed pose 16 while BD22 works the launcher.
"""


def _expand(spec):
    """'RIFR': 'A7 B8 ...' -> {('RIFR','A'): 7, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


_FIRE = 'A4 B5 C6 D4'
_GRENADE_SHOT = 'E4 F4 G6 H6'
_RIGL = ('D18 E17 F16 G16 H16 I16 J16 K16 L16 M16 N16 O16 P16 Q16 R16 S16 '
         'T16 U16 V16 W16 X16 Y16 Z16')
_RIG2 = 'A16 B16 C16 D16 E16'

TABLE = _expand({
    'RIFG': 'A3 B0 C1 D2 E3 F3 G2 H1 I0 J3 K3 L31 M30 N30',
    'RIFF': _FIRE + ' ' + _GRENADE_SHOT + ' I3',
    'RI2F': _FIRE + ' ' + _GRENADE_SHOT,
    'RI2G': 'A3',
    'RIFZ': 'A27 B28 C29',
    '2IFG': 'A3',                          # purist copy of RIFG A
    '2IFF': _FIRE,                         # purist copy of RIFF A-D
    'RIFR': 'A7 B8 C8 D8 E8 F8 G9 H9 I10 J10 K11 L11 M12 N13 O13 P13 Q14 '
            'R15 S15 T15 U16 V16 W16 X16 Y17 Z18 [8',
    '2IFR': 'A25 B25 C25 D25 E25 F25 G25 H25 I24 J22 K23 L25 M25 N25 O25 P26',
    '3IFR': 'A0 B1 C2 D9 E9 F9',
    'RIGL': 'A7 B8 C8 ' + _RIGL,
    'RIG2': _RIG2,
    '1IGL': _RIGL,                         # unloaded copy of RIGL D-Z
    '1IG2': _RIG2,                         # unloaded copy of RIG2
    'DURR': 'J3 K3 L31 M31 N31 O31 P31 Q31',
})
