"""HellishMissileLauncher (BD22) -> meshes/HellishMissile.md3 (10 frames).

Mesh frame meanings (BD21 def Modeldef.HellishMissile.def: A->0, B..I->1..8,
J->9; no BD21 weapon code exists. Meaning taken from parts.py / pose_axis.py /
vertex-distance matrix / side renders -- one launcher, one surface):
   0     ready
   1-3   recoil kick #1: 1 = slammed back 35 units (pitch +3.5), 2 = back 30
         with the nose kicked up (pitch +7), 3 = returning (back 12)
   4     ready (vertex-identical to 0)
   5-7   recoil kick #2: 5 = back 25 (pitch +3.5), 6 = back 30 nose up
         (pitch +7, the peak), 7 = returning (back 15)
   8     ready (identical to 0)
   9     ready (identical to 0; BD21's "no target?" J)
   no select/lower frames, no sprint pose, no reload (the gun has none).

BD22 sprite art (RVCG, two shoulder launchers; measured from the PNGs):
   A ready | B C left launcher fires (flash, launcher still in place; missile
   spawned on B) | D E left launcher kicked back (D peak, E 88%) | F ~45% |
   G ~12% | H I right fires | J K right kicked back | L ~45% | M ~12% |
   Q P O N raise (Q lowest) | N O P Q lower.

BD22 sequences -> poses produced by TABLE (self-check):
   Select      TNT1, RVCG Q P O N -> 0 0 0 0, then Ready A -> 0
   Deselect    RVCG N O P Q -> 0 0 0 0, then TNT1
   Ready       RVCG A -> 0 (sprint, taunt, grenade toss, kick/slide flash: A -> 0)
   Fire (left) RVCG B C D E F G A -> 1 1 2 2 3 4 0   (kick #1)
   OpenFire2   RVCG H I J K L M A -> 5 5 6 6 7 8 0   (kick #2; alternates
               with the left shot on every trigger pull)
   NoAmmo      A x5 -> 0
   Purist      PVCG B-M -> same poses as RVCG B-M (same art); PVCG A is
               only ever a 0-tic state.

Judgement calls:
 - Kick on the launch letter. BD22's art keeps the launcher in place for the
   two flash letters (B C / H I) and shows the recoil from D / J. The model
   has no muzzle flash, so the only fire cue in VR is the kick, and BD21's
   author keyed the launch letter B to the kick frame 1. So B/H take the
   first kick frame, D-E / J-K the peak (2 / 6, the nose-up frames, matching
   the art's 100%/88%), F / L the returning frame (3 / 7, ~35-50%), and G / M
   (art ~12%) the ready frame, so A follows with no jump.
 - The left shot uses kick #1 and the right shot kick #2 so successive shots
   differ a little, as the alternating art does.
 - Q P O N / N O P Q (raise/lower) are the ready pose: the mesh has no select
   frames and BD21 showed none either.
"""


def _expand(spec):
    """'RVCG': 'A0 B1 ...' -> {('RVCG','A'): 0, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A ready | B C launch, D E peak, F returning, G back (kick #1)
    # H I launch, J K peak, L returning, M back (kick #2)
    # N O P Q raise/lower: no select frames in the mesh -> ready
    'RVCG': 'A0 B1 C1 D2 E2 F3 G4 H5 I5 J6 K6 L7 M8 N0 O0 P0 Q0',
    # purist copy: same letters, same art
    'PVCG': 'A0 B1 C1 D2 E2 F3 G4 H5 I5 J6 K6 L7 M8',
})
