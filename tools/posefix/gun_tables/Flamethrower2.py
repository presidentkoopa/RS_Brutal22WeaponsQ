"""Flamethrower2 (BD22 class Flamethrower2 / PuristFlamethrower2)
-> meshes/Flamethrower2.md3 (6 frames).

Mesh frame meanings (BD21 def Modeldef.Flamethrower2.def + Flamethrower.txt +
parts.py / pose_axis.py / vertex-distance matrix):
   0-2   ready idle: body still, only the pilot-light cylinder flickers
         (0.0 / 0.1 / 0.2); BD21 Ready played FLMT A B C = 0 1 2
   3-4   firing: body pushed back 1 unit, nozzle parts jitter; BD21 played
         FLMT D E = 3 4 alternating for the whole flame stream
   5     pickup (BD21 FLMT F, ROTATING spawn model) -- not shown in hand
   no select/lower frames, no sprint pose, no reload (the gun has none).

BD22 sprite art (FLMT): A B C ready, blue pilot flame flickering | D E G H
firing, flame burst | I J K L raise (I lowest) | M N O P lower (P lowest) |
Q ready, pilot flame out (dry / underwater / no gas) | R S T U V gun swung
aside for sprint/kick/slide (R ~ ready, V furthest).

BD22 sequences -> poses produced by TABLE (self-check):
   Select      TNT1, FLMT I J K L -> 0 0 0 0, then Ready
   Ready       FLMT A B C (loop) -> 0 1 2
   ReadyDry    FLMT Q (loop) -> 0
   Fire        FLMT D -> 3
   Hold loop   E D G H  E D G H  E D G H -> 4 3 4 3  4 3 4 3  4 3 4 3,
               refire loops back to E (4) -- strict 3/4 alternation all the
               way through, as BD21 played D E; release -> Ready+6 (A B C)
   Deselect    FLMT M N O P -> 0 0 0 0, then lowered off-screen
   StartSprint FLMT R S T -> 0 0 0, Sprinting U -> 0, StopSprint T S R -> 0
   KickFlash   R S T U, V x10, U T S R -> all 0 (SlideFlash* likewise)
   NoAmmo      inherited "####" "#" -> keeps whatever letter was shown
   Purist      2LMT A B C D E G H Q -> same as FLMT (same art);
               2LMT M N O P (only reachable through the "####" deselect) -> 0

Judgement calls:
 - G and H are given the opposite fire frame from E and D (G=4, H=3) so the
   BD22 order E D G H plays 4 3 4 3: an even flame jitter with no repeated
   frame, matching BD21's D E alternation.
 - Raise/lower (I-P), dry ready (Q) and swing-aside (R-V) are the ready pose
   0: the mesh has no select, sprint or pilot-off frames, and BD21 showed the
   ready pose for all of them.
"""


def _expand(spec):
    """'FLMT': 'A0 B1 ...' -> {('FLMT','A'): 0, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A B C idle (pilot flicker) | D E G H flame, alternating 3/4 in BD22 order
    # I-L raise, M-P lower, Q dry ready, R-V swung aside: all ready (0)
    'FLMT': 'A0 B1 C2 D3 E4 G4 H3 I0 J0 K0 L0 M0 N0 O0 P0 Q0 '
            'R0 S0 T0 U0 V0',
    # purist copy: same letters, same art
    '2LMT': 'A0 B1 C2 D3 E4 G4 H3 M0 N0 O0 P0 Q0',
})
