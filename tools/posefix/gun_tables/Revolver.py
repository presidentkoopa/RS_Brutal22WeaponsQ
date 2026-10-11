"""Revolver -> Revolver.md3 (33 frames)

Mesh (BD21 authored def + parts.py, ref frame 0):
  0 ready | 1-2 hammer back | 3-10 fire: kick up, settle | 11-17 re-cock, cylinder
  indexes, back to ready (17 == 0) | 18-22 gun rolls onto its side | 23 cylinder
  swinging out | 24 cylinder out | 25-27 tilting up, cylinder facing (26 = loading
  posture, chambers full) | 28-29 shells pushed out (29 = empty) | 30-31 level, open
  32 sprint pose

BD22 (Revolver.dec):
  Reload  REVR A B C D E F F 0 18 19 20 21 22 22 | Open | G H I J K K K 23 24 24 25 25 25 25
          L M N O P Q 26 (Q 2 tics)
  each shell (InsertShellAnimation; BD22 spawns one spent casing per shell)
          Z R S T T U V W X Y 26 27 27 26 26 26 26 26 26 26  -- stays open, stays tilted
  close   Q P O N M L 26 | K J I H 25 25 24 24 | Close | G 23, F E E D C B 22 21 21 20 19 18, A 0
          (old mapping put N-Z on the ready pose: the cylinder shut during the shell loop
          and opened again to close -- the owner's complaint)
  Reload after unload / speedloader REVR A-F, REVU A B C D E E F G H I 24 24 25 25 25 25
          26 26 27 28, J K... 29 (empty chambers), L M N 29, O O P.. Q Q R 28 28 27.. 26 26 26
          then the close above
  Unload  opening as Reload, then REVU S T 27 28, K 29, J I H G F E D C B A 29 28 27 26 26
          25 25 25 24 24, Close, REVR G-A
  Fire    REVO B-K 1-10, hammering L-R 11-17, S-W 0 | sprint / kick X 0, Y Z [ \ 32
Judgement: REVR A opens and closes every reload, so it is the ready pose (0).
"""
def _x(spec):
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out

_REVO = 'A0 B1 C2 D3 E4 F5 G6 H7 I8 J9 K10 L11 M12 N13 O14 P15 Q16 R17 S0 T0 U0 V0 W0 X0 Y32 Z32 [32 \\32'
TABLE = _x({
    'REVR': 'A0 B18 C19 D20 E21 F22 G23 H24 I24 J25 K25 L26 M26 N26 O26 P26 Q26 '
            'R27 S27 T26 U26 V26 W26 X26 Y26 Z26',
    'REVU': 'A24 B24 C25 D25 E25 F26 G26 H27 I28 J29 K29 L29 M29 N29 O28 P27 Q26 R26 '
            'S27 T28 U26 V26 W26',
    'REVO': _REVO,
    '2EVO': ' '.join(t for t in _REVO.split() if t[0] in 'ABCDEFGHIJKLMNOPQRSTUVW'),
    'REVS': 'A0 B0 C0 D0 E0 F0 G0 H0 I0 J0 K0 L0',
    'R3VO': 'A0 B32 C32 D32 E32',
})
