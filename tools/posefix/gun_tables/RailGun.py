"""RailGun (BD22) -> RailGun.md3 (37 frames), mapped by moment.

Frame meanings (BD21 Modeldef.Railgun.def + Railgun.txt + parts.py + renders):
  0-3   raise (pitch -46 -> 0); 2 is still tilted 11.5 deg down / 12 low
  3     READY, level (BD21 RAIL D); 11 is vertex-identical, 35 within 0.8
  4     trigger pulled, beam out (BD21 RAIF A)
  5-6   recoil, pushed back (6 = max), 7-10 coming forward (10 ~ ready)
  12-16 gun rolls to 15 deg while the battery (Mag-Bat) drops out;
        16 = battery 30 units below the gun
  17-28 battery rising back into the well (the new cell), 29 = seated
        (all at the 15 deg roll)
  30    jolt (lift +5, pitch +4.7) right after seating
  31-35 rolling back to level, 35 ~ ready
  36    zoom pose (scope moved; BD21 RAIZ B / SNIP A)
  Sprint pose: 2 (BD21 RAIL A B C -> 2).

BD22 art: RAIL A B C = charged idle (glow), D = uncharged ready (0 charges,
also unloaded), E-H lower, L K J I raise, M-Q swing aside charged, R-V uncharged
(sprint holds P / U, kick holds Q / V). RAIF A B flash, C D kick, E-G settle,
H discharged hold, I-K recharge. RAIZ A B aim in, C D scope, E F scope shot,
G-K red scope recharge, L M N unloaded aim in, O unloaded scope.
RAIR reload: A-E gun swings up to vertical (PlasmaCaseSpawn + Reload1 BEFORE A),
F-H upright, I x10 hand reaching, J-O hand brings the new cell up,
O-S approach (Reload2 "build-up" at O), InsertBullets after S, T-X pushed in
(X x5), Y Z hand away, F upright again, [ ] swing back down.
RAR2 A-C coming down to level, D-H hand to the scope (Beep at G), I-Q recharge
glow (Recharge at I); R-W = first-pickup rise from below to vertical.

Pose lists in BD22 order (tics expanded), from this table:
  Fire        RAIF AB CD EF G H HHHHHHHH HHHH IJK K x20
              4 5 6 7 8 9 10 | 3 x13 | 3 3 3 | 3 x20 -> ready 3
  Reload      3 | <casing, Reload1> A-E 35 34 33 32 31 | F G H H 28 24 20 20
              | I x10 16 | J-O 17 17 18 18 19 20 | <Reload2> O P P P Q Q R S
              20 21 21 21 22 22 23 24 | T T U V W 25 25 26 27 28 | X x5 29
              | Y Z F 29 29 28 | [ ] 30 31 | RAR2 A B C D D 32 33 34 35 35
              | E F 3 3 | G H H H 3 | I-Q 3 ... | ready 3
  Unload      3 | A-F 35 34 33 32 31 28 | Z Y X X X 29 x5 | <Reload1>
              V U T 27 26 25 | S-J 24 23 22 21 20 19 18 18 17 17
              | I I I I 16 x4 | H H G F 20 20 24 28 | E-A 31 32 33 34 35 | D 3
  FirstSelect RAR2 R-W 0 1 2 3 31 24 | H H 20 20 | I x5 16 | J.. as Reload
  Select      L K J I 0 1 2 3 -> 3        Deselect  E F G H 3 2 1 0
  Sprint      M N O 3 3 2 | P hold 2 | O N M 2 3 3 (empty: R S T / U / T S R same)
  Kick        M N O P 3 3 2 2 | Q x10 2 | P O N M 2 2 3 3 (empty R-V same)
  Aim         RAIZ A B C D 3 36 36 36 | zoom shot E F G H I J K.. 36 | out C B A 36 36 3
              unloaded L M N O 3 36 36 36 | out N M L 36 36 3 -> RAIL D 3
  Inspect     RAR2 Q..K, J J I x9 J..Q all 3

Judgement calls:
- Level ready is 3 (per owner): every ready / idle / charge letter is 3.
- F is shown three ways: after E (gun just upright), after Z (cell seated) and
  in the unload's way back. The mesh has no "upright" pose of its own, only
  battery in / out, so F = 28 (battery 1.4 units off seated). The battery
  therefore stays in through A-E and drops over F G H (28 24 20 -> 16), about
  6 tics after BD22 throws the spent cell (PlasmaCaseSpawn before A). Putting
  the drop at A-E instead would make F flash the battery in/out for 1 tic at
  the end of every reload (the flicker being fixed).
- A-E reuse the roll-back frames 35..31 played forwards (roll 1 -> 13 deg with
  the battery in), the only frames that tilt the gun without moving the battery.
- Insertion: the battery climbs slowly while the hand brings the cell
  (J-S 17..24), enters the well over T-W (25..28) after InsertBullets, is home
  at X (held 5 tics), jolt at [ and rolls back to level over ] A B C D.
- Unload replays the reload backwards (Z Y X, V U T pull out, S..J carry away);
  BD22 keeps showing RAIL D (= 3, battery in) once unloaded, so on the way down
  H G F bring the battery back up (20 24 28) rather than popping it in at D.
- First pickup: RAR2 R-W rise (0-3) and roll (31), then the battery drops
  (24 20 16) and the new one goes in as in the reload.
- Sprint/kick: authored sprint pose 2 for the swung-aside letters, the first
  two letters (M N / R S, art still near ready) stay 3.
- Zoom: scope overlays (RAIZ C-K, O) -> 36 (BD21's zoom pose); aim-in A / L
  = 3, B / M = 36. Zoomed shots stay on 36 (switching to the 4-10 recoil would
  swing the scope back and forth).
- 2AIF = purist RAIF (same letters, same poses). 2HTN E (purist warning) = 3.
"""


def _expand(spec):
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A B C charged idle, D uncharged ready | E F G H lower 3 2 1 0 |
    # L K J I raise 0 1 2 3 | M N / R S start of the swing, O P Q / T U V aside
    'RAIL': 'A3 B3 C3 D3 E3 F2 G1 H0 I3 J2 K1 L0 M3 N3 O2 P2 Q2 '
            'R3 S3 T2 U2 V2',
    # A trigger, B C push back (C max), D-G forward, H discharged, I-K recharge
    'RAIF': 'A4 B5 C6 D7 E8 F9 G10 H3 I3 J3 K3',
    '2AIF': 'A4 B5 C6 D7 E8 F9 G10',
    # A-E swing up (roll-back frames forwards, battery in) | F shared: 28
    # G H drop, I out | J-W new battery rising | X seated | Y Z hand away
    # [ ] jolt and start back down
    'RAIR': 'A35 B34 C33 D32 E31 F28 G24 H20 I16 J17 K17 L18 M18 N19 O20 '
            'P21 Q22 R23 S24 T25 U26 V27 W28 X29 Y29 Z29 [30 ]31',
    # A B C D back to level | E-Q hand at the scope, recharge: ready |
    # R-W first-pickup rise then roll and drop
    'RAR2': 'A32 B33 C34 D35 E3 F3 G3 H3 I3 J3 K3 L3 M3 N3 O3 P3 Q3 '
            'R0 S1 T2 U3 V31 W24',
    # A / L aim in from ready, B / M at the eye, C-K and N O scope overlays
    'RAIZ': 'A3 B36 C36 D36 E36 F36 G36 H36 I36 J36 K36 L3 M36 N36 O36',
    '2HTN': 'E3',
})
