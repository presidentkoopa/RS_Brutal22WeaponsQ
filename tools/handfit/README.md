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
