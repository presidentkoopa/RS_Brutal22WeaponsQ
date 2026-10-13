"""Authored poses for the four guns whose BD22 sprites share no names with BD21.

Each BD22 sprite frame gets the model frame that shows the SAME MOMENT in the
authored BD21 animation. Phases were matched by looking at both sides: BD22's
sprite art and DECORATE timing (sounds, ammo spawns), and the mesh's own frames
(per-surface positions: magazine, battery, shell, receiver, barrel).

Authored BD21 frame meaning, from the authored defs and the meshes:

  AssaultShotgun.md3 (32)  0-3 raise | 4 ready | 5-10 fire | 11 reload start
      12-13 bolt back | 14-16 drum out | 17-24 new drum rising, seated at 24
      25-28 tilt for charging | 29-31 bolt forward, back to ready
      aim A12A A-G -> 4..10 | sprint -> 3 | empty ready (A12R Q) -> 27
  Plasma.md3 (30)  0-3 raise | 4 ready | 5-8 fire | 9-12 cooldown tilt
      13-15 = ready | 16-17 alt-fire recoil | 18 reload start | 19 cell gone
      20-23 new cell rising | 24 seated | 25-28 roll | 29 back | sprint -> 3
  M79.md3 (33)  0-2 raise | 3 ready | 4-6 fire | 7-18 barrel opening
      19-22 spent shell out | 23-26 new shell in | 27 seated | 28-31 closing
      32 closed | sprint -> 2
  FlameCannon.md3 (8)  0 ready | 1-4 fireball kick | 5 recovering
      6-7 flamethrower jitter (BD21 alternates 6,7)

Where a BD22 sequence is longer or shorter than BD21's, it is resampled evenly
over the authored run. Where BD22 reuses one frame in two places the pose was
chosen to read correctly in both (noted inline).
"""


def _expand(spec):
    """'USAS': 'A4 B5 ...' -> {('USAS','A'): 4, ...}"""
    out = {}
    for spr, s in spec.items():
        for tok in s.split():
            out[(spr, tok[0])] = int(tok[1:])
    return out


ASG = _expand({
    # A ready | B-F fire, resampled over 5-10 | G-I aim in, J aimed hold,
    # K-M aimed fire, N-O back to the hold (authored A12A A-G -> 4..10, then D)
    # T S R Q raise | U V W X lower | Z Y unloaded raise | [ ] unloaded lower
    # P is only ever a 0-tic state.
    'USAS': 'A4 B5 C6 D8 E9 F10 G4 H5 I6 J7 K8 L9 M10 N7 O7 P4 '
            'Q3 R2 S1 T0 U3 V2 W1 X0 Y3 Z2 [3 ]2',
    # A-H empty-reload start (and unload end, played backwards)
    # I empty ready (authored A12R Q, bolt locked back)
    # J-P first-pickup raise | Q-U gun swung aside for sprint/kick (sprint pose)
    '3SAR': 'A11 B12 C13 D13 E13 F13 G13 H13 I27 J0 K1 L1 M2 N2 O3 P3 '
            'Q3 R3 S3 T3 U3',
    # A-G tilt and grab drum | H-M drum out | N-S no drum | T-Z new drum in
    'USAR': 'A11 B12 C12 D13 E13 F13 G13 H14 I14 J14 K14 L15 M15 N16 O16 '
            'P16 Q16 R16 S16 T17 U17 V18 W18 X19 Y20 Z21',
    # A-F drum seats | G-J hand leaves | K-M hand to bolt | Q S R pull,
    # P hold back | O N release | T-Z hand away | [ \ back to front.
    # M is shown both before the pull and after the release: 28 reads in both.
    '2SAR': 'A21 B22 C22 D23 E24 F24 G24 H24 I24 J24 K25 L25 M28 N29 O28 '
            'P27 Q26 R26 S26 T30 U30 V30 W31 X31 Y31 Z31 [31 \\4',
    # 0-tic only, or purist idle, or the pickup: ready pose, as before
    '2SAS': 'A4', 'SMGR': 'A4', 'RIFF': 'A4', 'SHTN': 'A4', 'SHTZ': 'A4',
    'PLAY': 'A4', 'A12P': 'A4',
})

PLASMA = _expand({
    # A F G H I ready (light colour = ammo level) | B or C fire, D E recoil
    # J-O alt-fire charging: authored charge pose is the ready pose
    # W V U T raise | P Q R S lower
    'PRSG': 'A4 B5 C5 D7 E8 F4 G4 H4 I4 J4 K4 L4 M4 N4 O4 '
            'P3 Q2 R1 S0 T3 U2 V1 W0',
    # three colour sets of the same move: front, front, then swung aside
    'PRSK': 'A4 B4 C3 D3 E3 F4 G4 H3 I3 J3 K4 L4 M3 N3 O3',
    # first-pickup raise
    'PRR1': 'A0 B1 C2 D3 E3',
    # A Z B C start (and end) | D-I cell out, held | J-N new cell rising
    # O seated (insert sound) | P-T hand pushes | U-Y roll back to ready.
    # A, Z and C also close the animation, so they stay on the ready-like 18.
    'PRSR': 'A18 B18 C18 D19 E19 F19 G19 H19 I19 J20 K20 L21 M22 N23 O24 '
            'P24 Q24 R24 S24 T24 U25 V26 W27 X28 Y29 Z18',
    # alt-fire release: A B recoil (authored PLSN L K), C-I cooldown tilt
    # (authored PLSN B-E), held on I, then back down the same way
    'PRSA': 'A17 B16 C9 D9 E10 F11 G11 H12 I12',
    '2RSG': 'A4', 'PLAY': 'A4', '2HTN': 'E4', 'PRAS': 'C4',
})

M79 = _expand({
    # A ready | B-E fire resampled over the authored 4,6,6,6,5,5,5
    # F-K breech opens, shell starts out | L-P barrel empty, spent shell away
    # Q-U hand brings shell | V-X shell goes in | Y seated
    # (BD22 then hides the gun 4 tics) | Z [ \ ] barrel snaps shut
    'GRLN': 'A3 B4 C6 D6 E5 F11 G13 H15 I17 J18 K19 L20 M21 N22 O22 P22 '
            'Q23 R23 T24 U24 V25 W25 X26 Y27 Z28 [29 \\30 ]31',
    # A-G closed, swinging down | H-L settle to ready | M-P raise | Q-T lower
    # U V blank spacer frames that open the first-pickup load: show it open
    # X-] swung aside for sprint/kick (sprint pose 2)
    'GRL2': 'A32 B32 C32 D32 E32 F32 G32 H3 I3 J3 K3 L3 M0 N1 O1 P2 '
            'Q2 R1 S1 T0 U20 V20 X3 Y3 Z2 [2 ]2',
    # inspect: looking into the loaded, open barrel
    'GRL3': 'A27 B27 C27 D27',
    '2RLN': 'A3', 'SHTN': 'A3', '2RL2': 'A3', 'PLAY': 'A3', 'GLAP': 'A3',
})

FLAMECANNON = _expand({
    # A ready (also dry fire, deselect hold) | the mesh has no raise, lower or
    # sprint poses, and BD21 showed the ready pose for all of them
    # B C D E fireball, resampled over authored 1..5 | H I J K flamethrower,
    # authored FLMF F G alternating -> 6 7
    'FLMG': 'A0 B1 C2 D4 E5 F0 H6 I7 J6 K7 L0 M0 N0 O0 P0 Q0 R0 S0 '
            'T0 U0 V0 W0 X0',
    '2LMG': 'A0', 'PLAY': 'A0',
    'MANA': 'A0 B0 C0 D0 E0 H0 I0 J0 K0',
})

# FlameCannon's fire frames were never keyed: the generator read "####" B..K as
# the MANA sprite (the line above them is the pickup, MANA H). Without these the
# model disappears and a flat sprite shows whenever it fires.
FLAMECANNON_ADD = [('FLMG', f) for f in 'BCDEHIJK']

TABLES = {
    'AssaultShotgun': ASG,
    'Plasma_Gun': PLASMA,
    'GrenadeLauncher': M79,
    'FlameCannon': FLAMECANNON,
}

MESH_FRAMES = {'AssaultShotgun': 32, 'Plasma_Gun': 30, 'GrenadeLauncher': 33, 'FlameCannon': 8}
