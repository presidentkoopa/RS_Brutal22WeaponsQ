"""DSweap / Dragonslayer (BD22 Dragonslayer.dec, posefix copy) -> meshes/DSweap.md3 (10 frames).

MESH FRAME MEANINGS (BD21 def + Dragonslayer.txt + pose_axis.py / top & front renders)
  0   ready: sword upright (+70 deg)                         (DSLA A)
  1   cocked: blade pointing right, ~20 deg up                (DSLA B, the Hold)
  2   the cut: blade level, pointing forward-right            (DSLA C, the blur)
  3   swung through to the left                               (DSLA D, unused by BD22)
  4   on the left, start of the return cut                    (DSLA E)
  5-8 guard: upright (5) lowering to forward-right-down (8)   (DSLC A-D)
  9   one step past 8, unused

  The DSLA / DSLC art and order are BD21's unchanged (BD22 only changed the
  swing sound and, via posefix, the hold frames), so the authored BD21 frame
  for each letter IS the same moment.  The sweep across the screen is carried
  by the sprite offsets (Offset(-50..-620, ...)), which QZD applies to HUD
  models as yaw/pitch (hw_weapon.cpp: rotation += (mx/4, (my-32)/-4)), as it
  did for BD21's VR def.

BD22 SEQUENCES -> POSES (self-check, BD22 order)
  Ready / Select / Deselect / Kick / Slide (posefix)  DSLA A -> 0
  Fire     DSLC A B C D | DSLA B | DSLA C x7 (offsets sweep it left)
           | DSLC D x19 (posefix hold, waits for Attack2) | DSLC D D | DSLC D C B A
           -> 5 6 7 8 | 1 | 2 x7 | 8 x19 | 8 8 | 8 7 6 5 -> 0
  Attack2  DSLA E x7 (offsets sweep it right) | DSLC D x6 | D D | D C B A
           -> 4 x7 | 8 x6 | 8 8 | 8 7 6 5 -> 0
  DSLC A-D is played forward (guard) and backward (recovery): 5..8 reads as
  lowering then raising, right in both.

JUDGEMENT CALLS
- Same frames as the current mapping: the authored BD21 def already matches
  BD22's code letter for letter.  Nothing in this mesh shows a held-right or
  held-left end of the cut, so the posefix hold letter DSLC D stays on 8 (the
  low guard the recovery rises from).
"""

TABLE = {
    ('DSLA', 'A'): 0,
    ('DSLA', 'B'): 1,
    ('DSLA', 'C'): 2,
    ('DSLA', 'E'): 4,
    ('DSLC', 'A'): 5,
    ('DSLC', 'B'): 6,
    ('DSLC', 'C'): 7,
    ('DSLC', 'D'): 8,
}

MESH_FRAMES = 10


def _selfcheck():
    T = TABLE
    seqs = [
        ('Fire', [('DSLC', c) for c in 'ABCD'] + [('DSLA', 'B')] + [('DSLA', 'C')] * 7
         + [('DSLC', 'D')] * 21 + [('DSLC', c) for c in 'DCBA'] + [('DSLA', 'A')]),
        ('Attack2', [('DSLA', 'E')] * 7 + [('DSLC', 'D')] * 8 + [('DSLC', c) for c in 'DCBA'] + [('DSLA', 'A')]),
    ]
    for name, seq in seqs:
        print('%-8s %s' % (name, ' '.join(str(T[k]) for k in seq)))


if __name__ == '__main__':
    _selfcheck()
