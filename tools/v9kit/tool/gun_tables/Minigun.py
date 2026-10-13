"""Minigun (BD22 class MiniGun) -> meshes/Minigun.md3 (16 frames).

MESH (BD21 Modeldef.Minigun.def + Minigun.txt + parts.py/mg_rot.py on the 'Pipe'
surface, which is the barrel cluster and spins about the bore axis):
   0-3  raise (0 lowest, pitch -31 deg .. 3 pitch -6); 3 is also the authored
        sprint pose (BD21 CHSP A -> 3).  BD21 played CHGS ABCD = 0..3 up,
        DCBA down.
   4-7  barrel spin cycle, trigger released, no recoil.  Barrel roll about the
        bore: 4 = 0 deg (READY / rest), 5 = 25.6, 6 = 80.4, 7 = 106.0, and the
        next 4 is 120 (= 0 again, the barrel cage is 3-fold).  BD21 idle spin
        Ready2 = CHAG ABCD 1 tic = 4,5,6,7,4,...  This +1-per-tic order is the
        only authored rotation, so every spin below steps through it in that
        order; a frame is never skipped where it can be avoided (a skip is a
        larger, direction-ambiguous jump) and never stepped backwards.
   8-11 the same four barrel angles with the TRIGGER PULLED (trigger surface
        rotated 20 deg); 8 and 10 also have the whole gun kicked back 2 units
        (recoil).  BD21 Hold = CHAF ABCD 1 tic = 8,9,10,11 with shots on 8, 10.
  12-15 geometric copies of 4-7 (BD21 CHAE = no-ammo idle).  Not needed: CHAE
        takes the CHAG pose for the same letter (identical art minus the belt).
  Write-up below uses positions P0..P3 = barrel angle 0/25.6/80.4/106.

BD22 SPRITES (spr.py sheets):
  CHAG A-F  six barrel-rotation steps of the ready gun (A = rest).
  CHAG H-L  gun swinging aside (left/down) for sprint/kick; L fully aside.
  CHAG M-P  the same swing while spinning (blurred), Q-T aside + spinning.
  CHAG U-X  raise (U lowest)   CHAG Y-]  lower (] highest, Y lowest).
  CHAE      the same letters with an empty belt (no ammo).
  CHAF A-F  spun-up firing (flash on A C E); G-O fire from rest (flash on
            G J M); P Q dry spin while spun up; R S T dry spin (no ammo).
  CHAV G-O  purist copy of CHAF G-O.
  CHAS A-T  first-pickup belt loading, gun steady at the ready pose.

MAPPING
  CHAG/CHAE A4 B5 C5 D6 E7 F7.  Forced by Ready2 (A C D E loop) = 4 5 6 7, the
     authored idle spin.  B and F fall between those: B5 / F7 make the BD22
     6-step letter run ABCDEF = 4 5 5 6 7 7 (one revolution in 6 tics, a
     slower spin than Ready2's 4) and Fire's wind-up ABDF = 4 5 6 7 (every
     barrel angle once, then the first shot on 8).
  CHAF G-O  G8 H9 I10 J11 K8 L9 M10 N11 O8 = the authored BD21 fire cycle
     8 9 10 11 played continuously; the 9-tic BD22 loop gets one repeated 8 at
     the O->G seam (9 tics cannot hold a whole number of 4-frame turns).
     Shots: G on 8 (kick), J on 11, M on 10 (kick).
  CHAF A-F  A8 B9 C10 D10 E11 F11 (spun-up fire: one turn per 6-tic loop like
     BD22's own A-F run; shots A on 8 and C on 10 kick, E on 11).  F11 -> A4
     of Ready2 is the next authored step.
  CHAF P9 Q11 dry spin while spun up: trigger held, no recoil; BD22's art is a
     2-frame P/Q blur alternation and so is this.
  CHAF R4 S5 T6 dry spin (no ammo) after a cold trigger pull: spin frames
     without recoil (no rounds fire); T6 -> EndSpin D6 keeps the angle.
  Swing aside H4 I4 J3 K3 L3 and M4 N4 O3 P3, Q R S T 3: sprite J/O are past
     half-way aside (21 of 36 px), so the authored sprint pose 3 takes over
     there; H I M N barely move.  The mesh has no spinning-while-aside frames,
     so the spin-kick's Q-T hold the sprint pose (judgement call).
     The same letters play reversed on the way back (K J I H / P O N M):
     3 3 4 4 reads right both ways.
  Raise U0 V1 W2 X3, lower ]3 [2 Z1 Y0 (authored CHGS ABCD / DCBA).
  CHAS -> 4 (gun steady at ready while the hand feeds the belt).
  CHAV G-O = CHAF G-O.

SELF-CHECK (pose lists in BD22 order, 1 tic each unless noted):
  Ready              4
  Ready2 (spinning)  4 5 6 7 | loop
  AltFire spin-up    4 5 5 6 7 7 -> Ready2 4 5 6 7 ...
  Fire (from rest)   4 5 6 7 -> Hold
  Hold (normal)      8 9 10 11 8 9 10 11 8 | loop  (shots on 8, 11, 10)
  Hold (tactical: H K N skipped)  8 10 11 9 10 8 | loop
  EndSpin            6 7 5 6 7 4 5 6 7 | 4 5 5 6 7 7 | 4 5 5 6 7 7 |
                     4 5 5 6 7 7 (2 tics each) | 4 5 5 6 (3 each) | 7 7 (4 each)
                     -> Ready 4   (barrels always turn forward, tics lengthen)
  HoldSpin (normal)  8 9 10 10 11 11 | loop -> Ready2 4 5 6 7
  HoldSpin (tactical: B D F skipped) 8 10 11 | loop
  StopAlt            4 5 6 7 4 5 6 7 7 | 4 5 5 6 7 7 x2 | (2 tics) | 4 5 5 6 (3)
                     | 7 7 (4) -> 4
  HoldEmpty          4 5 6 4 5 6 4 5 6 -> EndSpin 6 7 5 ...
  HoldSpinEmpty      9 11 9 11 9 11 -> Ready2 4 ...
  Select             0 1 2 3 -> 4
  First select       0 1 2 3 | CHAS 4 x24 -> 4
  Deselect           3 2 1 0
  Sprint             4 4 3 | 3 x14 per pass | 3 4 4 -> 4
  Kick               4 4 3 3 3(10) 3 3 4 4
  Spin kick          4 4 3 3 | 3 x10 | 3 3 4 4
  Spin slide         4 4 3 3 | 3 (10+25) ; end 3 3 3 3 3 | 3 3 4 4

JUDGEMENT CALLS
  * Wind-up: BD22 gives only 4 tics (ABDF) before the first shot; it now
    turns through every barrel angle (4 5 6 7) and the first shot lands on the
    kicked frame 8.  AltFire spin-up turns at 6 tics/rev then Ready2 at 4.
  * Spin-down: EndSpin/StopAlt step forward every frame and slow only by
    BD22's own lengthening tics; BD22's D F C opening run skips once (7->5).
  * Leaving Hold (O8 -> EndSpin D6) jumps two barrel steps once per burst;
    the alternative O11 would step backwards.
  * Tactical class (TacticalDoomer only; default classes are non-tactical)
    skips letters, so its fire loops contain skips; unavoidable with fixed
    letter->frame keys.
"""


def _expand(spec):
    """'CHAG': 'A4 B5 ...' -> {('CHAG','A'): 4, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


_CHAG = ('A4 B5 C5 D6 E7 F7 '              # spin cycle (A = ready)
         'H4 I4 J3 K3 L3 '                 # swing aside (sprint / kick)
         'M4 N4 O3 P3 Q3 R3 S3 T3 '        # swing aside while spinning
         'U0 V1 W2 X3 '                    # raise
         'Y0 Z1 [2 ]3')                    # lower (played ] [ Z Y)

_CHAF_HOLD = 'G8 H9 I10 J11 K8 L9 M10 N11 O8'

TABLE = _expand({
    'CHAG': _CHAG,
    'CHAE': _CHAG,                         # no-ammo copy of CHAG
    'CHAF': 'A8 B9 C10 D10 E11 F11 ' + _CHAF_HOLD + ' P9 Q11 R4 S5 T6',
    'CHAV': _CHAF_HOLD,                    # purist copy of CHAF G-O
    'CHAS': 'A4 B4 C4 D4 E4 F4 G4 H4 I4 J4 L4 M4 N4 O4 P4 Q4 R4 S4 T4',
})
