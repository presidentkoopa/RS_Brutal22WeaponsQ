"""SSG (super shotgun) -> SSG.md3 (52 frames). Hand-made pose table.

MESH FRAME MEANINGS (BD21 def + BD21 SSG.txt order/sounds + parts.py; surfaces:
0 'Cube' = barrels, 1 'Runko' = stock/receiver (body), 2/3 = the two shells,
4 'Open' = top lever, 5 = trigger).  Barrel angle is relative to the stock.
   0      sprint pose (SSRU A): ready tipped 5 deg nose-down
   1      READY (SHTZ A)
   2-10   double-barrel fire recoil (SHOF A-I): 6 = furthest back, 7 = most tilt
   11,12  single-barrel fire (SHTU A/B) = identical to ready
   13     reload start = ready
   14     top lever pushed (barrels 0.7 deg)                    <- Lever2
   15-22  barrels swinging open 2.7 -> 29.6 deg; spent shells still in chambers
   23     fully open (30.2); shells popped 11 units back out of the chambers
          (spent ones gone / new pair held at the breech)       <- eject anchor
   24-27  new pair sliding in (10.1, 7.3, 3.8, 1.0 from seated)
   28     both seated, gun still open and level                 <- sshotl anchor
   29     flick start: whole gun dipped (stock -13.7, barrels -44), still open
   30-37  swing upward, still open: stock -9.5 -> +50, barrels -40 -> +20
   43     barrels SNAPPED SHUT at the top of the swing (stock & barrels +50)
   44,45  coming back down (41, 18.7 deg)
   46     ready (= 1)
   38-42  ONE-shell insert (one shell seated, the other 11.1 -> 1.0), ends on 28
   47-51  raise (SHT5 A-E): 47 lowest (25 deg down) -> 51 (2 deg)
There is no frame with empty open chambers and no partial-close frame: the close
is the 37 -> 43 snap (as BD21 authored it, SHTZ Z -> SHO9 D).

BD22 SEQUENCES (story.py order) -> POSES (self-check, printed by _selfcheck()):
 Fire        SHT2 A | B C D E E F G H I J | A..   1 | 2 3 5 6 6 7 8 9 10 10 | 1
 AltFire     SHT2 X / Y | G H I J A               11/12 | 8 9 10 10 1
 Reload (2)  SHTZ A A B C<Lever2> D E F G H I I I H J K
                 1 1 13 14 15 17 19 21 22 22 22 22 22 22 22
             <sshoto><casings> L M [ N O P Q S T T U
                 23 23 23 23 23 23 24 25 26 26 27
             <sshotl><give> V W X Y Y(4) Z      28 28 28 29 29(x4) 31
             <sshotc> SHZ2 A B C D E F F G H I J<Lever1>
                 33 35 37 43 43 43 43 44 44 45 46
             SHTZ B A A                           13 1 1
   = lever, open once (monotonic 14->22), eject at the casing spawn (22->23),
     pair slides in and seats exactly on the load sound (27->28), dip, swing up
     open, snap shut once at the top (37->43, 3 tics after sshotc; BD21's
     authored lead was 4), down to ready.  No reversal, no dip to ready.
 Reload2 (1) SHTZ A A SHZ3 G H<Lever2> I J K      1 1 13 14 17 20 22
             <sshoto><casing> SHZ2 P Q R S S T U V W X X Y Y
                 38 38 38 38 38 38 38 39 40 41 41 42 42
             <sshotl><give> SHZ2 Z SHZ3 A B C D E E(3)   28 28 28 28 29 29 29(x3)
             SHTZ Z <sshotc> SHZ2 A B C D E F F F G H I J SHTZ B A A
                 31 | 33 35 37 43 43 43 43 43 44 44 45 46 | 13 1 1
   = one-shell insert (38-42) seats on the load sound (42->28).
 RaiseReloading (select, empty): enters at SHTZ L -> same as Reload from L.
 ResumeNormalRaise (select, loaded): SHZ2 A A <sshotc> A B C D G I J SHTZ B A
                 33 33 33 35 37 43 44 45 46 13 1   (BD22 shows it snapping shut)
 RaiseNoAmmo SHT2 K L M N                           47 49 50 51 -> 1
 Deselect    SHT2 O P Q R                           51 50 49 47
 Unload      SHTZ A A B C D E F G H I I I H J K     1 1 13 14 15 17 19 21 22 22 22 22 22 22 22
             SHZ3 F<sshoto> SHZ3 E(16) SHTZ Z <sshotc> SHZ2 A..J SHTZ B A A
                 22 | 29 | 31 | 33 35 37 43 43 43 43 44 44 45 46 | 13 1 1
 Inspect     SHTZ A A B <sshoto> SHZ2 K L M N O O(3+2) <sshotc> N M L K SHTZ B A A
                 1 1 13 | 14 16 18 20 22 22 | 20 18 16 14 | 13 1 1
 Sprint      SHT2 S T U V..V V U T S                1 0 0 0..0 0 0 0 1
 KickFlash   SHT2 S T U V W(10) V U T S             1 0 0 0 0 0 0 0 1

JUDGEMENT CALLS
 - SHTZ H is shown both on the way up (G H I) and after the hold (I I I H J):
   H = I = 22 (fully open) so the barrels never swing back; BD22's art there is
   the gun tilting, not the barrels closing.
 - SHZ3 F (Unload's open-sound frame; its sprite is missing from the pk3) = 22,
   not 23: Unload's next pose is the dip (shells seated, shared with Reload2),
   so popping the shells out for 1 tic would read as them going back in.
   Unload therefore reads: open, tip down and hold, flick shut (no empty-chamber
   frame exists in this mesh).
 - SHZ3 L-P (ReloadSmoke) and SHZ3 Q-U (ReloadSmoke2) are FLASH-layer smoke
   puffs. They get the pose the main layer shows on the same tic (23 and 38) so
   any model drawn for them coincides with the gun.
 - SHZ2 K-O (inspect, played forward then reversed) use the opening frames
   14-22: a part-open break that reads right both ways.
 - SHTZ B (start: thumb on lever, end: after Lever1) = 13 (ready), SHTZ C = 14
   (lever pushed, on the Lever2 sound).
 - X/Y (one barrel) keep BD21's authored single-barrel frames 11/12 (= ready).
 - Purist copies: VSSG = SHT2, VSHZ = SHTZ, V5HZ = SHZ2 (same letters/art).
"""


def _expand(spec):
    """'SHTZ': 'A1 B13 ...' -> {('SHTZ','A'): 1, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


_SHT2 = ('A1 B2 C3 D5 E6 F7 G8 H9 I10 J10 '      # ready, fire recoil
         'K47 L49 M50 N51 '                      # raise (RaiseNoAmmo)
         'O51 P50 Q49 R47 '                      # lower (Deselect)
         'S1 T0 U0 V0 W0 '                       # sprint / kick swing -> sprint pose
         'X11 Y12')                              # single-barrel fire (BD21 SHTU A/B)

_SHTZ = ('A1 B13 C14 '                           # ready, thumb on lever, lever pushed
         'D15 E17 F19 G21 H22 I22 J22 K22 '      # barrels open once, held open
         'L23 M23 [23 N23 O23 P23 '              # ejected; new pair held at breech
         'Q24 S25 T26 U27 '                      # pair sliding in
         'V28 W28 X28 '                          # seated on sshotl, hand leaves
         'Y29 Z31')                              # dip, start of the flick

_SHZ2 = ('A33 B35 C37 D43 E43 F43 G44 H44 I45 J46 '   # swing up open, snap shut, down
         'K14 L16 M18 N20 O22 '                       # inspect: part-open break
         'P38 Q38 R38 S38 T38 U38 V39 W40 X41 Y42 '    # one-shell insert
         'Z28')                                        # seated on sshotl

_SHZ3 = ('A28 B28 C28 D29 E29 '                  # Reload2: hand leaves, dip / Unload hold
         'F22 '                                  # Unload open sound (see notes)
         'G13 H14 I17 J20 K22 '                  # Reload2: lever, quick open
         'L23 M23 N23 O23 P23 '                  # ReloadSmoke (flash) = concurrent main pose
         'Q38 R38 S38 T38 U38')                  # ReloadSmoke2 (flash) = concurrent main pose

TABLE = _expand({
    'SHT2': _SHT2,
    'VSSG': ' '.join(t for t in _SHT2.split() if t[0] in 'ABCDEFGHIJ'),
    'SHTZ': _SHTZ,
    'VSHZ': _SHTZ,
    'SHZ2': _SHZ2,
    'V5HZ': ' '.join(t for t in _SHZ2.split() if t[0] in 'ABCDEFGHIJ'),
    'SHZ3': _SHZ3,
})

MESH_FRAMES = 52

# BD22 sequences in play order: 'SPR LETTERS' (each letter one tic unless 'L*n').
SEQUENCES = {
    'Fire': 'SHT2 A SHT2 BCDEEFGHIJ SHT2 AAAA',
    'AltFire(X)': 'SHT2 A SHT2 X SHT2 GHIJA',
    'AltFire2(Y)': 'SHT2 A SHT2 Y SHT2 GHIJA',
    'Reload': 'SHT2 A SHTZ AABCDEFGHIIIHJK | SHTZ LM[NOPQSTTU | SHTZ VWXYY*4Z | '
              'SHZ2 ABCDEFFGHIJ SHTZ BAA SHT2 A',
    'Reload2': 'SHT2 A SHTZ AA SHZ3 GHIJK | SHZ2 PQRSSTUVWXXYY | SHZ2 Z SHZ3 ABCDEE*3 '
               'SHTZ Z | SHZ2 ABCDEFFFGHIJ SHTZ BAA SHT2 A',
    'RaiseReloading': 'SHTZ LM[NOPQSTTU | SHTZ VWXYY*4Z | SHZ2 ABCDEFFGHIJ SHTZ BAA SHT2 A',
    'ResumeNormalRaise': 'SHZ2 AA | SHZ2 ABCDGIJ SHTZ BA SHT2 A',
    'RaiseNoAmmo': 'SHT2 KLMN SHT2 A',
    'Deselect': 'SHT2 A SHT2 OPQR',
    'Unload': 'SHT2 A SHTZ AABCDEFGHIIIHJK SHZ3 F | SHZ3 E*16 SHTZ Z | '
              'SHZ2 ABCDEFFGHIJ SHTZ BAA SHT2 A',
    'Inspect': 'SHT2 A SHTZ AAB | SHZ2 KLMNO*5 | SHZ2 NMLK SHTZ BAA SHT2 A',
    'Sprint': 'SHT2 A SHT2 STUVVVVVUTS SHT2 A',
    'KickFlash': 'SHT2 STUVW*10VUTS',
    'ReloadSmoke(flash) vs main': 'SHZ3 LMNOP',
    'ReloadSmoke2(flash) vs main': 'SHZ3 QRSTU',
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
            L = letters[j]; n = 1
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
        print('%-28s %s' % (name, _poses(seq)))


if __name__ == '__main__':
    _selfcheck()
