# Lane B handoff, 2026-10-26: bd22q 1.99x (branch `lane-b-1.99x`)

Base: `main` 70b0574 (1.99). NOT merged, NOT tagged, NOT released: those wait for the owner.
Every rig result below is from the **QuestZDoom 17.3 rig** (`tools/rig/build/rig`, log line
"QZDoom version 4.14.3", "qz: engine OK"), on doom2 -> brutal22test6 -> BD_VoxelPack -> pack.
Runs from the earlier wrong engine (bin/, 4.15pre) were thrown away and redone.
Evidence (renders, logs) is in `/home/claude/lane_b_out/` and `/home/claude/lane_b_rig/logs/`.

First check: the Depot's `sets/bd22q_1.97/src` and `main`'s `src/` are **byte-identical**
(`diff -rq`: 0 files). No Depot fix is missing from main.

## 1. Done (measured)

### Item 18: "a bang sound when I load into a map". FIXED (`76185df`)
- The sound is **ours**: `Melee/Swing` from our real-punch detector, about 15 tics into every map.
- Cause: about 15 tics into a map the engine re-syncs its VR yaw (`gl_openvr.cpp`,
  `resetDoomYaw`). The hand's world position swings round the body **in one tic**. Measured in
  the rig (body frame): lf -10.2 -> +10.2, ll -8.5 -> +8.5, about 27 m/s. `RSQ_FistHand` read that
  as a jab and played Melee/Swing plus a punch. It happens only with `rsq_punch 1`.
- Fix: a one-tic step over 0.5 m (17.5 m/s, faster than any arm) is treated as the frame
  moving, and the punch history starts again.
- Second, related regression found on the way: `OffPunch` (hands.zs) **ignored `rsq_punch`**.
  With punching off, an off-trigger press away from the gun still swung and punched; 1.92
  never did. The owner's call (2026-10-25) is "off-hand punch stays behind rsq_punch". It is
  now gated.
- Rig, QZ_SNDLOG, map01 -> map02 -> map03 (-> map04), Rifle/Axe/Pistol, rsq_punch 1:
  1.99 gives 2 Melee/Swing per run, this build gives 0. Off trigger 60 cm from the gun:
  rsq_punch 0 gives 1.92 none, 1.99 a swing, this build none; rsq_punch 1 swings. A deliberate
  punch still lands (`lb_fix18_punchlive`).
- No other pack sound at map load. With no pack, 1.92 and 1.99 compared over map changes,
  save/load and all six BD22 classes, the remaining differences are BD22's own select or reload
  sounds, which the pack's VR reload replaces by design.
- If the owner hears a bang with `rsq_punch 0`, it is not this. Ask what he holds and which class he plays.

### Item 10: magazine-in-hand poses for the F10 guns. 3 of 9 refitted (`7ba55d7`); 6 need an owner look
- Method: Ermac's authored ammo_hand holds (Rusted Legacy, MIT; `ammo_hand.md3` frames 0-8,
  the same file we ship, byte-identical). For each frame, the hand's contact patch is the hand
  vertices within 1.5 cm of **his** part in that frame. Our part is fitted onto that patch by
  trimmed ICP, translation only, because `Place(HANDMAG)` adds only `HandHook` and the part keeps
  its seated orientation. The fit is penalised for hand vertices inside our part (ray parity).
  All 9 parts x 9 frames were scored. Tools: scratchpad `fit10b.py` and `rend_cand.py`
  (Depot's kit rgeo/hudrender, read-only).
- Changed:
  - Flamethrower canister: frame 3, contact gap 0.82 cm. Before, it floated under the hand.
  - Nuker block: frame 6 (Ermac's BFG pod hold), gap 0.81 cm. Before, 18 cm above the palm.
  - Hellish drum: frame 6, gap 1.11 cm. Before, 28 cm off.
  - New `RsrHoldPod` state (RQHN M -> ammo_hand frame 6), chosen per gun by
    `RSR_ReloadHandler.HoldState` (15, 16).
  - `TopInHand` / `HandHook` rows in `rsr_guns.bd.zs` (HandHook = shift_hook(TopInHand - Well), checked).
- In-engine CARRY renders, main vs this build: `carry_main_vs_lb.png` (Flamethrower, Hellish)
  and `carry_nuker_main_vs_lb.png` (Nuker, 3 angles; this build shows the block in the off hand,
  main shows the hand under it). Offline 3-view sheets: `item10_candidates.png` (now / frame-3
  fit / best frame, per gun).
- Not changed, deliberately: MG42 drum, M32 cylinder, Unmaker skull, Devastator bay, Minigun box,
  Machinegun box. They already sit in the frame-3 palm, 2.4 to 5.7 cm off Ermac's magazine
  centre, measured. Their best-scoring alternatives are visual judgement calls (see Owner questions).

### "Reload Non-Standard Guns" option. BUILT (`7ba55d7`)
- `rsq_reload_nonstd`, **user** bool, default **on**. The row is on the BD22 VR Weapons page,
  right after "Reloading". It is `user` like `rsr_reload` because it is read per player with
  `RSQ.PlayerInt` and gates only that player's own reload and counters.
- Non-standard, parsed from brutal22test6 `actors/Weapons/*.dec`:
  - No `Reload:` state at all: MG42, MiniGun, IncendiaryLauncher, Unmaker, Devastator,
    NukeLauncher, HellishMissileLauncher.
  - Flamethrower2: its `Reload:` label is only its dry-ready loop, and BD22 never jumps to it
    (0 references).
  - BD21 Machinegun (docs/BD21_Machinegun.txt): its Reload reloads only the underbarrel grenade.
  - That is exactly `RSQ_Counters.GUN[]`, the 9 counter guns.
- Standard, untouched: every gun with a reachable BD22 Reload: Rifle, Pistol, SMG, MP40,
  AssaultShotgun, RailGun, Plasma, Sniper, Rocket_Launcher, Shotgun, SSG, GrenadeLauncher,
  Revolver(2).
- Off: the counter idles (no `RSQ_Empty`, and a magazine left out is put back) and `RSR_Start`
  refuses the gun, so its Reload falls through to Ready.
- Rig, all 9 guns, `+reload` then fire held 150 tics:
  - Off: no reload phase, no script error, shot counts equal to `rsr_reload 0` (BD22 stock path):
    Minigun 54/54, Machinegun 54/54, Flamethrower 168/168, Devastator 36/36, Hellish 23/23,
    M32 2/2, Nuker 1/1, MG42 110/114, Unmaker 150/151 (one-shot jitter from timing under load).
  - On: IDLE -> EMPTY -> DROP as before.
  - Logs: `logs/lb_ns0_*`, `lb_ns1_*`, `lb_nsstock_*`.

### Items 13 / 15 (Machinegun box, M32 in the headset): the weapon code path, tested
- Owner's lead: "our chaingun weapon code hasn't been written to support reloading". Checked
  per gun. Every non-standard gun's Ready loop has the posefix line
  `A_JumpIfInventory("Reloading",1,"Reload")`. That is the path BD22 itself uses: its ACS
  "CheckWeaponAction" gives `Reloading` on a BT_RELOAD edge. The Machinegun also has
  `WRF_ALLOWRELOAD`.
- The rig drives reload with `+reload`, which is BT_RELOAD, the same usercmd bit a bound
  controller button sends. So the rig does **not** bypass the real path. `+oh_reload`
  (BT_OFFHANDRELOAD, `rsr_magrelease`) also works.
- **Found and fixed (`589353a`): the Minigun did not reload while spun up.** BD22's spun idle
  loop `Ready2` calls A_WeaponReady but never reads `Reloading`. After alt-fire spin, the button
  did nothing (rig: main no reload; this build IDLE -> EMPTY -> DROP). That fits "we cannot
  reload it". The other spun or dry loops (Machinegun IdleNoAmmo, Flamethrower ReadyDry) are
  reached only with no reserve, where there is nothing to reload.
- With the 17.3 rig, BDoomer class, realistic reserves: Machinegun reloads on the button at a
  full reserve and at 50 rounds, and auto-reloads when the box empties (Clip2 160).
  M32 reloads on the button with 3 rounds; Minigun at 50.
- **What still blocks the M32 / MG42 in the headset is the capacity (owner question below),
  not the input path.** Measured: AmmoM202 MaxAmount 4 vs M32 cylinder 6, so a full reserve of
  4 makes a full cylinder of 4 and `Reload` jumps to Ready ("full"). M32 fired to empty from 4
  then +reload: no reload (`lb_auto_m32_4`), because the counter and the reserve empty together
  and there is nothing left to load. MG42: Clip2 MaxAmount 200 vs drum 200; at a full reserve
  the drum is "full" and the button does nothing.
- Quest input facts (VrInputDefault.cpp + engine/vr/defbind*.txt): off trigger = KEY_LSHIFT
  (`+oh_attack`); off grip = KEY_PAD_RTHUMB (443, rsr_grip_keys); in the owner's own layout
  (defbind3) reload is **R grip + R stick down** (`axis8minus +reload`). There is no single
  reload button, so a missed reload in the headset may also be the input. Ask him (below).

### Item 11 (weapons coming apart when grabbed). Rig evidence for his next pass
- Steadied grab (off grip within 50 cm, so the engine re-aims) rendered side-on, main vs this
  build: pistol after its last shot (slide locked), pistol at rest, SSG during its reload.
  `item11_pistol_locked_steadied_main_vs_lb.png`, `item11_steady_main_vs_lb.png`.
  The parts stay on the gun in every shot. Recoil (the cause of the earlier splits) is out since
  1.99. Not reproduced in the rig.

### Regression pass vs 1.92 (cmp2, 1.92 left, this build right)
- `cmp2_a.png`: Pistol, Rifle, SMG, Shotgun, SSG, AssaultShotgun, Plasma, Railgun are identical.
- `cmp2_b.png`, `cmp2_c.png`:
  - BFG, BFG10k (the 1.92 frame caught it mid-raise), Nuker, Chainsaw, Axe and GrenadeLauncher
    match.
  - Sniper and M32 differ on purpose: 1.92 had no model for them (it drew a Rifle); 1.93+ has
    the XM21 and M32 meshes.
  - Revolver, Rocket_Launcher, Minigun, Unmaker, Flamethrower2, DSweap and MG42 show the default
    rifle on one side: those are rig select-timing misses, not pose changes. Re-shoot them
    before calling them; hand tables are byte-identical to 1.92 for every 1.92 gun (Depot doc A6).
- Full give/select/fire/alt-fire/reload sweep, all 31 classes, class BDoomer, ballistics 2:
  **no pack script error, no VM abort** (`logs/sw_lb_*`). Only BD22's own `Deh_Actor_153` and
  BD_VoxelPack's `DeathSphereHealth` / voxeldef lines, also present with no pack.
- Reload paths:
  - **All 18** magazine reloads go IDLE>EMPTY>DROP>EMPTY>CARRY>INSERT>SEATED>DONE>IDLE (mags.py).
    The Nuker's harness needs the blast to clear and a nuke re-given first (it carries one).
  - Rifle and Machinegun M203: "shut: loaded".
  - Spin test: psp x/y stay 0/32 through walk, fire and reload; one flash per shot.
- RailGun and Sniper with Real scope mode, eye at the eyepiece: no VM abort. No `out Vector`
  parameter anywhere in our zscript (Lane A's REGT_ADDROF crash does not apply).
- RQLK lock-ring art: RQLKA0-D0.png **are in main's pk3** (src/sprites). The Depot's "no lump"
  note is stale.

## 2. Not done
- Items 10's other six parts (above): need the owner's eye on `item10_candidates.png`.
- Item 19 (BFG sounds): no pack change. Audit: none of BD22's 8 BFG / BFG10k sound names
  (BFG/Charge, BFG/Draw, BFG/Fire, BFG10K/*, FAREXPL) is redefined by our SNDINFO. Globally, 0
  sound names of BD22 are redefined and 0 of our sound files share an 8-char lump with BD22
  (the A4 fix holds). Nothing of ours can change a BFG sound, so we need his description.
- Item 21 (Ruger scope default): not changed (owner call).
- Item 14 (Machinegun 40 mm height), 16 / 17 (melee), 20 (voxel shells), 8 / 9 (grip nudges):
  the Depot's fixes are in main and unchanged here. M203 load passes on both guns. No new
  headset evidence beyond the cmp2 sheets.
- Dual wield and flick reload: not driven this session.
- Minigun's bigger in-hand box: owner-later, not built.

## 3. Open
- cmp2 re-shoot of the seven "default rifle" tiles (select timing).
- The rig's `qz_lgrip` steadying could not be confirmed from the probe (no "steadied" log line);
  the renders show the re-aim happened.

## 4. Owner questions
1. **Capacities (do not change without you):** M32 cylinder 6 vs BD22's AmmoM202 max 4, and MG42
   drum 200 vs Clip2 max 200. A counter is a real magazine only below the reserve max: at a full
   reserve the gun reads "full" and the reload button does nothing. Options: M32 cylinder 4 (or
   3), MG42 drum 100 (as the Minigun and Machinegun now), or leave them.
2. Which button do you press to reload on the Quest? Your layout puts `+reload` on R grip +
   R stick down. Is that what you used on the Machinegun and the M32?
3. Item 10: the six parts not refitted (MG42 drum, M32 cylinder, Unmaker, Devastator, Minigun
   box, Machinegun box). Are they right as they are? Sheet `item10_candidates.png`, row "now".
4. Item 19: which BFG sound is wrong (charge, fire, draw, explosion), and does it still happen
   after 1.99's A4 lump fix? The pack has none of the BFG's sounds.
5. Item 21: Ruger scope default Dot or Real? Real is a second full scene render (mono, 256x256
   camera texture) **only while your eye is behind the eyepiece** (scope_real.zs gate), one
   frame stale. Off the scope it costs nothing.
6. Free charge default and PuristSniper model: still yours to call. PLAN records free charge
   "stays off"; PuristSniper "stays out".

---

# Round 2/3 (2026-10-26, afternoon/evening): branch `lane-b-1.99x`

Rig: QuestZDoom 17.3 (`tools/rig/build/rig`, "QZDoom version 4.14.3"), doom2 -> brutal22test6 ->
BD_VoxelPack -> pack, `flock -o -s /home/claude/rig.lock`, at most 2 engines. Evidence in
`/home/claude/lane_b_out/` (r3_*, r3fix_*), logs in `/home/claude/lane_b_rig/logs/` (r3*, cmp3_r3fix_*).
Round 2 was interrupted at 14:06 and the container restarted once mid round 3: every run in flight
then was voided and re-run.

## 1. Done (measured)

### "All of the hand poses are off": FOUND and FIXED (`44792ab`)
- The round-2 1.92 comparison (`pose_vs_192_*.png`) showed real, deterministic differences on 21 of
  26 guns at rest. They were not bob phase: the last 3 settled frames of each build are 0-8 px apart,
  1.92 vs ours 360-4328 px.
- Ruled out, file by file: handtable rows (identical for every 1.92 gun except the deliberate ones
  below), MODELDEF hand blocks, `hand.md3` (frames 0-43 vertex-identical; 1.95 only appended 44-45),
  the free hand's MODELDEF and layer state (probe: same sprite/frame on every layer).
- Bisected in the rig (the `1.92` tag is byte-identical to `BD22Q_192.pk3`): already present in 1.95.
  1.95 with 1.92's `MODELDEF.*` still differs; **1.95 with 1.92's `gunmoves.zs` alone renders the
  Plasma pixel-identical to 1.92** (0 px).
- Cause: 1.95 (413b3cc) switched off the Sniper's six recoil rows in `RSQ_GunMoves.Frame` by keying
  them to gun 0. A probe that called `Frame()` for every (gun, sprite, frame) in the table showed
  670 of 2680 lookups for OTHER guns returning a different row than 1.92 (e.g. Plasma at rest:
  turn 3.10 / move 9.18 instead of 0). `FollowGun` feeds that to the gun and support hand layers,
  so every hand sat off its fit. Measured, not explained: why key 0 does this on 17.3's VM was not
  isolated (same loop, same arrays). Keyed to 99 (no gun) all 2680 lookups equal 1.92's.
- After (`r3fix_<Class>.png` = this build alone; comparison numbers vs the round-2 1.92 frames):
  19 guns 0-1 px from 1.92 (were 360-4328). Remaining differences are all deliberate (table below).

### Flamethrower (owner: "the flamethrower is wrong")
- At rest, steadied (off grip at the gun), firing and after firing, this build vs 1.92:
  rest 8 px, steadied 3 px, i.e. identical. Firing / after firing differ only in the flame and
  smoke particles (random), the hand and gun are the same (`r3_flamethrower_{rest,steady,firing,afterfire}.png`).
- Round 2's Flamethrower2_* tiles were rendered BEFORE the fix, with the gunmoves bug present; their
  hand differences are this bug.
- So what the owner sees is **1.92's own Flamethrower pose** (a separate prototype scored it 3 of 12
  grip rules: support hand 5 cm inside the gun, index 8 cm off the trigger) plus, in builds up to
  9ab84cb, the gunmoves offset. Not re-posed here (no new hand poses; the hand fitter is for that).

### Item 3: dual wield and flick reload, driven in the rig (real input: +user3, +attack/+oh_attack, controller pitch)
- Pistol Start gives the off-hand pistol; Dual key -> `RSQ_Off_BrutalPistol` in the off hand; both
  fire per hand (mag 16 -> 12 each); off controller snapped from +30 to -30 deg in one tic -> the OFF
  pistol alone reloads (BD22 Reload, offmag 12 -> 16, reserve Clip1 60 -> 56); main controller the
  same -> the MAIN pistol alone (12 -> 16, 56 -> 52); Dual key again -> fist. Identical to 1.92 on the
  same input (reserve 60/56/52). No VM abort, no crash. `r3_dual_flick.png`, `r3_dual_flick.log`.
- Machinegun launcher (M203): rig `m203.py GUN=mg` on this build: latch, open 9.7 cm, round in,
  "shut: loaded" (log `m203mg.log`, `r3_m203mg_side_lb3.log`).

### Item 14 (Machinegun 40 mm height): headset evidence
- Side view with the tube open and the round home, main 1.99 vs this build
  (`r3_item14_mg_m203_seated.png`, sequence `r3_item14_mg_m203_sequence.png`). The round sits on
  the tube's bore line (RSM_Geo gun 2: bore U -6.517, from the mesh with ZOffset -5, `41d1c3b`).
  No change this round; main and this build are the same here.

### Items 16/17 (axe and sword): headset evidence
- Rig, Two-Handed Steadying OFF (`vr_two_handed_weapons false`), off grip held 22 cm from the
  weapon: axe `RSVR_MeleeTwo 1, RSVR_AxeTwo 1`, engine steadying 0; sword `RSVR_MeleeTwo 1`,
  steadying 0. Released: all 0. One controller drives it. `r3_item16_melee_twohand.png`.
  With steadying ON the axe also reports steadied 1 (the engine's grab, as documented: menu row).
- Swings (0.3 m/tic, 3 directions): UP: no swing sound, no cut, axe and sword; DOWN: Axe/Swing,
  Melee/SwingStrong; SIDE: the same. Logs `r3_item16_17_{axens,swordns}.log` (QZSND lines).

### Item 20 (voxel casing scale): headset evidence
- Rifle, "Spent casings" voxels ON: EmptyBrass scale 0.153 (BD22 with no pack: 0.150); OFF (3D
  mesh lend): 1.000 with the real-size mesh, as designed. `r3_item20_vox1.log`, `r3_item20_nopack.log`.

## 2. Not done
- No new hand poses for guns whose 1.92 pose is itself bad (Flamethrower, see above): for the fitter.
- Round 1's seven "wrong gun" cmp2 tiles: superseded by the r3fix set (every gun's held class is
  printed on its tile and logged by LBW), not re-shot separately.
- The six un-refitted in-hand parts (item 10) and the other owner calls: unchanged.

## 3. Open
- Why gun key 0 misreads on 17.3 is not explained (measured only). `gunmoves.zs` now says so; keep 0 out of `key[]`.
- The gunmoves generator (`rsq_gunmoves_gen.py`, depot_import) was not re-run; 413b3cc's key edit was by hand.

## 4. Owner questions (unchanged unless noted)
1. Item 10: the six un-refitted in-hand parts (`item10_candidates.png`, row "now").
2. Free-charge default; PuristSniper model.
3. Item 19: which BFG sound is wrong.
4. NEW: the Flamethrower at rest is now exactly 1.92's. Is it 1.92's pose you dislike (then it goes
   to the hand fitter), or was it the offset this round fixed?

## Every gun at rest vs 1.92 (this build, `r3fix_*`)
| Gun | Result |
|---|---|
| AssaultShotgun, BFG10k, BIG_FUCKING_GUN, BrutalPistol, BrutalSMG, Devastator, Flamethrower2, GrenadeLauncher, HellishMissileLauncher, MG42, MP40, Minigun, Plasma_Gun, Revolver, Rifle, Rocket_Launcher, SSG, Shot_Gun, Unmaker | same as 1.92 (0-1 px); 16 of them were off before `44792ab` (gunmoves key 0) |
| IncendiaryLauncher | differs on purpose: grip 2 cm forward (item 9, owner) |
| NukeLauncher | differs on purpose: hands from the BFG (item 7) |
| RailGun | grip same; scope glass / dot (1.96b) |
| Sniper | 1.92 had no Sniper (drew a Rifle); XM21 mesh since 1.95 |
| BrutalAxe | 1.95 two-handed placement tables (164 px, owner 2026-10-23) |
| Chain_saw | 2 cm left + trigger finger (item 8, 1.95) |
| DSweap | not a 1.92 weapon fit (Dragonslayer fit 2026-10-23) |
| Flamethrower2 (1.92 itself) | 1.92's pose is the one a prototype scored 3/12: for the hand fitter |

## Gated test pk3 (round 3)
`/home/claude/lane_b_out/BD22_VR-Reloaded_1.99x-lb-r3.pk3`, built from `1953013` (src identical to
`44792ab`), sha256 `7061efe3ab4e948214cdf32b659e3bfab69f9702e736c1c847d6457d57e150d9`.
Gate (`lane_b_rig/sweep.sh`, logs `sw_r3_*`): all 31 classes given, selected (held class logged),
fired, alt-fired, reload button pressed, fired again; class BDoomer, rsr_reload 1, ballistics 2.
0 pack script errors, 0 VM aborts, 0 crashes. The only error lines are BD_VoxelPack's own (four
voxeldef lines, DeathSphereHealth), present with no pack too. Not yet on the owner's headset.

---

# Round 4 (2026-10-27): branch `lane-b-1.99x`, the owner's r3 headset report items 1-7

Rig: QuestZDoom 17.3 (`/home/claude/rsq_weapondepot/tools/rig/bin`, "qz: engine OK"), doom2 ->
brutal22test6 -> BD_VoxelPack -> pack, `flock -o -s /home/claude/rig.lock`, one engine at a time.
Driver `/home/claude/lane_b_r4/run.sh`, test-only probe `/home/claude/lane_b_r4/r4probe.pk3` (logs
casings, shot origins, hand-follow rows, damage, all in the controller frame, cm). Logs in
`/home/claude/lane_b_r4/logs/`. Sheet: `/home/claude/lane_b_out/r4_fixes.png`. r3 = the delivered
`BD22_VR-Reloaded_1.99x-lb-r3.pk3` (7061efe3), r4 = this round.

## 1. Done (measured)

### Item 1: over-under machine gun (Machinegun) casings out of the barrel. FIXED (`1769b47`)
- Port re-measured off `Machinegun.md3` frame 4 with the Depot's own `bd22_plus.eject_port`
  (boundary loop, 18 verts): mesh (43.41, -0.27, -4.20) -> controller F 14.3 L -0.3 U -4.3 cm.
  The shipped number was right.
- Cause was timing. BD22's casing spawner (`50CaseSpawn2`, Casing.dec) is a Speed 20 projectile;
  the case is born where the spawner has flown to. `casings.zs` moved it to the port on the NEXT
  WorldTick, so every case was drawn for one tic out in front. Rig, first shot: r3 EmptyBrass age 0
  at F 91.5, MGLinks at 155.3 (the gun ends at 68.8); age 1 at the port.
- Fix: place in `WorldThingSpawned`, which the engine calls from the fresh-thinker pass with target
  and vel already set (dthinker.cpp: CallPostBeginPlay, then the first Tick, same tic).
  r4: EmptyBrass and MGLinks age 0 at F 14.9 L -0.3 U -6.0 (the port; the probe's own
  pixelstretch round trip reads U about 1.3 low), then down the chute. Applies to every gun's brass.
- Rig frames at 480 px do not resolve a 5 cm case at arm's length (tried four poses, casing size
  x4); the sheet plots the rig-logged positions on the mesh instead.

### Item 2: Ruger/XM21 bullets from below the barrel. FIXED (`02f433e`)
- Muzzle measured off `XM21.md3` (frame 0, surface 9 = body and barrel) through MODELDEF.rsr's chain
  (Depot `tools/kit/rgeo.py to_flu`): tip F 62.34, bore L 0.28 U 5.03 (constant from F 45 to the
  tip). The controller, where QZD 17.3 starts every player shot (AttackPos), is 62 cm behind and
  5 cm under it.
- New `zscript/rsq/muzzle.zs` (`RSQ_Muzzle`): hitscans re-fired with `LineAttack(LAF_ABSPOSITION)`
  from the muzzle, same angle/pitch/damage/puff/range/flags, direction still the engine's AttackDir;
  BD22's trail-only rail (damage 0, "Gray") redrawn by `Actor.RailAttack` from a mount at the muzzle
  with the same FRailParams. Wall guard: if the hand-to-muzzle line hits geometry, nothing moves.
- Rig: r3 all three hitscans and both rails from (0, 0, 0); r4 hitscans and trail from
  (62.5, 0.3, 3.8). The damaging rail (30, colour None, invisible) still starts at the controller
  on purpose: fired from a mount its kills would not be the player's.
- The rig does not draw particle rail trails in its frame dumps (none visible on r3 either), so the
  evidence is the log, plotted on the mesh in the sheet.

### Item 3: Minigun hand keeps shaking with the barrel spin. FIXED (`a347fb5`)
- Measured per surface vs ready frame 4 (`Minigun.md3`, Scale -1 1 1, ZOffset -5): in frames
  5, 6, 7, 9, 11 the body (`Runko` x3, `Grip`) moves 0.00 cm and only `Pipe` (the barrels) turns;
  in frames 8 and 10 the body moves 2.04 cm straight back, no turn.
- `gunmoves.zs` rows 46-48 and 50-52 had been fitted to the whole mesh, barrels included, and read
  the spin as a 0.5-1.9 degree turn. Now 5-7/9/11 are zero and 8/10 are the 2.04 cm kick (row 49
  already was).
- Rig, fire 20 tics then release, spin-down tics 294-360: hand turned in 45 of 57 tics (r3), 0 of 57
  (r4). While firing the hand still kicks 2.04 cm with the frame.

### Item 4: Unmaker, only the top half of the skull comes out. FIXED (`0a9f677`)
- The RS VR Weapons version: Depot `sets/plus_0.7` `unmaker_wm.md3` (MODELDEF.rsr `WM_VP_Unmaker`).
  Same mesh: surfaces of 10931 / 361 / 249 verts, as ours. It draws surfaces 1 (flap) AND 2 (lever)
  as the part. Ours drew only 1 (`magazine`); 2 (`magazine#2`, the jaw) stayed on the gun.
  bd22_plus.py's card meant both (`ref_parts skull, skull2 -> magazine`).
- MODELDEF.rsr: gun = surface 0 only; part, hand and dropped skull = 1 + 2.
- Rig, reload to CARRY with the skull held clear of the gun: r3 vs r4 differ in exactly two places,
  the gun's socket (about 300 px) and the hand (about 280 px): the jaw moved from gun to hand.

### Item 5: IDKFA gives neither revolver. FIXED (`1534fd7`)
- Cause: with "Shotvolver Swap" on, the Revolver class was replaced (roster.zs), and the engine's
  give-weapons cheat skips any replaced weapon (player_cheat.zs); Revolver2 had CHEATNOTWEAPON.
  Rig r3: swap off gives Revolver only; swap on gives neither (the owner's report).
- Also found: the swap never reached map pickups. BD22's `RevolverSpawner` gives "Revolver" with
  A_GiveInventory (NO_REPLACE). Rig r3, swap on: the pickup gave the BD22 Revolver.
- Fix: Revolver2 not CHEATNOTWEAPON (it is in slot 2 via KEYCONF.rsq); the swap now replaces
  `RevolverSpawner` with `RSQ_ShotvolverSpawner` (DECORATE.rsqrev: Revolver2 + 6 Clip2, the same 6
  rounds BD22's spawner gives and one full cylinder, RevolverAmmo MaxAmount 6).
- Rig r4: idkfa gives Revolver AND Revolver2, swap on or off, on all five BD22 classes (Purist,
  Doomer2 pistol, BDoomer rifle, Doomer3 melee, TacticalDoomer). PuristRevolver stays
  CHEATNOTWEAPON (BD22's own). Pickup, swap on: Revolver2 + Clip2 30 -> 36; swap off: BD22 Revolver.
- Not swapped: a Revolver placed directly by editor number 5874 (no Doom 2 map has one).
- For the owner's slug check: the menu row is "Shotvolver Slugshot Alt Fire" (`rsa_rev_magnum`,
  default off).

### Item 6: butt strike range. EXTENDED (`fc43821`)
- Old: the hit volume was the gun itself, the stock-to-forward segment, padded 5 map units (15 cm).
- New: plus a sweep 60 units ahead of the stock along the stock's motion, padded 12. Why those:
  BD22's own kick (Melee.dec `KickAttack`: FastProjectile Speed 30, lives 2 tics `TNT1 AA 1`,
  Radius 12, fired from the controller in VR), i.e. 72 units (2.1 m) of reach. The blow gates
  (speed, butt leading, two hands) and the hand-to-target `Clear` line are unchanged.
- Rig, steadied two-handed Rifle stroke (off grip 35 cm ahead, gun hand swept 15 cm/tic about it),
  frozen zombieman ahead: r3 hits at 40 units only (55, 70, 90, 105, 120: miss); r4 hits at 40, 55,
  70, 90, 105, misses at 120 (stock about 13 units ahead of the pawn + 60 + 12 + radius 16).

### Item 7: option renamed. DONE (`d10b3c2`)
- MENUDEF.rsq: "Shotvolver Swap for Revolver" (On/Off). Cvar `rsq_slug_replaces_shotvolver` kept so
  saved settings carry over. README updated.
- Rig: `openmenu RSQ_Options` renders the row "Shotvolver Swap for Revolver  OFF"
  (`/home/claude/lane_b_out/r4_item7_menu.png`).

### Gated test pk3 (round 4)
`/home/claude/lane_b_out/BD22_VR-Reloaded_1.99x-lb-r4.pk3`, built from `d10b3c2`, sha256
`0ce5ec20c329397764880c88a4918efe408d9b0d54e6614b235c85e2b5e452cc`.
Gate (`/home/claude/lane_b_r4/sweep.sh`, logs `logs/sw_r4_*`, one engine at a time): all 31 classes
given, selected, fired, alt-fired, reload button, fired again; BDoomer, rsr_reload 1, ballistics 2.
0 pack script errors, 0 VM aborts. The only error lines are BD_VoxelPack's 4 voxeldef lines (baseline).
Every gun's shot count and reload phases equal r3's, except the Unmaker (r3 20 shot tics, r4 16):
re-run twice per build, it is 16 or 20 on BOTH builds (trigger-release jitter), so not a regression.
Not yet on the owner's headset.

## 2. Not done
- Items 8-15 of the report (chainsaw, axe, sword, reload capacities, dual-wield options, Ruger
  scope, revolver mesh): out of this round's scope.
- No rig frame shows a casing or the particle rail trail (see items 1-2); those two are evidenced by
  the rig log plotted on the mesh.
- Butt strike through a wall: not driven; the unchanged hand-to-target `Clear` trace gates it.

## 3. Open
- Item 2 moves the hitscans and the visible trail only. Should the Ruger's damaging rail also start
  at the muzzle? Possible only from a mount, which would take the kill credit off the player.
- Item 5: the swap's map-pickup half never worked before r4 (BD22's spawner bypasses class
  replacement). Worth the owner checking a revolver pickup with the swap ON.
- Item 6: 72 units (2.1 m) is the kick's reach; if it feels too long in the headset, BUTT_REACH
  (melee.zs) is the one number.
- Queued after r4 (coordinator): the Moonlight revolver as BD22's normal revolver mesh with a
  break-open speedloader reload (reference/moonlight/README.md). Not started.

---

# Moonlight revolver (queued task), time box 05:59-06:44 2026-10-27

## Done (measured)
- 41-frame contact sheet, side view, per surface: `reference/moonlight/moonlight_41frames.png`.
- The frames DO contain a break-open, an eject and a speedloader (no blocker). Frame map,
  surfaces, placement, hinge, chambers, cylinder and loader seat: `reference/moonlight/README.md`
  "Measured", reproducible with `measure_moonlight.py` (output `measured.txt`).
- The Depot's hand-fitted `rev_wm.md3` is rev.md3 frame 0 moved rigidly (residual 0), so the fit carries to
  all 41 frames: `Scale 1.35 / Offset 0.0262 0.9224 / ZOffset 0.5878`. Rig (QZD 17.3, test-only
  pk3, not in src): frame 0 sits in the existing revolver hand fit (row 17), frame 26 shows the open
  break-top (`moonlight_rig_frame0_vs_26.png`); 0 script errors of ours.

## Half done
- Speedloader baked into frame 0 at its seat (closed-part frame), test asset only
  (`/home/claude/lane_b_r4/moon/bake.py` -> `moontest/models/moon/rev_seat.md3`, normals not
  re-baked). Not in src.

## Not done (next, in order)
1. Meshes into src: `models/bd/Moonlight/rev.md3` + a reload copy with the loader baked at the seat
   (bake.py) -> gun = surfaces 0+2, part = 1+3, loader = 10 (+ rounds 4-9 for per-round mode).
2. RSB: new rows in `rsb_guns.zs` cloned from the BD22 Revolver's speedloader entry (index 3; per
   round 7) with the measured Hinge (8.46, 0, -1.14), Axis (0, 1, 0), OpenDeg 63.3, seat
   Base/Tip/Bore on the loader axis, Scale/Offset of the new placement; MODELDEF.rsb gun/part/loader
   blocks (RBRG/RBRP/RBRW pattern). Revolver2 (the Shotvolver) keeps index 8/9 and Revolver.md3.
3. MODELDEF: BD22 Revolver's sprite frames -> rev.md3 (ready 0; fire recoil 1-14), replacing the
   411-line Revolver.md3 map.
4. `gunmoves.zs` Revolver rows are fitted to Revolver.md3's recoil frames: re-fit them to the
   Moonlight's frame body only (the item 3 lesson), or the hand moves against a still gun.
5. Rig: `tools/rig/brk.py` (break, load, flick shut) on the Revolver, speedloader and per-round feed;
   then the 31-gun sweep.
