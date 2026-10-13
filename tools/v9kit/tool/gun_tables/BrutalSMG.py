"""BrutalSMG (BD22) -> BrutalSMG.md3 (27 frames, KRISS-Vector-style SMG).

MESH FRAME MEANINGS (BD21 def Modeldef.SMG.def + SubMachinegun.txt + parts.py ref 3)
  surfaces: 0 charging handle ("Sights", 239v) | 1 body | 2 trigger | 3 magazine ("Lipas")
  0-2   raise (0 lowest, 45 deg down; 2 = 11 deg down)  [BD21 SMGS A B C]; 2 = authored
        sprint pose [BD21 SMSP A]
  3     ready [BD21 SMGG A, also the ADS pose SMGA A]
  4-6   fire recoil, trigger pulled on 4-5 [BD21 SMGF A B C]
  7     reload start = ready (vertex-identical to 3 and 26)   [BD21 SMGR A]
  8     old mag gone: well empty, new mag hanging just below the well (mag top 2.6
        below the mouth), gun still level (roll 0.4)          [BD21 played the
        EmptyClipSpawn just before SMGR A, so 7->8 is the magazine drop]
  9-18  new mag rises into the well while the gun rolls to ~21 deg:
        9 below | 10 tip at the mouth | 11-13 entering | 14 ~60% in | 16 ~85% |
        18 effectively seated (0.3)
  19    seated + slap jolt (body jumps up 1, pitch +5 deg)
  20-25 charging handle pulled (peak 10.2 at 23) and snapped forward (25) while the
        gun rolls back from 19 deg to 0.8 deg
  26    ready (identical to 3)
  BD21 order: SMGR A..T = 7..26 one tic each, one "reload" sound at the start.
  The mesh has NO rolled-with-mag-in pose before the swap and no ready-without-mag
  pose; its roll is welded to the magazine rise. Everything below follows from that.

BD22 SEQUENCES -> POSES (self-check, generated from TABLE by seqcheck.py)
Select:
    SMGS H0 G1 F2 E3 | SMGR A3
Deselect:
    SMGR A3 | SMGS A3 B2 C1 D0
Fire:
    SMGR A3 | <SMG/Fire> | SMGF A4 B5 C6 | SMGR A3
Fire purist:
    VSMG A3 | 2MGF A4 B5 C6 | VSMG A3
ADS in/fire/out:
    SMGR A3 | SMGZ C3 D3 E3 | SMGZ F3 | SMGZ G4 H5 I6 | SMGZ F3 | SMGZ E3 D3 C3 | SMGR A3
Sprint:
    SMGR A3 | SMGF D3 E3 F2 | SMGF G2 G2 G2 G2 | SMGF F2 E3 D3 | SMGR A3
KickFlash:
    SMGF D3 E3 F2 G2 H2 | SMGF H2 | SMGF H2 G2 F2 E3 D3
Reload:
    SMGR A3 | SMGR B7 C7 D7 E7 F7 G7 G7 H7 H7 H7 | <SMG/Reload1 mag out> | SMGR I8 J8 K8 L8 M8 N8 O8 | SMGR O8 <EmptyClip2Spawn> | SMGR P8 P8 P8 Q8 R9 S10 T11 U14 U14 U14 U14 V16 | <give ammo> | <SMG/Reload2 seat> | SMGR X18 W19 X18 Y20 Z21 Z21 | SMGR [22 \\23 ]25 | SMGR D7 C7 B7 | SMGR A3
ReloadEmpty (after unload):
    SMGR A3 | SMGR B7 | 2MGR E8 D8 C8 B8 A8 | SMGR P8 P8 P8 Q8 R9 S10 T11 U14 U14 U14 U14 V16 | <give ammo> | <SMG/Reload2> | SMGR X18 W19 X18 Y20 Z21 Z21 | SMGR [22 \\23 ]25 | SMGR D7 C7 B7 | SMGR A3
Unload:
    SMGR A3 | SMGR B7 C7 D7 E7 F7 G7 G7 H7 H7 H7 | <SMG/Reload1> | <take ammo> | SMGR I8 J8 K8 L8 M8 N8 O8 O8 | 2MGR A8 B8 C8 D8 E8 | SMGR B7 A3
FirstSelect:
    3MGR K0 J1 I2 H3 G8 F8 | SMGR O8 O8 P8 P8 P8 Q8 R9 S10 T11 U14 U14 U14 U14 V16 | <SMG/Reload2> | SMGR X18 W19 X18 Y20 Z21 Z21 | SMGR [22 \\23 ]25 | SMGR D7 C7 B7 | SMGR A3
SelectDual:
    SM2S Q3 P3 O3 N3 | <Rifle/Select> | SM2S M3 L3 K3 J3 | SMGR A3
SelectDualUnloaded:
    SM2S W3 V3 U3 T3 | SM2S S3 R3 K3 J3 | SMGR A3

  Read: the magazine leaves exactly once (7->8 at I, right on SMG/Reload1) and goes
  in exactly once (8 -> 18 over Q..V, seated at X on SMG/Reload2, slap at W), then
  the gun rolls back with the charging-handle pull (Y..]) and is at ready from D on.
  The old mapping put the mag rise on B..N and then played 10 9 8 (mag dropping)
  on D C B at the end, so every reload showed the clip going in twice.

JUDGEMENT CALLS
  - SMGR B..H (BD22 turns the gun and grabs the mag) stay on 7 (ready, mag in): the
    mesh has no turned-with-mag pose; its roll only happens while the new mag rises.
    Using 26->19 backwards would wiggle the charging handle out and in.
  - SMGR B C D are played at both ends (B C D... opening, ...D C B closing). They are
    7 in both; the mesh's roll-back (20..25) is therefore fitted onto Y Z [ \\ ] so the
    gun is already home (25 ~= ready) when D C B play. No flick to ready mid-reload.
  - X is shown before and after W (X W X = the seat slap): X 18 (seated), W 19 (the
    authored slap jolt) -> a one-tic jolt, as BD22's art.
  - Q R: BD22 shows the new mag coming from off-screen; the mesh's farthest mag
    position is 8 (just under the well), so P Q hold 8 and the rise starts at R.
  - 2MGR A-E (gun with an EMPTY well, turning to/from the front) -> 8, the only
    empty-well frame. Consequence of the mesh having a mag at ready: after an unload
    the mag pops back into the well at SMGR B (one tic, gun level both sides), and
    ReloadEmpty pops it down at 2MGR E before inserting it once.
  - 3MGR K J I H (first pickup, gun rising) -> select frames 0 1 2 then 3; G F (gun up,
    empty well, BD22 then inserts a mag) -> 8. The mag drops out of sight at G (one
    tic, gun level) and is then inserted once.
  - SM2S (dual -> single: the right gun stays up while the left one leaves) -> ready 3.
  - SMGF D E (front, before swinging aside) -> 3; F G H swung aside -> authored sprint
    pose 2. SMGZ (ADS) -> BD21's aim pose = ready 3; aimed fire G H I -> 4 5 6.
  - 2MGF / VSMG are the purist copies of SMGF / ready.
"""


def _expand(spec):
    """'SMGR': 'A3 B7 ...' -> {('SMGR','A'): 3, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


TABLE = _expand({
    # A ready | B-H turn + grab mag (mesh: still ready, mag in) | I mag out (Reload1)
    # J-O mag away, O drop spawn | P Q empty, new mag below | R-V mag rising
    # X seated (Reload2) / W slap | Y-] roll back + charging handle | (D C B = 7)
    'SMGR': 'A3 B7 C7 D7 E7 F7 G7 H7 I8 J8 K8 L8 M8 N8 O8 P8 Q8 R9 S10 T11 '
            'U14 V16 W19 X18 Y20 Z21 [22 \\23 ]25',
    # empty-well gun turning to / from the front (ReloadEmpty, FinishUnload)
    '2MGR': 'A8 B8 C8 D8 E8',
    # first pickup: K..H rising (select frames), G F up with an empty well
    '3MGR': 'K0 J1 I2 H3 G8 F8',
    # A-D lower (deselect) | H-E raise (select)
    'SMGS': 'A3 B2 C1 D0 E3 F2 G1 H0',
    # A-C fire | D E front (start/end of swing) | F G H swung aside (sprint/kick/slide)
    'SMGF': 'A4 B5 C6 D3 E3 F2 G2 H2',
    '2MGF': 'A4 B5 C6',
    # C D E aim in / out | F aimed | G H I aimed fire
    'SMGZ': 'C3 D3 E3 F3 G4 H5 I6',
    # dual -> single switch: the kept gun is at ready throughout
    'SM2S': 'J3 K3 L3 M3 N3 O3 P3 Q3 R3 S3 T3 U3 V3 W3',
    'VSMG': 'A3',
})

MESH_FRAMES = 27
