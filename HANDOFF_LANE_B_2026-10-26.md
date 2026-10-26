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
