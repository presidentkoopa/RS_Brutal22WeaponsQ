"""Unmaker (BD22 class Unmaker / PuristUnmaker) -> meshes/Unmaker.md3 (16 frames).

Mesh frame meanings (BD21 def Modeldef.Unmaker.def + Unmaker.txt + parts.py /
pose_axis.py / vertex-distance matrix / side renders):
   0-3   ready idle: body still, only the small glowing part drifts 0 -> 0.4
         (BD21 Ready played UNHG ABCDD DCBA AAAA = 0 1 2 3 3 3 2 1 0 0 0 0 0)
   4-7   select/lower: gun tips nose-down and drops away; 4 = just below ready
         (pitch -5), 5 (-19), 6 (-33), 7 = lowest (-39, 62 units from ready)
   8     fire start = ready pose (0.4 from frame 0)
   9-11  spin-up: gun draws back 1 -> 5 units
   12-15 firing: drawn back, jittering (12 back, 13 right, 14 down, 15 left)
   no sprint pose, no reload (the gun has none).

BD22 sequences -> poses produced by TABLE (self-check):
   Select      TNT1, UNHS A B C D -> 7 6 5 4, then Ready 0 1 2 3 3 ...
               (BD21 keyed UNHS A-D to 4..7, i.e. the gun dropping, then snapped
               to ready; BD22's UNHS A is the LOWEST art, so the raise runs
               7 -> 4: lowest at the start, rising into ready.)
   Deselect    UNHS E F G H -> 4 5 6 7, then TNT1 (E high ... H lowest, as the art)
   Ready       UNHG ABCDD DCBA AAAA -> 0 1 2 3 3 | 3 2 1 0 | 0 0 0 0
   Fire        UNHF A B C D -> 8 9 10 11 (spin-up, gun drawing back)
   Hold loop   UNHF E F G H -> 12 13 14 15, repeats while held
   Release     UNHF D C B A -> 11 10 9 8 -> Ready 0 (BD22's own reversal)
   NoAmmo      UNHG C D D C B A -> 2 3 3 2 1 0 (dip is a sprite offset only)
   StartSprint UNHG E F G -> 0 0 0, Sprinting UNHG H -> 0, StopSprint G F E -> 0
   KickFlash   UNHG E F G H, I x10, H G F E -> all 0
   SlideFlash* UNHG E..I / I, H..E -> all 0
   Purist      2NHG A-D -> 0 1 2 3; 2NHF A-H -> 8..15 (same art as UNHG/UNHF)

Judgement calls:
 - UNHG E-I is the gun swung aside (sprint, kick, slide). The mesh has no
   sprint pose and BD21 showed the ready pose (UNHG A) while sprinting, so
   these are the ready pose 0 -- no jump into the lowering frames mid-kick.
 - The raise order is reversed relative to BD21's keying (see Select above),
   so the gun no longer pops from lowered straight to ready.
"""


def _expand(spec):
    """'UNHG': 'A0 B1 ...' -> {('UNHG','A'): 0, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A-D idle (authored 0..3) | E-I swung aside for sprint/kick/slide: ready
    'UNHG': 'A0 B1 C2 D3 E0 F0 G0 H0 I0',
    # A-D raise, lowest first (7 -> 4) | E-H lower (4 -> 7)
    'UNHS': 'A7 B6 C5 D4 E4 F5 G6 H7',
    # A-D spin-up 8..11 (also played D-A on release) | E-H firing 12..15
    'UNHF': 'A8 B9 C10 D11 E12 F13 G14 H15',
    # purist copies: same letters, same art
    '2NHG': 'A0 B1 C2 D3',
    '2NHF': 'A8 B9 C10 D11 E12 F13 G14 H15',
})
