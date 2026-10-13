# posefix — how RS_BD22_Models_v8.pk3 was made

Stock QZD 17.3. **Load RS_BD22_Models_v8.pk3 after BD22** (brutal22test6.pk3): it carries
replacement copies of six BD22 weapon files at BD22's own paths (the br_vr way), so its
versions win.

    python restore_and_strip.py ..\..\..\RS_BD22_Models.pk3 ..\..\..\RS_BD22_Models_v8.pk3 ^
        ..\..\..\VR_WeaponSetRebuild\WeaponSets bd22_displayed.json ^
        ..\..\..\RS_VR_Weapons\bd22\brutal22test6.pk3
    python verify_pk3.py <old.pk3> <new.pk3> <bd22 lump list> <bd22 DECORATE Weapons dir> <WeaponSets dir>

| File | What it does |
|---|---|
| `pose_tables.py` | Authored poses for AssaultShotgun, Plasma_Gun, GrenadeLauncher, FlameCannon |
| `fill_tables.py` | Everything new in v4: BFG / RailGun level poses, hand families (fist, boot, grenade letter maps shared by BD22's colour copies), the 21 guns' missing frames (SIBLING / READY), and the eight new weapons (NEW) |
| `restore_and_strip.py` | Builds the pk3 from the old one. Meshes are stored zip-LZMA (QZD reads method 14) |
| `vrmelee/` | Shipped as is: `ZSCRIPT.rsvr`, `MAPINFO.rsvr` (registers `RSVR_MeleeHandler`), `zscript/rsvr/melee.zs` (real axe / Dragonslayer swings, axe throw), `zscript/rsvr/vrhand.zs` (the only file that reads QZD's VR fields: AttackPos, AttackDir, OverrideAttackPosDir, PlayInVR) |
| `weapon_patch.py` | The weapon-file replacements: every changed line of Axe, Dragonslayer, GrenadeLaunch, IncendiaryLauncher, SSG and Saw, checked against BD22's original line before it is changed. Only effect: the gun stays on screen where BD22 blanked it (reloads, unload, inspect, axe/chainsaw/Dragonslayer swings, kicks with the Dragonslayer and M202) |
| `md3strip.py` | Rewrites an MD3 keeping only chosen frames; everything else byte-identical |
| `decsim.py` | DECORATE explorer: every (sprite, frame) a weapon or flash layer can show |
| `bd22_displayed.json` | decsim's output for the 29 weapon classes + BD22's sprite art list |
| `verify_pk3.py` | Independent check: re-runs decsim and fails if any shown frame has no model; compares every FrameIndex line's vertices with the intended frame of the source mesh; placement, files, sprite names, class names |
| `pose_axis.py` | Prints each mesh frame's position and barrel pitch (how "level" was judged) |

Engine facts this relies on (checked in the QZD 17.3 source, tag qzd17.3):
- `models.cpp`: a MODELDEF sprite name is fatal only if the engine never saw
  it; DECORATE registers every sprite name its states use, art or not.
- `file_zip.cpp` / `files_decompress.cpp`: zip LZMA (method 14) is read.
  Every mesh in the pack was decoded byte-identical through a copy of
  `DecompressorLZMA` built on the engine's own `LzmaDec.c`.

The meshes inside the pk3 are stripped, so its FrameIndex numbers do not match
the full meshes in `RS_QuestHands\models\bd`. Running
`gen_bd22_modeldef.py --write` would regenerate the old MODELDEF and undo all of
this. `hands_blocks.py` is the v3 hand-block table, superseded by
`fill_tables.py`.

## VR melee (v7)

- Axe and Dragonslayer: swing the controller; the blade hits what it passes
  through. Each hit is BD22's own attack actor (AxeAttack / AxeAttackNoDecal,
  DSAttack / DSAttack2) started where and at the height the blade met the body,
  so BD22 decides the gore (its blood actors mark head / leg hits from the
  impact height; Saw / Cut deaths take heads, legs, arms, or halve the body).
  Blow = blade speed over 3.0 m/s (axe edge) / 3.5 m/s (sword point), measured
  relative to the player's own movement; harder swings add BD22's ripper hit.
  Each body is hit once per swing. Blade into a wall / floor at speed: BD22's
  axe impact (sparks, clang, decal, or the floor's splash). Hits and throws
  buzz the weapon hand (the engine's own fire rumble, via `RSVR_Buzz`).
- Axe alt-fire: hold, swing, let go: BD22's ThrowedAxe (ThrowedAxeStrong with
  berserk) leaves at the hand's speed (x3, 14-42 units/tic), with 8-degree aim
  help toward a visible monster, arced for the drop. Then BD22's own
  after-throw (fists via its FistSelect script); the axe lands as a pickup.
  Outside VR alt-fire is BD22's sideways swing (kept whole as `SideSwing`).
- Trigger: BD22's own chop, unchanged.
- The axe in the world (thrown, stuck in a wall, pickup) is BrutalAxe.md3 at
  true size (fill_tables.WORLD).
- Blade geometry: `handframe.py` / `bladeinfo.py` in posefix/melee place the
  held model relative to the controller with the engine's own HUD-model chain
  (models.cpp RenderHUDModel + hw_vrmodes GetWeaponTransform).

## v8: reloading, hands, ballistics (options: Options > RS VR Reload, Hands, Ballistics; also in BD22's menu)

| Option | cvar | Default |
|---|---|---|
| Reloading: Stock (BD22) / Immersive (VR) | `rsq_reload` | Stock |
| Shells / rounds per hand trip | `rsq_shells` | 2 |
| VR hands | `rsq_hands` | On |
| Ballistics: Stock (BD22) / Enhanced | `rsq_ballistics` (server) | Stock |
| Reload debug readout | `rsq_debug` | Off |

**Immersive reloading** (`weapon_patch.py` GATES + `zscript/rsq/reload.zs`).
BD22's own reload animations run unchanged. At 37 points in 13 guns the gun
pauses and asks whether the hand has done that step:
- FETCH: the off hand goes away from the gun, to get a magazine.
- INSERT: the hand comes back to the glowing marker at the magazine well,
  port or breech.
- RACK: the hand takes the slide, bolt or pump at the marker and pulls it 6 cm back.
- SHELL: shotgun and revolver, one shell per pass at the port. After
  `rsq_shells` shells the hand goes away for more.

Pressing reload during a pause does that step for you. With stock reloading,
or outside VR, every gate passes in 0 tics. The gate's first state shows exactly
what BD22's next state shows, so even the model's frame blending is unchanged.
A gate adds no states inside BD22's sequences (a `Goto` and a label take none),
so every relative jump still lands where it did. The gate states sit at the top
of `States`. The off hand buzzes on each step (`ALF_ISOFFHAND`).

**Hands**: Ermac's posed hands fitted onto every gun. See `hands/HAND_FITTING.md`
(the tools, the process, and how to redo it for another weapon set).
`rsq_hands_gen.py` builds the table, the MODELDEF blocks and the cut meshes.

**Enhanced ballistics** (`zscript/rsq/ballistics.zs`): hitscan and player
projectile impacts throw dust, sparks or splashes by surface (SURFACES.rsq;
untagged = concrete) and a few mesh chips (capped at 64). Damaging player
projectiles get a short particle trail (capped at 24). With it off, nothing runs.

**HK416 sniper fix**: `Scale -1.35 1.35 1.35`, `Offset 6.499 -3.835 10.913`.
v4-v7 had Scale y = -1.35, which (after the jDoom turn) reversed it and put it
69 cm behind the hand.

Tests: `hands/rtest/` (fake VR hands, scripted off hand, logger). Runs headless
on the local QZD build.

## Vanilla VR Plus add-on (RS_VanillaVRPlus_VR.pk3)

The same hands, reloading and ballistics, for the set in
`1.0b_Weapons_VanillaVRPlus_v1.2`. Load it after the set.

    python vplus/build_vplus.py <set folder> RS_VanillaVRPlus_VR.pk3

- `vplus/vplus_patch.py`: the reload pauses in the set's own `Decorate/rifle.txt`,
  `revolver.txt` and `shotty.txt`. The pack carries the patched copies at the same names,
  and the set's `decorate.txt` includes them. Each anchor line is checked to occur exactly
  once.
  - M16: magazine out, magazine in, charging handle.
  - Revolvers: away for rounds, back to the open cylinder.
  - Pump: a shell per pass, and the pump after every shot (BD22's shotgun does the same).
  - Super shotgun: away for shells, back to the breech.
- **It also fixes a crash in the set** (`FIX_SWITCH`). With "Weapon switching: Default",
  the Deselect of the M16 and the revolvers jumps into Select. A_Raise sees the pending
  weapon and lowers again in the same tic, until the stack runs out. Switching away from
  those guns crashes QuestZDoom 17.3. On the pump shotgun the same jump lands in Fire.
  The fix adds the slow lower / raise that Vanilla_Fist already has.
- `vplus/vfits.json`: the hands (`hands/HAND_FITTING.md` section 8). Gun ids 21-25 in
  `vrmelee/zscript/rsq/guns.zs`.
- Shared scripts: `rsq/guns.zs` (split out of `reload.zs`, both sets) and
  `rsvr/common.zs` (RSVR_Token / RSVR_Buzz, moved out of `melee.zs`). `reload.zs` looks
  up BD22's "Reloading" token by name, so the same file runs on both sets. BD22 still
  compiles with these.
- Tests: `vplus/rtest/` (fake VR hands, logger). They checked: stock and immersive
  reloads of all five guns, waits, skips by pressing reload, switching, hands layers,
  ballistics and the menu.

Do not load it together with RS_BD22_Models: they define the same classes.

