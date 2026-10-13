# Handoff 2026-10-11: Quest packs, avatar grip points, and the tools

For the coders. This covers everything from the 2026-10-03 → 2026-10-11 session: what was made, how to check it, and what to commit and push. Nothing below has been committed.

## 1. What was made

**A. Quest (QuestZDoom 17.3): BD22 hands, reload and ballistics**
- File: `E:\DOOMWork\RS_BD22_Models_v8.pk3`.
- Load order: `brutal22test6.pk3`, then this pack.
- It gives posed hands on every BD22 gun.
- Reloading can be stock or immersive, and ballistics stock or ours, both switchable in the options menu.
- Sources and the full write-up are in `RS_QuestHands\tools\posefix\`; start with `README.md` and `hands\HAND_FITTING.md`.
- Still needs a headset test.

**B. Quest: Vanilla VR Plus add-on**
- File: `E:\DOOMWork\RS_VanillaVRPlus_VR.pk3`.
- Load order: Doom or Doom 2, the owner's `1.0b_Weapons_VanillaVRPlus_v1.2` set, then this pack.
- It gives the same hands, reload and ballistics for that set. Never load it together with A.
- It also carries a fix for a crash in the set: with default weapon switching, switching away from the M16 or the revolvers overflows the stack.
- Sources are in `RS_QuestHands\tools\posefix\vplus\`, described in the posefix README section "Vanilla VR Plus add-on".
- Still needs a headset test.

**C. REMA: the avatar's hands on the guns**
- 72 guns now have new `palm`, `rake` and `supportat` in their card grip blocks, fitted to c_doom_marine's hand.
- They span 18 card files in `RS_VR_Weapons`:
  - `WMCARD.01_pistol` … `WMCARD.14_magazine_shotgun` and `WMCARD.grenade`
  - `bd22\WMCARD.bd22`
  - `RS_Modern\WMCARD.breach` and `RS_Modern\WMCARD.breach_set`
- Only those grip lines changed, plus one comment line per gun.
- Originals and the diff are in `_backups\avatar_grip_2026-10-10\`.
- Build and test steps are in `_reports\avatar_grip_2026-10-10\HANDOFF_build_and_test.md`.
- There is no engine change and no script change. The installed `RS_VR_Reload.pk3` already reads `rake`.

**D. The tools that did C**
- They live in `E:\DOOMWork\tools\avatar_grip\`. The README covers the process, the rules, the per-gun options and the known limits.
- A full copy of the source is in the claude.ai project as `avatar_grip_tools_source.md`.
- These are the tools for putting hands on every future weapon set. Keep them safe.

## 2. Check before committing

1. **C, build:** rebuild the three REMA packs in this order, using the handoff in C:
   - `RS_VR_Weapons\build.ps1`
   - `RS_VR_Weapons\bd22\build.ps1`
   - `RS_VR_Weapons\RS_Modern\build.ps1`
2. **C, cards in the packs:** each pack should have the comment `fitted 2026-10-10` once per gun: 37, 25 and 10.
3. **C, boot test:** `tools\main_boottest\main_boottest.ps1` should report `BOOT: ok` with no script errors.
4. **C, headset:**
   - Turn on `vr_gun_anchor_hand 1` to see the avatar's hands on the grips.
   - Saved `vr_gundata_palm_*` / `vr_gundata_sup_*` lines in `doomxr.ini` override the cards, so blank them for the guns being tested.
   - The gun list to check is in the C handoff.
5. **D, tools:** run `cd tools\avatar_grip` then `python table.py`.
   - This proves the tools run on this PC. It needs numpy, scipy and Pillow.
   - It writes only to `tools\avatar_grip\out\`. Don't commit `out\`.
6. **A and B:** the owner tests these in the headset. Nothing to rebuild.

## 3. Commit and push

**`RS_VR_Weapons` repo** (remote `origin` = github.com/presidentkoopa/RS_VR_Weapons, branch `main`). Commit after step 2 passes, by explicit path only:

```
cd E:\DOOMWork\RS_VR_Weapons
git add WMCARD.01_pistol WMCARD.02_pump WMCARD.03_revolver_breaktop WMCARD.04_revolver_swingout WMCARD.05_rifle WMCARD.06_breakaction WMCARD.07_smg WMCARD.08_cell WMCARD.09_chaingun WMCARD.10_launcher WMCARD.11_bfg WMCARD.12_chainsaw WMCARD.13_flamethrower WMCARD.14_magazine_shotgun WMCARD.grenade bd22/WMCARD.bd22 RS_Modern/WMCARD.breach RS_Modern/WMCARD.breach_set
git commit -m "Grip points for 72 guns fitted to c_doom_marine's hand: palm, rake, supportat"
git push origin main
```

**`E:\DOOMWork` root repo** (no remote is configured, so it can only be committed):

```
cd E:\DOOMWork
git add tools/avatar_grip HANDOFF_2026-10-11_grips_and_quest_packs.md _reports/avatar_grip_2026-10-10 RS_QuestHands/tools/posefix
git status   # check nothing else came along; .pk3 and _backups are ignored
git commit -m "Avatar grip tools, Quest hands/reload/ballistics pack sources, handoffs"
```

- `RS_QuestHands/tools/posefix` holds the sources for A and B. Some of it may be committed already; `git status` will show what's new.
- Do not commit the `out\` folder, any `.pk3` files, or `_backups\`.
- To push the root repo, it needs a remote first. That is the owner's call.

## 4. Open items

None of these block the above.

- **RS_Avatar:** nothing to change.
- **Gun angle in the hand (engine run):**
  - The new points fix *where* each gun sits in the hand. *Which way* it points is still each gun's recorded tilt.
  - The agreed plan is to work out every gun's angle from one `vr_gun_dump` run in a level, so the barrel points where the controller points.
  - `vr_gun_dump` is built but has never produced a verified dump (see `_reports\gun_seating_2026-10-02\LANE_STATE_2026-10-03.md` §4.1). Next step: build, run it in a level, then derive the angles from the dump.
- **Chainsaw rake (script, optional):**
  - Chainsaw rear handles measure 87°. The card parser only accepts −10..80, so 80 was written.
  - Widening the range in `RS_VR_Reload\zscript\wm\parser.zs` (`GripKey`, `rake`) to 90 would let the true value go in.
- **Hand height (engine question):**
  - `RS_AVATAR.md` §3 notes the engine may draw the hand 1.2× taller than the gun along world up (pixel stretch).
  - If the avatar's hands sit high on every gun, check that first.
- **BD22 load order in REMA:**
  - The BD22 setup also needs `RS_VR_Weapons.pk3`, because the player class lives there.
  - `bd22\BD22_STATE.md` also lists `RS_WorldHands`, `RS_VR_BD22_Players` and `RS_VR_BD22_Slots`. That list is from Sep 28; confirm it against the desktop `BD22.zdl`.
