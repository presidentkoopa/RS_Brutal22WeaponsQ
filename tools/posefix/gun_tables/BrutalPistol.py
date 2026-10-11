"""BrutalPistol -> BrutalPistol.md3 (38 frames)

Mesh (BD21 authored def + parts.py, ref frame 3):
  0-2 raise (rot 45 -> 0) | 3 ready (PIST A) | 4-7 fire, hammer/slide kick
  8 slide locked back | 9 old magazine gone | 10-18 new magazine rising while the
  gun rolls to ~21 deg | 19-20 seated | 21-25 slide runs forward, gun rolls back
  26 level, done | 27 sprint pose | 28-37 aim/spin set (unused by BD22)

BD22 (Pistol.dec):
  Reload (round chambered, 2ISR) A-D 3 | E-G 8 | H-J 9 (mag out, Pistol/Reload1 at start)
      K-O 10 11 13 15 17 (new mag, Pistol/Reload2 after O) | P Q R S S 19 19 20 20 20
      T (pistol/slide2) U V 21 22 23 | PISR T T U V W 23 23 24 25 26 | PISR D C B A 3
  Reload2 (empty, PISR) A-D 3 | E-G 8 | H-J 9 | K-O 10 11 13 15 17 | P Q R S T T U V W
      19 19 20 21 23 23 24 25 26 | D C B A 3
      (old mapping played D C B A as 11 10 9 8: the magazine dropped out and went in a
      second time -- the owner's "inserts the clip twice")
  Unload PISR A-D 3, W V U T S S 26 25 24 23 21 21, 2ISR S O N M K J I I H G
      20 17 15 13 10 9 9 9 9 8, F E D C B A 8 8 3 3 3 3
  Fire #### A B C D E 3 4 5 6 7 | select PISS A B C 0 1 2 (empty G H I same)
  deselect PISS D E F / J K L 2 1 0 | dual-switch PI2G L-G / X-S raise 0 0 1 1 2 3
  sprint / kick PIST J K L M N and O P Q R S: 3 27 27 27 27 (swung aside = sprint pose)
  inspect PISI A-E 3, F G H (slide pulled, pistol/slide) 8, I.. (slide2) 3
Judgement: A-D open AND close every reload, so they are the ready pose (3).
"""
def _x(spec):
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out

TABLE = _x({
    'PISR': 'A3 B3 C3 D3 E8 F8 G8 H9 I9 J9 K10 L11 M13 N15 O17 P19 Q19 R20 S21 T23 U24 V25 W26',
    '2ISR': 'A3 B3 C3 D3 E8 F8 G8 H9 I9 J9 K10 L11 M13 N15 O17 P19 Q19 R20 S20 T21 U22 V23',
    'PIST': 'A3 B4 C5 D6 E7 I3 J3 K27 L27 M27 N27 O3 P27 Q27 R27 S27',
    '2IST': 'A3 B4 C5 D6 E7 I3',
    'PISS': 'A0 B1 C2 D2 E1 F0 G0 H1 I2 J2 K1 L0',
    'PI2G': 'G3 H2 I1 J1 K0 L0 S3 T2 U1 V1 W0 X0',
    'PISI': 'A3 B3 C3 D3 E3 F8 G8 H8 I3 J3 K3 L3 M3 N3 O3 P3 Q3 R3 S3 T3 U3',
})
