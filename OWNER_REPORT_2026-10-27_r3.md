# Owner's headset report on BD22_VR-Reloaded_1.99x-lb-r3 (2026-10-27 05:03)

Worked in this repo (lane-b-1.99x). Owner's words are kept where the meaning matters.

## Works / liked
- Dual flick to reload: "quite nice".
- Voxels look good.
- The grenade throw is nice. Throwing in general is probably okay; the axe throw waits for the axe changes below.
- Punching is good, both forward and side to side.
- The two-handed butt strike works and he likes the knockback.
- Minigun: barrels, frame and hand shake when firing. "Whole thing looks damn good".
- He has been getting ammo with Use.

## Bugs
1. **Over-under machine gun:** the casings come out of the barrel, not the port.
2. **Ruger 14 / sniper:** the bullets leave from below the barrel, as if from the magazine.
3. **Minigun:** after firing, the frame stops shaking and the barrels keep spinning a little (correct), but the hand keeps shaking. The hand shake is tied to the barrel spin; it must follow the frame shake.
4. **Unmaker carve:** only the top half of the skull pops out. The RS VR Weapons version (the same mesh) has the whole skull come out.
5. **IDKFA gives neither the revolver nor the shotvolver.** So the shotvolver's slug-shot alt fire can't be verified yet.
6. **Butt strike range:** too short. Enemies back away as you close in, so extend the range. This is the two-handed rifle with a "punch" from the grip hand, i.e. a stock hit.

## Changes
7. **Chainsaw:** remove its swing animation. The player swings it physically. It damages whatever comes into range, not by velocity or momentum like the other melee weapons.
8. **Axe lock-on:** it locks onto one enemy, using the same indicator icon as the Shieldsaw and the saber.
9. **Axe blade orientation:** hits count only when the blade edge leads the motion, judged from the controller's rotation. In the normal ready pose (pointing like a gun) the blade faces out, so a swing down cuts and an arm raised is the flat of the head, not an attack. Side to side counts only when the controller is rotated so the edge faces the way it moves.
10. **Two-handed sword:**
    - stop the weapon snapping to the off hand;
    - the off-hand mesh snaps to the handle below the main hand, and the main hand still drives the attack;
    - possibly more damage in this mode.
11. **Rename the option "Slugrevolver replaces Shotvolver"** to "Shotvolver Swap for Revolver", On/Off.
12. **Revolver and shotvolver:**
    - they should be different meshes;
    - the owner has a measured, reloadable candidate mesh for the normal revolver (ASK HIM FOR IT).
13. **Reloads for guns that have no idea of a magazine** (weapon code changed to add ammo use and magazines):
    - Unmaker: 200;
    - Flamethrower: 100;
    - over-under machine gun: 100;
    - chaingun: 200.
14. **Options to dual-wield every gun,** most of them off by default.
15. **Ruger scope:** today it is a fake glass texture, and the dot doesn't work. It needs one of:
    - a truly see-through red-dot sight, with no magnification and a red dot in it;
    - a real scope that renders a 3x zoom.

## Questions answered (in the reply)
- **"Gun bash"** is a BUTTON: BD22's kick button with a gun in hand does a gun hit instead of the boot. The swing-down gesture with a pistol is the **pistol whip**, a different move. The naming is confusing; consider a rename.

## Added by the owner (2026-10-27 06:50)
16. **Pistol whip (the one-handed downstroke) only works with the OFF hand,** not the main hand. Fix it so the main hand's downstroke whips.
17. **The impact hit flash on EVERY melee hit:** punch, butt strike, pistol whip and gun bash all get the RS_CombatFX hit-flash graphic, with its colour assignable (the RSH0 tint options Original/Blue/Green/Amber/White already exist in TRNSLATE.rsq). Today only the gun bash has it (F4).

## For 2.0 (owner, 2026-10-27 08:15)
18. **A skin-tone slider for the FBX hands,** in both BD22 Weapons Q 2.0 and ModelSwapper 2.0.
    - **Feasible on QuestZDoom 17.3 with no engine change:** a slider of discrete steps. Each step is a pre-recoloured copy of the hand texture, swapped by the option (MODELDEF skin / A_ChangeModel). Gloves could be one of the steps.
    - **To be checked:** whether a smooth slider is possible through a GLDEFS material shader on 17.3. Prove it on the rig before promising it.

## For 2.0 (owner, 2026-10-27 11:21)
19. **Option "Player Ballistics: Hitscan / Bullet":** the player can choose to fire real bullets instead of hitscan.
    - **Source to build from:** the owner's RS_Ballistics (E:\DOOMWork\RS_Ballistics) already turns MONSTERS' hitscans into real flying rounds: `zscript/rsb/enemyfire.zs`, cvar `sv_rsb_enemy_rounds`, speed `sv_rsb_enemy_round_speed` = 80 map units a tic. Port that to the player's hitscans in BD22Q, with a WorldHitscanPreFired hook as recoil.zs already uses.
    - **Rules:**
      - it is a server cvar (it decides where shots go);
      - a round leaves from the drawn muzzle (RSQ_Muzzle);
      - same damage as BD22's hitscan;
      - the kill is credited to the player.

## Revolvers (owner, 2026-10-27 16:00)
20. "I don't need two revolvers and one shotvolver." Keep exactly two:
    - the **Revolver** (BrutalRevolver, the Moonlight);
    - the **Shotvolver** (BD22 `Revolver`).

    Drop `Revolver2` (BD21's slug revolver) and the "Shotvolver Swap for Revolver" option that swaps it in. The Shotvolver's slug alt fire, if any, stays on the Shotvolver.
