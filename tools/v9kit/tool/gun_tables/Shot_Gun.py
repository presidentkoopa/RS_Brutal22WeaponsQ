"""Shot_Gun (pump shotgun) -> Shotgun.md3 (36 frames). Hand-made pose table.

MESH FRAME MEANINGS (BD21 def + BD21 Shotgun.txt order/sounds + parts.py; body =
'Runko'; surfaces 4 'pump' and 5 'eject' = fore-end and bolt; surface 2 = THE
SHELL: at rest it sits in the chamber, it rides back/forward with the pump, and
in 23-31 it is the shell being loaded).
   0-3    raise (SHSS A-D): 0 lowest (45 deg down) -> 3 (6 deg, also the
          authored sprint pose STRN A)
   4      READY (also the authored aim pose SHT8 A/D/E)
   5-8    fire recoil (SHTA B-E): 5,6 straight back, 7 muzzle up, 8 settling
   9      = ready
   10-14  gun rolls/tilts into the side "pump & load" posture (14 = posture)
   15-18  pump pulled back 0.9 -> 6.3 (chambered shell rides back with it)
   19-21  pump forward 5.4 -> 0.9,  22 = pump home, still in the posture
   23-28  SHELL INSERT, posture held: shell comes up from below the receiver
          (17.1 from rest, 16.5, 14.4, 10.9, 6.8) into the loading port and
          the tube mouth (28). BD21 played it once per shell: SSHR AAABC D<snd> EF
   29-31  shell pushed in through the ejection port to the chamber (SSHR G-I,
          never played by BD21 code; not used here)
   32     = ready (aimed),  33-35 pump back 1.5/4.8/6.3 while aimed (SHT8 J-L)
14 and 22 are the same pose (posture, pump home, shell hidden in the chamber).

BD22 SEQUENCES (story.py order) -> POSES (self-check, printed by _selfcheck()):
 Fire+Pump1  SHTA A B C D E W | SHTN A x7 | A B C D E F G <casing> H<Pump1> I J K L M N
             <Pump2> P Q | F E D C B | SHTA F G H I | SHTN A
             4 5 6 7 8 9 | 4.. | 4 10 11 12 13 14 14 | 15 16 16 17 18 18 18 | 20 21 |
             14 13 12 11 10 | 9 9 9 9 | 4
 Reload      SHTN A | A B C D E F S T                4 | 4 10 11 12 13 14 14 22
   per shell U U U V W <Shotgun/Reload,give> X Y Z [ ]
             22 22 22 24 26 | 27 28 28 22 22
             = the loop holds the posture; every pass a shell rises from below
               (16.5 -> 10.9 -> 6.8 on the insert sound -> 3.1 at the port)
               and vanishes into the gun on [ ]; the next pass starts clean.
   finish    SHTN T S F E D C B | SHTA F G H I       22 14 14 13 12 11 10 | 9 9 9 9
   (was empty) Pump2: T S F G H<Pump1> I J <casing> K L M N <Pump2> P Q F E D C B
             22 14 14 14 15 16 16 17 18 18 18 20 21 14 13 12 11 10 | SHTA 9 9 9 9
 ReloadFromPumping  SHTN S T -> loop                  14 22 -> 22 22 22 24 26 ...
 Kick while loading  SHTN [ ] alternating (offsets)  22 ...
 Unload      SHTN A B C D E F                         4 10 11 12 13 14
   per shell G <Pump1> H I J K L K J <Pump2> I H G F  14 15 16 16 17 18 17 16 16 15 14 14
   finish    SHTN E D C B A | SHTA F G H I            13 12 11 10 4 | 9 9 9 9
 Aim in/out  SHT8 A B C(hold) / B A SHTN A            4 4 4 / 4 4 4
 Fire2 (aimed) SHT8 D E F G C                          5 6 8 32 4
 Pump3 (aimed) <Pump1> SHT8 G H I I J J <casing,Pump2> I H H G G C
             32 33 34 34 35 35 | 34 33 33 32 32 4
 Inspect     SHTN A B C D E F G <Pump1> SHT6 A B C D E F F F F(2) G <Pump2> H I
             SHTN F E D C B A | SHTA F G H I
             4 10 11 12 13 14 14 | 15 16 16 17 17 17 17 17 17 17 16 15 14 |
             14 13 12 11 10 4 | 9 9 9 9     (press-check: pump part-way back,
             the chambered shell rides back into view, then home)
 Select      SHTA M L K J -> SHTN A                   0 2 3 3 -> 4
 FirstSelect SHTA M L K | SHTN B C D E F G H I J J K K L L L L L M M N P Q R
             G G G F F E D C B A
             0 2 3 | 10 11 12 13 14 14 15 16 16 16 17 17 18 18 18 18 18 18 18 18
             20 21 22 14 14 14 14 14 13 12 11 10 4
 Deselect    SHTA N O P Q                             3 2 1 0
 Sprint      SHTA R S T U..U T S R                    4 4 3 3..3 3 4 4
 KickFlash   SHTA R S T U V(10) U T S R               4 4 3 3 3 3 3 4 4

JUDGEMENT CALLS
 - The mesh has one side posture for both pumping and loading (BD22 tilts the
   gun further right for loading, S T U..]); S and T both hold that posture.
 - Insert pass: U (no hand yet in BD22's art) = 22, shell hidden; the shell
   appears on V and reaches the port on Y. SSHR G-I (29-31, chamber load
   through the ejection port) is a different motion and is not used.
 - SHTN L = 18 (pump fully back) so Unload's K L K J is one full pump cycle.
 - SHTA F G H I (ReadyToFireAgain settle after every pump/reload) = ready 9.
 - SHT8 G is both the aimed-fire recovery and the start/end of the aimed pump:
   32 (= ready with pump home) reads right in both.
 - Purist copies: 2HTN = SHTN, 2HTA = SHTA (same letters/art).
"""


def _expand(spec):
    """'SHTN': 'A4 B10 ...' -> {('SHTN','A'): 4, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


_SHTN = ('A4 B10 C11 D12 E13 F14 G14 '           # ready, roll into pump/load posture
         'H15 I16 J16 K17 L18 M18 N18 '          # pump back (Pump1 at H)
         'P20 Q21 R22 '                          # pump forward (Pump2), home
         'S14 T22 '                              # into / out of the loading posture
         'U22 V24 W26 X27 Y28 Z28 [22 ]22')      # one shell per pass, insert on X

_SHTA = ('A4 B5 C6 D7 E8 W9 '                    # fire: BD21 authored SHTA A-E
         'F9 G9 H9 I9 '                          # settle after pump/reload
         'M0 L2 K3 J3 '                          # raise (lowest first)
         'N3 O2 P1 Q0 '                          # lower
         'R4 S4 T3 U3 V3')                       # sprint / kick swing -> sprint pose 3

_SHT6 = 'A15 B16 C16 D17 E17 F17 G16 H15 I14'   # inspect press-check
_SHT8 = 'A4 B4 C4 D5 E6 F8 G32 H33 I34 J35'      # aim, aimed fire, aimed pump

TABLE = _expand({
    'SHTN': _SHTN,
    '2HTN': ' '.join(t for t in _SHTN.split() if t[0] in 'ABCDEFGHIJKLMNPQ'),
    'SHTA': _SHTA,
    '2HTA': ' '.join(t for t in _SHTA.split() if t[0] in 'ABCDEFGHIW'),
    'SHT6': _SHT6,
    'SHT8': _SHT8,
})

MESH_FRAMES = 36

SEQUENCES = {
    'Fire+Pump1': 'SHTN A SHTA ABCDEW SHTN A*7 | SHTN ABCDEFG | SHTN HIJKLMN | SHTN PQ | '
                  'SHTN FEDCB SHTA FGHI SHTN A',
    'Reload x3': 'SHTN A | SHTN ABCDEFST | SHTN UUUVW|XYZ[] | SHTN UUUVW|XYZ[] | '
                 'SHTN UUUVW|XYZ[] | SHTN TSFEDCB SHTA FGHI SHTN A',
    'Reload(empty)->Pump2': 'SHTN UUUVW|XYZ[] | SHTN TSFG SHTN HIJKLMN | SHTN PQFEDCB SHTA FGHI SHTN A',
    'ReloadFromPumping': 'SHTN P SHTN ST | SHTN UUUVW|XYZ[]',
    'DoKickReloading': 'SHTN [][][][*4]*4',
    'Unload x2': 'SHTN A SHTN ABCDEF | SHTN GHIJKLKJIHGF | SHTN GHIJKLKJIHGF | '
                 'SHTN EDCBA SHTA FGHI SHTN A',
    'AimIn/Out': 'SHTN A SHT8 ABC*5 | SHT8 BA SHTN A*5',
    'Fire2+Pump3': 'SHT8 C SHT8 DEFGC | SHT8 GHIIJJ | SHT8 IHHGG SHT8 C',
    'Inspect': 'SHTN A SHTN ABCDEFG | SHT6 ABCDEFFFF*2G | SHT6 HI SHTN FEDCBA SHTA FGHI SHTN A',
    'Select': 'SHTA MLKJ SHTN A',
    'FirstSelect': 'SHTA MLK SHTN BCDEFGHIJJKKLLLLLMMN | SHTN PQRGGGFFEDCBA SHTN A',
    'Deselect': 'SHTN A SHTA NOPQ',
    'Sprint': 'SHTN A SHTA RSTUUUUUTSR SHTN A',
    'KickFlash': 'SHTA RSTUV*10UTSR',
}


def _poses(seq):
    out = []
    toks = seq.split()
    i = 0
    while i < len(toks):
        if toks[i] == '|':
            out.append('|'); i += 1; continue
        spr, letters = toks[i], toks[i + 1]; i += 2
        j = 0
        while j < len(letters):
            L = letters[j]
            if L == '|':
                out.append('|'); j += 1; continue
            n = 1
            if j + 1 < len(letters) and letters[j + 1] == '*':
                k = j + 2
                while k < len(letters) and letters[k].isdigit(): k += 1
                n = int(letters[j + 2:k]); j = k
            else:
                j += 1
            out += [str(TABLE[(spr, L)])] * n
    return ' '.join(out)


def _selfcheck():
    for name, seq in SEQUENCES.items():
        print('%-22s %s' % (name, _poses(seq)))


if __name__ == '__main__':
    _selfcheck()
