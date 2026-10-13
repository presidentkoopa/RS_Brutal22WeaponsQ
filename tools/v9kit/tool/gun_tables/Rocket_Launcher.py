"""Rocket_Launcher (BD22) -> RPG.md3 (39 frames), mapped by moment.

RPG.md3 is a launcher with a revolving rocket drum on a side crane.
Frame meanings (BD21 def + RocketLauncher.txt + parts.py/drum angle + renders):
  0-3   raise (body rot 52 -> 7 deg; BD21 select MISS ABCD, deselect DCBA)
  4     end of raise = level, drum aligned ("S1"); identical to 16 and 34-38
  5     READY (BD21 RLNG A): level, drum turned 11 deg off S1
  6-8   drum roll after a shot (BD21 RLNG BCD: 5 -> 6 -> 7 -> 8 -> 5);
        8 = drum back on S1 with the trigger pulled
  9-15  fire recoil: 9 pushed back + 5 deg up, 10 max (10 deg), 11-15 settle
  16    recoil done (= 4)
  17-21 crane swings the drum out to the side (17 barely, 21 fully out)
  22-24 old drum falls out of the crane (24 = frozen 25-45 units under the
        gun: never held, BD21 showed it 1 tic)
  25    new drum sitting in the crane, still swung out
  26-33 crane swings back in, drum spinning as it closes
  34    closed and seated (= 4)
  35-38 = 34 (BD21 "MIAI" zoom frames; nothing distinct)
  Sprint pose: 3 (BD21 MISP A).
  BD21 reload: 17-21 out, 21-23 drop, 24 (1 tic), 25, 26 x4, 27-32 closing, 33 34,
  roll 6 7 8, 5.

BD22 art: MISG A/F/I = ready with 3+/2/1-or-0 rockets, J = ready UNLOADED (no pack),
B-E and G-H = pack turning to the next tube after a shot, K-M = aim in.
MISF A-G / H-N / O-U = the same shot with 3 different packs (2ISF = purist copy).
MISR = reload: A-E gun dips (RocketCaseSpawn after E), F-H back up, I-K tilt
the breech up, L-N hold, O-T hand brings the new pack, U-X pack pushed in
(rocket/reload2 at U), Y Z hold, MIR2 A-E back to ready. MIR2 F = level with
no pack (end of unload). MISS = raise/lower in 4 ammo variants (D C + BA/JI/
LK/NM up; HG/QP/SR/VU + F/O/T + E down), W X Y = scope overlay.
MISK = swing aside for sprint / kick (A-E loaded, F-J unloaded).

Pose lists in BD22 order (tics expanded), from this table:
  Fire 3+ left   MISF A-G, MISG A AAA A BBCCDD, ready A
                 9 10 11 12 13 14 15 | 5 5 5 5 5 | 6 6 7 7 8 8 | 5
  Fire 2 left    ... MISG BBCCEE, ready F    ... | 6 6 7 7 8 8 | 5
  Fire last      MISF H-N, MISG F FFF F GGHHII, ready I
                 9 10 11 12 13 14 15 | 5 5 5 5 5 | 6 6 7 7 5 5 | 5
  Fire empty     MISF O-U, MISG I, -> Reload   9 10 11 12 13 14 15 | 5 | 17 ...
  Reload         5 | A-E 17 18 19 19 20 20 21 | <casing> F G H 22 23 24
                 | I J K L M M N N N 25 x9 | O P Q R S S T T T T 25 x10
                 | <reload2> U V V V W X 27 29 29 29 31 33 | Y x4 Z Z 34 x6
                 | MIR2 A-E 34 34 34 34 5 | ready 5
  ReloadUnloaded J 25 | from I as above (no jump: both 25)
  Unload         5 | MISG A 5 | MISR A B C C D D C B 17 18 19 19 20 20 19 18
                 | MIR2 F 21 | ReadyNoAmmo MISG J 25
  FirstSelect    -4 | F G H 22 23 24 | I-N 25 x9 | O-T 25 x10
                 | U V V V W X 27 29 29 29 31 33 | Y x7 Z Z 34 x9
                 | MIR2 A-E 34 34 34 34 5 | 5
  Select         D C B A 0 1 2 3 -> 5 (also D C J I, D C L K; unloaded D C N M -> 25)
  Deselect       H G F E 3 2 1 0 (also Q P F E, S R O E; unloaded V U T E)
  Sprint         A B C 4 4 3 | hold E 3 | C B A 3 4 4 | 5
  Kick (flash)   A B C D E(10) D C B A  4 4 3 3 3 3 3 4 4
  Unloaded sprint / kick  F-J all 25
  Aim            MISG K L M 5 5 5 -> MISS W 5 ; zoomed fire W W Y X Y W.. all 5

Judgement calls:
- Ready = 5 (BD21's RLNG A). The post-shot pack turn uses BD21's own roll
  6 7 8 then 5. For the last-rocket turn (GGHHII) I is also the 1-rocket ready
  letter, so it stays 5: 6 6 7 7 5 5 (drum-only nudge, the gun does not move).
- The old drum falls over F G H (22 23 24), the 3 tics after RocketCaseSpawn;
  its world chamber stays invisible for its first 7 tics, so the two do not
  overlap. The new drum is in the open crane from I (as BD21: 24 for 1 tic,
  then 25) and waits there while BD22's hand brings the pack; the crane closes
  over U-X from the reload2 sound and is seated at Y. F G H also open the
  first-pickup load, where the drop reads as the gun dumping an empty pack.
- Unloaded (MISG J) = 25, crane swung open: the mesh has no empty-crane pose
  that is not mid-fall, an open crane reads as "not ready", and the reload
  from the unloaded state (starts at I = 25) has no jump. Unload: BD22 replays
  C B backwards (gun comes back up) = small swing back (20 19 18), then MIR2 F
  = 21 (crane fully out), then 25.
- Unloaded sprint / kick (MISK F-J) stay on 25: the sprint pose 3 has the
  crane shut, so it would snap shut and open again at every sprint/kick.
- Unavoidable snaps, unloaded state only: select ends 3 -> 25, deselect starts
  25 -> 3, aim in/out (MISG K L M are shared with the loaded gun) 25 <-> 5.
  BD22 bug: SlideFlashEndEarlyUnload shows MISK E (loaded art) for 2 tics; E = 3.
- Zoom (MISS W X Y, scope overlay) and aim letters MISG K L M -> ready 5: the
  mesh has no distinct aim pose (35-38 = 34).
- 2HTN E is only shown by the purist warning -> ready.
"""


def _expand(spec):
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A F I ready (3+/2/1-0 rockets) | B C D (and E for 2-left) pack turn = roll
    # 6 7 8 | G H last-rocket turn 6 7 (I stays ready) | J unloaded = crane
    # swung open | K L M aim in/out
    'MISG': 'A5 B6 C7 D8 E8 F5 G6 H7 I5 J25 K5 L5 M5',
    # three packs, same shot: A/H/O fire, B/I/P max kick, rest settle
    'MISF': 'A9 B10 C11 D12 E13 F14 G15 H9 I10 J11 K12 L13 M14 N15 '
            'O9 P10 Q11 R12 S13 T14 U15',
    '2ISF': 'A9 B10 C11 D12 E13 F14 G15 H9 I10 J11 K12 L13 M14 N15 '
            'O9 P10 Q11 R12 S13 T14 U15',
    # A-E crane swings out (also unload, C B replayed backwards)
    # F G H old drum falls (casing spawned at F) | I-T new drum in the open
    # crane | U-X crane closes (reload2 at U) | Y Z seated
    'MISR': 'A17 B18 C19 D20 E21 F22 G23 H24 I25 J25 K25 L25 M25 N25 '
            'O25 P25 Q25 R25 S25 T25 U27 V29 W31 X33 Y34 Z34',
    # A-D still closed while the gun swings back level, E level = ready
    # F: unload only, crane fully out
    'MIR2': 'A34 B34 C34 D34 E5 F21',
    # raise D C then B A / J I / L K / N M ; lower H G / Q P / S R / V U then
    # F / O / T, E | W X Y scope overlay
    'MISS': 'A3 B2 C1 D0 E0 F1 G2 H3 I3 J2 K3 L2 M3 N2 O1 P2 Q3 R2 S3 '
            'T1 U2 V3 W5 X5 Y5',
    # A-E swing aside (sprint pose 3) | F-J unloaded: crane stays open
    'MISK': 'A4 B4 C3 D3 E3 F25 G25 H25 I25 J25',
    '2HTN': 'E5',
})
