# tools/handfit: putting the FBX hands on BD22 guns (snapshot 2026-10-27)

These tools put the FBX hands on 4 guns tonight: BrutalPistol, Flamethrower2, BrutalSMG and MP40. Until now they lived only in the cloud session's workspace; they are committed here so a coder on the owner's PC (or any session) can carry on. **They are a snapshot: many scripts still have the cloud paths (/home/claude/..., /tmp/claude-0/...) hard-coded.** Change those to the local paths before running.

## What is where
- **`fbx_fitter/`:** the FBX-skeleton hand fitter (prototype, "lane C").
  - It reads the FBX hand in pure numpy (`fbxbin.py`, `fbxhand.py`).
  - Grip rules G1-G9 / S1-S6 / U1-U6, landmarks (`landmarks.py`, `gunlm.py`), the 1.92 measurements (`measure192*`), the squeeze pose (`squeeze.py`), and baking to MD3 frames.
  - The FBX source is DXR `models/hands/hand_final.fbx` (owner's private repo; licence unknown). It is NEVER committed or shipped; only the baked MD3 frames ship. Never use the DXR IQM hands.
- **`batch1/`:** ported the r5 pistol and Flamethrower hands from the 1.92 test pack into 1.99: gun move = MODELDEF offsets, plus moving the reload tables, casing port and flame-at-spout.
- **`batch2/`:** BrutalSMG: index re-solve (the pistol hand), bake, gun move, moving the recoil rows (gunmoves pivot/fire rows), the sweep and the checker.
- **`batch3/`:** the method that starts from 1.92:
  - `m192.py` measures 1.92's Ermac hand on a gun: web, palm, cuff, knuckles;
  - `rigid3.py` re-seats the FBX pistol hand there;
  - `curl3.py` closes the fingers and solves the squeeze;
  - `port_b3.py` moves the gun and every dependent table;
  - `bake_b3.py`, `sheet_b3.py`, `sweep3.sh`.
  - The Rifle fit is done but not ported: `curl3_Rifle.json`, `st2_Rifle.npy`.
- `FLAMETHROWER_PARKED.md` and `REPORT.md` hold the rules learned, including the owner's correction that the gas-pump grip IS the pump grip.

## The method: ONE method for every gun (owner)
1. The drawn wrist is pinned to the controller, and the GUN moves to the hand (MODELDEF Offset/Angle).
2. Everything that hangs off the gun moves with it: every gun-hand MODELDEF block, the reload tables (rsr/rsb/rsp rows), the casing port, the recoil rows (gunmoves.zs), the muzzle row (RSQ_Muzzle), the scope table (RSQ_ScopeTable) and the M203 tables.
3. Start every gun from its 1.92 hold (`/home/claude/rsq_weapondepot/docs/reference/bd22q_192_poses` in the Depot repo) or from an existing named pose. Solve from scratch only if nothing fits.
4. Check every gun by eye against its 1.92 render. Nothing is "working" until it is shown working; VR behaviour is "not headset-confirmed" until the owner plays it (on PC VR, qzdoom17, vr_mode 10).

## Testing
- In the cloud: the Depot's `tools/rig` (QuestZDoom 17.3 rig, Linux).
- On the owner's PC: play the pack directly in PC VR. Load order: doom2 -> brutal22test6 -> BD_VoxelPack -> pack.
- Watch saved settings: `rsq_hands 1`, `rsq_scope_sniper 1`, `rsq_scope_railgun 1`.

## Status (2026-10-27 10:00)
- **Done (rig):** BrutalPistol, Flamethrower2, BrutalSMG, MP40.
- **In progress:** Rifle (fitted), Shotvolver (re-seated), BrutalRevolver, Sniper.
- **Then:** the remaining guns.

## `port/port_gun.py`: ONE command for the gun move (batch 4, 2026-10-27)
`python3 tools/handfit/port/port_gun.py <Class> <fit.json> [--src DIR] [--tag "batch 4"] [--dry]`
- Applies the gun move (MODELDEF Offset/ZOffset/Angle/Pitch/Roll on every gun-controller block, count listed) and moves
  every dependent table: gunmoves Pivot + fire rows (rows found from `key[]`, md3 frames from the gun's FrameIndex; the
  original placement must reproduce the shipped rows, asserted), rsr_guns.bd.zs reload case, rsb_guns.zs break rows,
  casing port, RSQ_Muzzle (moved, or added at the drawn tip), RSQ_ScopeTable, the Rifle's M203 (ToGun/FromGun, FwdHook,
  purist handguard hook). Optional `hand` in fit.json wires the FBX gun hand (md3, MODELDEF hand blocks, hands.zs /
  dualhands.zs labels, handtable rows; `support: "move"` moves the existing support pose with the gun).
- fit.json: `shift` (curl3's, cm in the gun's original frame; the gun keeps the approved pistol's r5 aim) or `place`.
- A new gun = one entry in `GUNS` (md3, ready frame, base Scale/Offset, handtable row, reload case, casing key, the bd block).
- Paths: repo-relative (`src/` or `$RSQ_SRC` / `--src`); fitter modules from `../fbx_fitter`. Writes `ported_<Class>.json` (the list) next to the fit.
- Committed in `2a503ff` (first push); Rifle / Shotvolver / BrutalRevolver ported with it in batch 4.
- **Verified:** `port/verify_mp40.sh` re-applies batch 3's MP40 move on 19f0203 and diffs against bdf3fae: byte-identical
  except the BrutalSMG muzzle row that commit also added.

### Batch 4 tools in `port/` (all repo-relative; env overrides listed in each file)
- `gate_gun.py smoke|sheet|hands|compose`: the per-gun rig gate (exclusive lock per engine run, rig ini restored, frame dumps deleted).
  `hands` takes Depot mags.py ids, `brk<Class>:<ammo>:<feed>` (break-open, with the open dump first) and `m203` (the moved rifle's launcher).
- `bake_gun.py <Class> <curl.json> <out>`: bakes trigger / squeeze / pistol-check frames with the wrist where the approved pistol's is.
  Needs `RSQ_HANDS_TOOL` = a full fitter checkout: the snapshot in `fbx_fitter/` lacks its lane data (ref192_pistol.json, results/).
- `reseat_from.py` (rigid re-seat from a given hold), `curl_gun.py [+]<Class>` (index + M/R/P curls), `sniper_fit.py` (the Rifle's hold on the Ruger).
- `fits/`: each gun's fit (shift, hand wiring), the curl / stage-2 data, the baked MD3s, and `ported_<Class>.json` (what the port moved; the M203 gate reads R, t from it).
- Rule found in batch 4: break-open guns (rsb_guns.zs) pass `Offset(i)` to RSB.Hook for the hinged parts AND the round in the off hand, so the
  off-hand RSQ_Hands block moves too, and the hold rows are re-expressed (Hand0-2 = g R^T, HandT = HandT - g R^T t) so the hand's hold is unchanged.
- `poses/<Class>.json` + `port/rebake.py`: each finished gun's solved hand as DATA (full joint vectors for trigger and squeeze, the solved
  fingers, the wrist placement on the gun, the gun move, the FBX source and take). `rebake.py bake poses/<Class>.json <out>` rebuilds the
  MD3 frames from the JSON and a hand FBX with the same skeleton (RSQ_FBX); for Rifle, Revolver and BrutalRevolver it reproduces the
  committed bakes exactly (max 0.0000 md3 units). `rebake.py export <Class>` writes the JSON from a gun's fits/.
  Support hands of these three are still Ermac's (noted in each JSON): no FBX support pose is solved for them yet.

## Destination: RS_Avatar (owner, 2026-10-27)
When the BD22 hands are done, `tools/handfit/poses/` (every gun's pose data: joint angles, wrist placement, gun move, FBX frame) and the re-bake tooling also go to the owner's **RS_Avatar** repo. RS Avatar uses the same FBX hand source for UZDXREMA's hand fitting, so one set of poses serves both. Coordinate with the avatar lane, and don't push into RS_Avatar without the owner's go.
