# Reload survey: BD22 (with RS_BD22_Models_v8) and Vanilla VR Plus 1.2

Machine-readable: `survey.json` (one record per gun). Scripts: `scripts/` (`survey.py build`). Images: `img/`.

**Frame:** centimetres in the VR weapon-controller frame: **F** forward, **L** left, **U** up, origin at the controller (QZD 17.3 HUD-model chain, same as `tool/hands/gunview.py`). Positions are for the gun in its READY pose: every reload frame is re-fitted onto the gun body, so offsets are relative to the gun as the hand holds it (the HUD animation's whole-gun tilt is listed separately as `body_pose`).

**Mesh frames:** BD22 = frame numbers of the stripped meshes in RS_BD22_Models_v8.pk3 (its MODELDEF FrameIndex), V+ = the set's own md3 frames.

**Representative images** (img/): BD22 Rifle [geometry](img/BD22_Rifle_geometry_side.png) / [storyboard](img/BD22_Rifle_storyboard.png); BD22 Pistol [geometry](img/BD22_BrutalPistol_geometry_side.png) / [storyboard](img/BD22_BrutalPistol_storyboard.png); BD22 Shotgun [geometry](img/BD22_Shot_Gun_geometry_side.png) / [storyboard](img/BD22_Shot_Gun_storyboard.png); V+ M16 [geometry](img/V+_VR_Rifle_geometry_side.png) / [storyboard](img/V+_VR_Rifle_storyboard.png); V+ revolver [closed](img/V+_VR_Revolver_geometry_side.png) / [open](img/V+_VR_Revolver_open_side.png) / [storyboard](img/V+_VR_Revolver_storyboard.png). Every other gun has the same set. Colours: magazine/cylinder/barrels orange, handle/slide/pump cyan, bolt green, shells/rounds yellow; yellow ring = controller origin; arrows = insert / pull / approach directions; red = hinge axis.

**Sound timing:** a sound listed "@X" starts when sprite X is shown (sounds in 0-tic states are attached to the next shown frame).

## Separable parts

- **Own md3/IQM surface(s):** BD22/Rifle magazine; BD22/Rifle charging_handle; BD22/Rifle bolt; BD22/BrutalPistol magazine; BD22/BrutalPistol slide; BD22/Shot_Gun pump; BD22/Shot_Gun bolt; BD22/Shot_Gun shell; V+/VR_Rifle magazine; V+/VR_Revolver barrel; V+/VR_Revolver rounds; V+/VR_Revolver speedloader; BD22/BrutalSMG magazine; BD22/BrutalSMG charging_handle; BD22/MP40 magazine; BD22/MP40 bolt_handle; BD22/AssaultShotgun magazine; BD22/AssaultShotgun charging_handle; BD22/Revolver cylinder; BD22/Revolver shells; BD22/SSG barrels; BD22/SSG shells; BD22/Rocket_Launcher drum; BD22/RailGun magazine; BD22/Plasma_Gun magazine; BD22/GrenadeLauncher barrel; BD22/GrenadeLauncher grenade; V+/VR_Revolver2 barrel; V+/VR_Revolver2 rounds; V+/VR_Revolver2 speedloader; V+/VR_Shotgun pump; V+/VR_Shotgun shell; V+/VR_SuperShotgun barrels; V+/VR_SuperShotgun new_shells
- **Vertex group only** (moves rigidly, shares a surface): V+/VR_Rifle bolt; V+/VR_Revolver cylinder; BD22/Sniper magazine_new; BD22/Sniper magazine; BD22/Sniper charging_handle; V+/VR_Revolver2 cylinder
- Not surveyed (no reload, or no model): BD22 no reload: Minigun, MG42, BIG_FUCKING_GUN, BFG10k, Unmaker, Devastator, NukeLauncher, IncendiaryLauncher (M202), HellishMissileLauncher, FlameCannon and Flamethrower2 (their Reload label only idles), Chain_saw, BrutalAxe, DSweap; BD22 dual weapons: DualRifles, DualPistols, DualSMG, DualMP40, DualPlasmaRifles, DualFlameCannon reload, but RS_BD22_Models_v8 has no models for them (dual labels excluded); V+ no reload: Vanilla_Fist / offhand fist, Vanilla_Chainsaw, Vanilla pistol, Vanilla_Chaingun, Vanilla_RocketLauncher, Vanilla_PlasmaRifle, Vanilla_BFG9000

## Summary

| Gun | Feed | Feed part (separate?) | Well / port | Insert dir, depth | Handle part (separate?) | Grab -> pull, travel | Mag-out / open frames |
|---|---|---|---|---|---|---|---|
| BD22/Rifle | magazine | magazine (yes) | (12, 0.4, 1) -> mouth (11.8, 0.4, -7.8) | (0.022, 0, 1), 8.8 cm | charging_handle (yes) | (-6.5, 1.3, 4.9) -> (-1, -0.001, -0), 7.3 cm | f9, f10, f11, f12, f13 |
| BD22/BrutalPistol | magazine | magazine (yes) | (-3, -0, -2.2) -> mouth (-5, -0, -14.8) | (0.153, 0.001, 0.988), 12.7 cm | slide (yes) | (-6.9, -0, -0.3) -> (-1, -0, -0), 4.7 cm | f9, f10 |
| BD22/Shot_Gun | tube | shell (yes) | port (19, 0, -2.8) | (1, 0, 0) | pump (yes) | (40.1, 0, -2.8) -> (-1, 0, -0.002), 6.4 cm | - |
| V+/VR_Rifle | magazine | magazine (yes) | (11.5, 0, -0.2) -> mouth (11.9, 0, -4.9) | (-0.09, -0, 0.996), 4.8 cm | bolt (vertex group) | (15, -3.4, 5) -> (-1, -0, -0.023), 7.7 cm | f14, f15, f16, f17, f18, f19, f20, f21(hidden) ... |
| V+/VR_Revolver | revolver_breaktop | barrel (yes) | hinge (9.4, -0, -1.7) axis (-0, -1, 0) | 63.4 deg open | - | - | open f19-f30 |
| BD22/BrutalSMG | magazine | magazine (yes) | (17.8, -0, -4.8) -> mouth (13.7, -0, -17.8) | (0.299, 0.001, 0.954), 13.6 cm | charging_handle (yes) | (22.4, 2.4, -2.7) -> (-0.96, 0.279, 0), 10.8 cm | f8, f9, f10 |
| BD22/MP40 | magazine | magazine (yes) | (31.4, -0, 1.8) -> mouth (31.4, -0, -4.4) | (0, -0.001, 1), 6.2 cm | bolt_handle (yes) | (22.7, 1.2, 3.2) -> (-1, 0, 0), 17.1 cm | f10, f11, f12, f13 |
| BD22/AssaultShotgun | magazine | magazine (yes) | (15.6, 0, -4.2) -> mouth (15.6, -0, -5.1) | (-0, 0.002, 1), 0.9 cm | charging_handle (yes) | (11.7, -0.7, -0.8) -> (-1, 0, 0), 10.2 cm | f14, f15, f16, f17, f18, f19 |
| BD22/Revolver | revolver_swingout | cylinder (yes) | hinge (-0, 0, -3.4) axis (1, 0, -0) | 90 deg open | - | - | open f23-f27 |
| BD22/SSG | break | barrels (yes) | hinge (10.7, 0, -2.5) axis (0, -1, -0) | 30.2 deg open | - | - | open f18-f32 |
| BD22/Rocket_Launcher | drum | drum (yes) | (-12.2, 2.2, 6.7) -> mouth (-12.2, -6.3, 10) | (-0, 0.932, -0.362), 9.1 cm | - | - | - |
| BD22/RailGun | cell | magazine (yes) | (22.1, 0, -3.5) -> mouth (22.1, 0, -8) | (0.001, -0, 1), 4.4 cm | - | - | f19, f15, f11, f12, f13, f14, f16, f17 ... |
| BD22/Plasma_Gun | cell | magazine (yes) | (12.6, 0, -10) -> mouth (13.2, -0.5, -13.5) | (-0.192, 0.132, 0.973), 3.6 cm | - | - | f15, f16, f17, f18 |
| BD22/GrenadeLauncher | break | barrel (yes) | hinge (18.3, 0, -3.7) axis (-0.001, 1, 0) | 30 deg open | - | - | open f9-f22 |
| BD22/Sniper | magazine | magazine (vertex group) | (11.6, 0.6, 3.2) -> mouth (11.9, 1.4, -2.1) | (-0.066, -0.149, 0.987), 5.3 cm | charging_handle (vertex group) | (-4.6, -0.3, 10.2) -> (-1, 0, -0), 7.6 cm | f92, f93, f94, f95, f96, f97, f98, f99 ... |
| V+/VR_Revolver2 | revolver_breaktop | barrel (yes) | hinge (9.4, -0, -1.7) axis (-0, -1, 0) | 63.4 deg open | - | - | open f19-f30 |
| V+/VR_Shotgun | tube | shell (yes) | port (12.5, -0.5, 3.3) | (0.892, 0.429, -0.14) | pump (yes) | (34.5, -0, 1.3) -> (-1, -0, 0.002), 10.2 cm | - |
| V+/VR_SuperShotgun | break | barrels (yes) | hinge (12.5, 0, 0.2) axis (0, -1, 0) | 58.5 deg open | - | - | open f9-f21 |

## Sounds

| Gun | Step | Sound (lump) where |
|---|---|---|
| BD22/Rifle | mag_out | Rifle/Reload1 @RIFR A (t0); magazine drops at RIFR G (mesh f9) |
| BD22/Rifle | mag_in | Rifle/Reload2 @RIFR O (t17), magazine 13 cm below seated, seats at RIFR R/S (f15) |
| BD22/Rifle | charge_back | Rifle/Bolt1 @2IFR I (empty reload only; handle -7.3 cm at 2IFR J) |
| BD22/Rifle | charge_release | Rifle/Bolt2 @2IFR K |
| BD22/BrutalPistol | mag_out | Pistol/Reload1 (lump MG_OUT, two clicks at 30/190 ms) @2ISR A / PISR A; magazine falls at f9 |
| BD22/BrutalPistol | mag_in | Pistol/Reload2 (PISR) @2ISR P / PISR P, the frame the magazine seats (f15) |
| BD22/BrutalPistol | slide_release | pistol/slide2 (PISSL) @2ISR T (empty reload only) |
| BD22/Shot_Gun | shell_insert | Shotgun/Reload ($random SHTLOAD1-4) @SHTN X, once per shell, as the shell reaches the loading port (f24 -> f25) |
| BD22/Shot_Gun | pump_back | Shotgun/Pump1 (SHGUPUM1) @SHTN H (Pump2 label, after loading an empty gun) |
| BD22/Shot_Gun | pump_forward | Shotgun/Pump2 (SHGUPUM2) @SHTN P |
| V+/VR_Rifle | mag_out | weapons/9mmclip1 @RIFL O (mesh f14, magazine 6 cm down and tilting out) |
| V+/VR_Rifle | mag_in | weapons/9mmclip2 in the 0-tic state after RIFK I, i.e. as RIFK J shows (mesh f34 -> f35, magazine 1.0 -> 0.5 cm from seated) |
| V+/VR_Rifle | charge | weapons/9mmslide in the 0-tic state after RIFK L, i.e. as RIFK M shows (bolt at -7.7 cm in f37, going home: -5.7 in f38) |
| V+/VR_Rifle | empty | AKEMPT @Reload when no reserve (then the reload still runs) |
| V+/VR_Revolver | cylinder_open | weapons/9mmclip1 @REVL Q (t0, mesh f16; action breaks open f18-f19) |
| V+/VR_Revolver | rounds_in | weapons/9mmclip2 @REVO A (mesh f26, loader on the open cylinder f25-f26) |
| V+/VR_Revolver | cylinder_close | weapons/9mmslide @REVO I (mesh f34, action closed at f33) |
| BD22/BrutalSMG | mag_out | SMG/Reload1 (SMGREL1) @SMGR I (mesh f8: magazine 17 cm out) |
| BD22/BrutalSMG | mag_in | SMG/Reload2 (SMGREL2) @SMGR X (mesh f14: seated); ammo moves here |
| BD22/BrutalSMG | charge | none: the cocking lever moves silently at SMGR Y-] (f16-f20); no BD22 sound for it |
| BD22/MP40 | charge_back | MP40/Bolt1 (BOLTBACK) @MP4R H (empty reload; bolt -8.6 -> -17.1 cm f8-f9, then locked 44 deg) |
| BD22/MP40 | dry_click | Weapon/Empty (DRYFIRE) @MP4R Q / 2P4R S |
| BD22/MP40 | mag_out | MP40/Reload1 (MP401) @MP4R W / 2P4R Z (mesh f10, magazine 12 cm down) |
| BD22/MP40 | mag_in | MP40/Reload2 (MP402) @2P4R I / 3P4R K (mesh f9); ammo moves here |
| BD22/MP40 | charge_release | MP40/Bolt2 (BOLTRELE) @MP4R J in FullReload (bolt runs home f9 -> f7) |
| BD22/AssaultShotgun | mag_out | ASG/Reload1 (USASOUT) @USAR J (mesh f14, magazine 7 cm down) |
| BD22/AssaultShotgun | mag_in | ASG/Reload2 (USASIN, two clicks 80/260 ms) @USAR X (mesh f19, 2.4 cm from seated) |
| BD22/AssaultShotgun | charge_back | asg/bolt1 (ASGBOLT1) @2SAR Q (handle already back since f14) |
| BD22/AssaultShotgun | charge_release | asg/bolt2 (ASGBOLT2) @2SAR O (handle runs home f28-f31) |
| BD22/Revolver | cylinder_open | Revolver/Open (revop) @REVR G (mesh f23, cylinder 45 deg out) |
| BD22/Revolver | shell_insert | Shotgun/Reload ($random SHTLOAD1-4) @REVR T, once per round (f26); SSGCaseSpawner per round at REVR Z |
| BD22/Revolver | cylinder_close | Revolver/Close (revlose) @REVR G on the way back (f23) |
| BD22/SSG | lever_open | SSG/Lever2 (SSGCLIP2) @SHTZ C (mesh f13, top lever turns) |
| BD22/SSG | open | weapons/sshoto @SHTZ L (mesh f22, barrels open; two SSGCaseSpawner) |
| BD22/SSG | shells_in | weapons/sshotl @SHTZ V (mesh f27, shells seated); ammo moves here |
| BD22/SSG | close | weapons/sshotc @SHZ2 A (mesh f30) |
| BD22/SSG | lever_close | SSG/Lever1 (SSGCLIP1) @SHZ2 J (mesh f41) |
| BD22/Rocket_Launcher | mag_out | rocket/reload1 (RLREL1, clicks at 30/360 ms) @MISR A (drum starts out, f16); RocketCaseSpawn @MISR F |
| BD22/Rocket_Launcher | mag_in | rocket/reload2 (RLREL2, clicks at 70/280 ms) @MISR U (mesh f25, drum 11 cm out on the right); ammo moves here |
| BD22/RailGun | mag_out | Railgun/Reload1 (RGREL1) @RAIR A (cell goes down f23-f11); PlasmaCaseSpawn @RAIR A |
| BD22/RailGun | mag_in | Railgun/Reload2 (RGREL2, 772 ms) @RAIR O (mesh f15, cell still 25 cm below; seats at RAIR X f24) |
| BD22/RailGun | charge | Plasma/Beep (BEP) @RAR2 G and Railgun/Recharge (RAILR1, 1.26 s) @RAR2 I: power-up after the cell is in, no handle |
| BD22/Plasma_Gun | mag_out | Plasma/Reload1 (PLSREL1, 1.5 s) @PRSR A (cell out at f15); PlasmaCaseSpawn @PRSR A |
| BD22/Plasma_Gun | mag_in | Plasma/Reload2 (PLSREL2, clicks 50/400 ms) @PRSR O (mesh f20, 0.9 cm from seated); ammo moves at PRSR P |
| BD22/GrenadeLauncher | open | GrenadeLauncher/Open (DSGROPEN) @GRLN J (mesh f11) |
| BD22/GrenadeLauncher | shell_insert | GrenadeLauncher/Load (DSGRLOAD) @GRLN U (mesh f17, round going into the barrel); ammo moves here |
| BD22/GrenadeLauncher | close | GrenadeLauncher/Close (DSGRCLOS) @GRLN [ (mesh f22) |
| BD22/Sniper | mag_out | Sniper/MagOut (X21MGOUT, clicks 70/190 ms) @X21R I (mesh f88) |
| BD22/Sniper | mag_in | Sniper/MagIn (X21MGIN, 1.4 s) @X21R U (mesh f101, new magazine 7 cm below seated; seated at f110) |
| BD22/Sniper | charge_back | Sniper/BoltBack (X21BACK) @X22R L (mesh f302, handle -7.6 cm; empty reload only) |
| BD22/Sniper | charge_release | Sniper/BoltForward (X21FORW) @X22R N (mesh f317) |
| V+/VR_Revolver2 | cylinder_open | weapons/9mmclip1 @REVL Q |
| V+/VR_Revolver2 | rounds_in | weapons/9mmclip2 @REVO A |
| V+/VR_Revolver2 | cylinder_close | weapons/9mmslide @REVO I |
| V+/VR_Shotgun | shell_insert | Shotgun/Reload @ReloadLoop after each SHTG R..J pass (a BD22 name: not in the set's SNDINFO, silent unless BD22 is loaded) |
| V+/VR_Shotgun | pump | shotpump (raw lump name; SNDINFO maps wpn/shotpump and guns/shotpump to lump shotpump) @SHTG J in Fire |
| V+/VR_SuperShotgun | open | weapons/sshoto (engine DSDBOPN) via A_OpenShotgun2 @SHT2 I |
| V+/VR_SuperShotgun | shells_in | weapons/sshotl (DSDBLOAD) via A_LoadShotgun2 @SHT2 S (mesh f18); ammo given just before |
| V+/VR_SuperShotgun | close | weapons/sshotc (DSDBCLS) via A_CloseShotgun2 @SHT2 X (mesh f23) |

## BD22/Rifle

- DECORATE: `brutal22test6.pk3:actors/Weapons/Rifle.dec`; model `RS_BD22_Models_v8.pk3:models/bd/Rifle/Rifle.md3` (29 frames), ready RIFG A = mesh f3, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 liikkuvat 268v/118t = charging_handle; #1 ejectport 79v/44t = bolt; #2 trigger 76v/47t; #3 Lipas 2046v/1736t = magazine; #4 Runko 4554v/4662t; #5 tähtäin 2781v/2349t

- **magazine** (own surface: Lipas#3 2046): well (12, 0.4, 1), mouth (11.8, 0.4, -7.8), insert dir (0.022, 0, 1), depth 8.8 cm; base (12.2, 0.4, -19.6); farthest out (-0.4, 5.6, -36.5) (f9, 36.9 cm)
- **charging_handle** (own surface: liikkuvat#0 268): grab (-6.5, 1.3, 4.9), pull (-1, -0.001, -0), travel 7.3 cm (max at f19)  
  _surface 'liikkuvat' (Finnish: moving parts) = AR-style T charging handle on top-rear of the receiver_
- **bolt** (own surface: ejectport#1 79): grab (0.6, 0.1, 2.8), pull (-1, -0, -0), travel 10.6 cm (max at f19)  
  _surface 'ejectport' = bolt carrier seen through the ejection port; moves with the handle_

- **Mag-out pose:** ready frame f3 with the magazine surface(s) #3 'Lipas' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f9 (RIFR G/RIFR H): magazine at (-0.4, 5.6, -36.5) from seated, body tilt 2.1 deg
- Mag-out frames (magazine out of the well): f9 RIFR G/RIFR H mag at (-0.4, 5.6, -36.5) body tilt 2.1 deg; f10 RIFR I/RIFR J mag at (-0.8, 11.1, -16.5) body tilt 4.4 deg; f11 RIFR K/RIFR L mag at (-0.7, 5.6, -17.2) body tilt 7.3 deg; f12 RIFR M mag at (-0.5, 0, -17.3) body tilt 10.5 deg; f13 RIFR N/RIFR O/RIFR P mag at (-0.3, 0, -13.1) body tilt 13.7 deg
- HUD animation tilts the whole gun up to 19.9 deg (f16); removed in all numbers above.
- Tactical reload (rounds left) skips the bolt: Reload -> FullReload

**Reload flow, empty** (Clip2=200, RifleAmmo=0; 59 tics, ends at Ready3):

- `reload`: RIFR A·f7 [**snd** Rifle/Reload1] RIFR B·f8 RIFR C·f8 RIFR D·f8 RIFR E·f8 RIFR F·f8 RIFR G·f9 RIFR G·f9 RIFR H*3·f9 [spawn EmptyClipSpawn] RIFR I·f10 RIFR J·f10 RIFR K·f11 RIFR L·f11 RIFR M·f12 RIFR N·f13 RIFR N·f13 RIFR O·f13 RIFR O·f13 [**snd** Rifle/Reload2] RIFR O·f13 RIFR N·f13 RIFR P·f13 RIFR Q·f14 RIFR R·f15
- `finishreloading`: RIFR S·f15 [ammo RifleAmmo+30, DoubleRifleAmmo+30, Clip2-30] RIFR T·f15 RIFR U·f16 RIFR U·f16 RIFR V·f16 RIFR V·f16 RIFR V·f16 RIFR W·f16 RIFR X·f16 RIFR Y·f17 RIFR Z·f18 RIFR [·f8 RIFR B·f8 2IFR A·f22 2IFR B·f22 2IFR C·f22 2IFR D·f22 2IFR E·f22 2IFR F·f22 2IFR G·f22 2IFR H*3·f22 2IFR I·f21 [**snd** Rifle/Bolt1] 2IFR J·f19 2IFR J·f19 2IFR J·f19 2IFR K·f20 [**snd** Rifle/Bolt2] 2IFR K·f20 2IFR L·f22 2IFR M·f22 2IFR N·f22 2IFR O·f22 2IFR P·f23

**Reload flow, partial** (Clip2=200, RifleAmmo=1; 40 tics, ends at Ready3):

- `reload`: RIFR A·f7 [**snd** Rifle/Reload1] RIFR B·f8 RIFR C·f8 RIFR D·f8 RIFR E·f8 RIFR F·f8 RIFR G·f9 RIFR G·f9 RIFR H*3·f9 [spawn EmptyClipSpawn] RIFR I·f10 RIFR J·f10 RIFR K·f11 RIFR L·f11 RIFR M·f12 RIFR N·f13 RIFR N·f13 RIFR O·f13 RIFR O·f13 [**snd** Rifle/Reload2] RIFR O·f13 RIFR N·f13 RIFR P·f13 RIFR Q·f14 RIFR R·f15
- `fullreload`: RIFR S·f15 [ammo RifleAmmo+30, DoubleRifleAmmo+30, Clip2-30] RIFR T·f15 RIFR U·f16 RIFR U·f16 RIFR V·f16 RIFR V·f16 RIFR V·f16 RIFR W·f16 RIFR X·f16 RIFR Y·f17 RIFR Z·f18 RIFR [·f8 RIFR B·f8 RIFR B·f8 RIFR A·f7

Sound lumps: Rifle/Reload1 = RIFLER1 504 ms; Rifle/Reload2 = RIFLER2 798 ms; Rifle/Bolt1 = bolt1 182 ms; Rifle/Bolt2 = bolt2 239 ms

![BD22_Rifle_geometry_side.png](img/BD22_Rifle_geometry_side.png)
![BD22_Rifle_storyboard.png](img/BD22_Rifle_storyboard.png)

## BD22/BrutalPistol

- DECORATE: `brutal22test6.pk3:actors/Weapons/Pistol.dec`; model `RS_BD22_Models_v8.pk3:models/bd/BrutalPistol/BrutalPistol.md3` (24 frames), ready PIST A = mesh f3, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Cube 158v/146t = hammer; #1 Cube 1659v/1581t = slide; #2 Cube 414v/444t = top_round; #3 Cube 352v/384t = magazine; #4 Cube 4111v/4581t; #5 Cube 134v/104t = trigger

- **magazine** (own surface: Cube#3 352): well (-3, -0, -2.2), mouth (-5, -0, -14.8), insert dir (0.153, 0.001, 0.988), depth 12.7 cm; base (-5.7, -0, -14); farthest out (-0, -0, -30.6) (f9, 30.6 cm)
- **slide** (own surface: Cube#1 1659): grab (-6.9, -0, -0.3), pull (-1, -0, -0), travel 4.7 cm (max at f10)  
  _slide; the authored reload shows it locked back (-4.7 cm) from the first frames and releases it after the magazine is seated_
- **top_round** (own surface: Cube#2 414): rest centre (-3.9, -0, -2.1)  
  _round(s) on top of the magazine: ride in with the magazine, then are carried forward/up into the chamber as the slide closes (f15-f22)_
- **hammer** (own surface: Cube#0 158): rest centre (-8.3, 0, -0.1)  
  _hammer, cocked (27 deg) in all reload frames_
- **trigger** (own surface: Cube#5 134): rest centre (0.2, -0, -5)

- **Mag-out pose:** ready frame f3 with the magazine surface(s) #3 'Cube' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f9 (PISR H/PISR I/PISR J): magazine at (-0, -0, -30.6) from seated, body tilt 1.3 deg
- Mag-out frames (magazine out of the well): f9 PISR H/PISR I/PISR J mag at (-0, -0, -30.6) body tilt 1.3 deg; f10 PISR K/2ISR K mag at (-2.5, 0, -13.4) body tilt 2.9 deg
- HUD animation tilts the whole gun up to 21.1 deg (f15); removed in all numbers above.
- Empty reload (2ISR) and tactical reload (PISR) show the same mesh frames: the slide is back from f8 to f15 and runs home f16-f20 in both

**Reload flow, empty** (Clip1=200, BDPistolAmmo=0; 36 tics, ends at Ready):

- `reload`: 2ISR A·f3 [**snd** Pistol/Reload1; spawn EmptyClip2Spawn] 2ISR B·f3 2ISR C·f3 2ISR D·f3 2ISR E·f8 2ISR F·f8 2ISR G·f8 2ISR G·f8 2ISR H·f9 2ISR I·f9 2ISR J·f9 2ISR K·f10 2ISR K·f10 2ISR L·f11 2ISR L·f11 2ISR L·f11 2ISR M·f12 2ISR N·f13 2ISR O·f14
- `finishreload`: 2ISR P·f15 [**snd** Pistol/Reload2; ammo BDPistolAmmo+15, BDDualPistolAmmo+15, Clip1-15] 2ISR Q·f15 2ISR R·f16 2ISR S·f16 2ISR S·f16 2ISR T·f17 [**snd** pistol/slide2] 2ISR U·f18 2ISR V·f19 PISR T·f19 PISR T·f19 PISR U·f20 PISR V·f21 PISR W·f22 PISR D·f3 PISR C·f3 PISR B·f3 PISR A·f3

**Reload flow, partial** (Clip1=200, BDPistolAmmo=1; 32 tics, ends at Ready):

- `reload2`: PISR A·f3 [**snd** Pistol/Reload1; spawn EmptyClip2Spawn] PISR B·f3 PISR C·f3 PISR D·f3 PISR E·f8 PISR F·f8 PISR G·f8 PISR G·f8 PISR H·f9 PISR I·f9 PISR J·f9 PISR K·f10 PISR K·f10 PISR L·f11 PISR L·f11 PISR L·f11 PISR M·f12 PISR N·f13 PISR O·f14
- `finishreload2`: PISR P·f15 [**snd** Pistol/Reload2; ammo BDPistolAmmo+15, BDDualPistolAmmo+15, Clip1-15] PISR Q·f15 PISR R·f16 PISR S·f17 PISR T·f19 PISR T·f19 PISR U·f20 PISR V·f21 PISR W·f22 PISR D·f3 PISR C·f3 PISR B·f3 PISR A·f3

Sound lumps: Pistol/Reload1 = MG_OUT 311 ms; Pistol/Reload2 = PISR 181 ms; pistol/slide2 = PISSL 335 ms

![BD22_BrutalPistol_geometry_side.png](img/BD22_BrutalPistol_geometry_side.png)
![BD22_BrutalPistol_storyboard.png](img/BD22_BrutalPistol_storyboard.png)

## BD22/Shot_Gun

- DECORATE: `brutal22test6.pk3:actors/Weapons/Shotgun.dec`; model `RS_BD22_Models_v8.pk3:models/bd/ShotGun/Shotgun.md3` (30 frames), ready SHTN A = mesh f4, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Cube 342v/126t; #1 Cylinder 152v/74t; #2 trigger 831v/288t = shell; #3 trigger 106v/58t; #4 pump 1220v/1446t = pump; #5 eject 304v/372t = bolt; #6 Runko 18929v/16484t

- **pump** (own surface: pump#4 1220): grab (40.1, 0, -2.8), pull (-1, 0, -0.002), travel 6.4 cm (max at f18)  
  _fore-end; grab_point = its centre_
- **bolt** (own surface: eject#5 304): grab (9.3, -1.5, 0), pull (-1, 0, -0), travel 6.4 cm (max at f18)  
  _bolt seen in the ejection port, moves with the pump_
- **shell** (own surface: trigger#2 831): port (19, 0, -2.8) (f25), approach dir (0.939, -0, 0.344), push (1, 0, 0), leading tip (23.2, 0, -2.8), size 5.8 x 2.2 cm  
  _surface 2 is named 'trigger' but is a 12 ga shell (831 verts): parked inside the receiver in the ready frame, brought from below-behind to the loading port in f22-f25, then back inside (f21). push_dir = into the magazine tube (+F)_

- HUD animation tilts the whole gun up to 18.1 deg (f21); removed in all numbers above.
- The same Pump1/Pump2 pair is used by the pump after every shot (Fire)

**Reload flow, empty** (AmmoShell=200, ShotgunAmmo=0; 109 tics, ends at Ready3):

- `reloadnormally`: SHTN A·f4 SHTN B·f10 SHTN C·f11 SHTN D·f12 SHTN E·f13 SHTN F·f14 SHTN S·f14 SHTN T·f21
- `insertshellanimation`: SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21
- `pump2`: SHTN S·f14 SHTN F·f14 SHTN G·f14 SHTN H·f15 [**snd** Shotgun/Pump1] SHTN I·f16 SHTN J·f16 SHTN K·f17 [spawn ShotCaseSpawn] SHTN L·f18 SHTN M·f18 SHTN N·f18 SHTN P·f19 [**snd** Shotgun/Pump2] SHTN Q·f20 SHTN F·f14 SHTN E·f13 SHTN D·f12 SHTN C·f11 SHTN B·f10
- `readytofireagain`: SHTA F·f9 SHTA G·f9 SHTA H·f9 SHTA I·f9

**Reload flow, partial** (AmmoShell=200, ShotgunAmmo=1; 99 tics, ends at Ready3):

- `reloadnormally`: SHTN A·f4 SHTN B·f10 SHTN C·f11 SHTN D·f12 SHTN E·f13 SHTN F·f14 SHTN S·f14 SHTN T·f21
- `insertshellanimation`: SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21 SHTN U·f21 [ammo ShotgunAmmo+1, AmmoShell-1] SHTN U·f21 SHTN U·f21 SHTN V·f22 SHTN W·f23 SHTN X·f24 [**snd** Shotgun/Reload] SHTN Y·f25 SHTN Z·f25 SHTN [·f21 SHTN ]·f21
- `finishedinsertingshells`: SHTN T·f21 SHTN S·f14 SHTN F·f14 SHTN E·f13 SHTN D·f12 SHTN C·f11 SHTN B·f10
- `readytofireagain`: SHTA F·f9 SHTA G·f9 SHTA H·f9 SHTA I·f9

Sound lumps: Shotgun/Reload = SHTLOAD1 219 ms, SHTLOAD2 326 ms, SHTLOAD3 315 ms, SHTLOAD4 221 ms; Shotgun/Pump1 = SHGUPUM1 225 ms; Shotgun/Pump2 = SHGUPUM2 235 ms

![BD22_Shot_Gun_geometry_side.png](img/BD22_Shot_Gun_geometry_side.png)
![BD22_Shot_Gun_storyboard.png](img/BD22_Shot_Gun_storyboard.png)

## V+/VR_Rifle

- DECORATE: `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/rifle.txt`; model `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/guns/m16.md3` (41 frames), ready RIFL A = mesh f0, scale (1.35, 1.35, 1.35) offset (0, 0, 0)
- Surfaces: #0 weapon.002 565v/710t = bolt; #1 weapon.003 23v/15t = casing; #2 weapon.004 35v/40t = trigger; #3 weapon.005 73v/78t = magazine

- **magazine** (own surface: weapon.005#3 73): well (11.5, 0, -0.2), mouth (11.9, 0, -4.9), insert dir (-0.09, -0, 0.996), depth 4.8 cm; base (11.9, 0, -15.9); farthest out (-3.8, 0, -32) (f27, 32.2 cm)  
  _weapon.005 = magazine (52 verts) + the two visible top rounds (13 + 8 verts)_
- **bolt** (vertex group: weapon.002#0 24/565): grab (15, -3.4, 5), pull (-1, -0, -0.023), travel 7.7 cm (max at f37)  
  _24-vertex piece of weapon.002 on the right side above the magazine well (bolt in the ejection port). It is what the authored charge moves (RIFK L-N, -7.7 cm); the M16 T charging handle itself is part of the body and does not move_
- **casing** (own surface: weapon.003#1 23): rest centre (10.2, -1.1, 3.8)  
  _weapon.003: ejected casing, collapsed (hidden) at rest_
- **trigger** (own surface: weapon.004#2 35): rest centre (1.1, 0, -2.3)

- **Mag-out pose:** authored frame, magazine already hidden: mesh f24 (RIFL Y), body tilt 3.4 deg
- Mag-out frames (magazine out of the well): f14 RIFL O mag at (0.7, -0, -6.3) body tilt 4.6 deg; f15 RIFL P mag at (1.5, -0, -7.3) body tilt 4.7 deg; f16 RIFL Q mag at (2.5, -0, -7.9) body tilt 4.7 deg; f17 RIFL R mag at (3.6, -0, -8.4) body tilt 4.7 deg; f18 RIFL S mag at (4.6, -0, -9.5) body tilt 4.5 deg; f19 RIFL T mag at (5.2, -0, -11.7) body tilt 4.3 deg; f20 RIFL U mag at (5.3, -0, -15.2) body tilt 4.1 deg; f21 RIFL V (mag hidden) body tilt 3.8 deg; f22 RIFL W (mag hidden) body tilt 3.6 deg; f23 RIFL X (mag hidden) body tilt 3.5 deg; f24 RIFL Y (mag hidden) body tilt 3.4 deg; f25 RIFL Z (mag hidden) body tilt 3.4 deg; f26 RIFK A (mag hidden) body tilt 3.4 deg; f27 RIFK B mag at (-3.8, 0, -32) body tilt 3.4 deg; f28 RIFK C mag at (-3.5, 0, -30.5) body tilt 3.4 deg; f29 RIFK D mag at (-2.8, -0, -26.6) body tilt 3.4 deg; f30 RIFK E mag at (-2, -0, -21) body tilt 3.4 deg; f31 RIFK F mag at (-1, -0, -14.6) body tilt 3.1 deg; f32 RIFK G mag at (-0.2, -0, -8.3) body tilt 2.5 deg
- HUD animation tilts the whole gun up to 4.7 deg (f15); removed in all numbers above.
- Lumps 9mmclip1/9mmclip2/9mmslide/AKEMPT are not in the uploaded set folder (SNDINFO names them, files absent)
- No separate charging-handle geometry: the T-handle under the carry handle is part of the main body component of weapon.002 (205 verts); the only part the authored charge moves is the 24-vertex bolt piece in the ejection port (right side). The carry handle/rear sight is its own 103-vertex component (F -3.2..2.2, U 5.1..10.6) and does not move
- The magazine is collapsed (hidden) in RIFL V - RIFK A (mesh f21-f26): the authored mag-out pose of the gun

**Reload flow, empty** (Clip=200, VR_RifleLoaded=0; 46 tics, ends at ready):

- `reloada`: RIFL L*2·f11 RIFL M*2·f12 RIFL N*2·f13 RIFL O·f14 [**snd** weapons/9mmclip1] RIFL P·f15 RIFL Q·f16 RIFL R·f17 RIFL S·f18 RIFL T·f19 RIFL U·f20 RIFL V·f21 RIFL W·f22 RIFL X·f23 RIFL Y·f24 RIFL Z·f25 RIFK A*2·f26 RIFK B*2·f27 RIFK C*2·f28 RIFK D*2·f29 RIFK E*2·f30 RIFK F*2·f31 RIFK G*2·f32 RIFK H*2·f33 RIFK I*2·f34 RIFK J·f35 [**snd** weapons/9mmclip2] RIFK K·f36 RIFK L·f37 RIFK M*2·f38 [**snd** weapons/9mmslide] RIFK N*2·f39 RIFK O*2·f40 RIFL A·f0
- `(end)`: - [ammo VR_RifleLoaded+20, Clip-20]

**Reload flow, partial** (Clip=200, VR_RifleLoaded=10; 46 tics, ends at ready):

- `reloada`: RIFL L*2·f11 RIFL M*2·f12 RIFL N*2·f13 RIFL O·f14 [**snd** weapons/9mmclip1] RIFL P·f15 RIFL Q·f16 RIFL R·f17 RIFL S·f18 RIFL T·f19 RIFL U·f20 RIFL V·f21 RIFL W·f22 RIFL X·f23 RIFL Y·f24 RIFL Z·f25 RIFK A*2·f26 RIFK B*2·f27 RIFK C*2·f28 RIFK D*2·f29 RIFK E*2·f30 RIFK F*2·f31 RIFK G*2·f32 RIFK H*2·f33 RIFK I*2·f34 RIFK J·f35 [**snd** weapons/9mmclip2] RIFK K·f36 RIFK L·f37 RIFK M*2·f38 [**snd** weapons/9mmslide] RIFK N*2·f39 RIFK O*2·f40 RIFL A·f0
- `(end)`: - [ammo VR_RifleLoaded+10, Clip-10]

Sound lumps: weapons/9mmclip1 = 9mmclip1 (file not found); weapons/9mmclip2 = 9mmclip2 (file not found); weapons/9mmslide = 9mmslide (file not found)

![V+_VR_Rifle_geometry_side.png](img/V+_VR_Rifle_geometry_side.png)
![V+_VR_Rifle_storyboard.png](img/V+_VR_Rifle_storyboard.png)

## V+/VR_Revolver

- DECORATE: `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/revolver.txt`; model `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/gats/rev.md3` (41 frames), ready REVL A = mesh f0, scale (1.35, 1.35, 1.35) offset (0, 0, 0)
- Surfaces: #0 python.004 298v/336t; #1 python.005 63v/60t = cylinder+ejector; #2 python.006 28v/34t; #3 python.007 105v/126t = barrel; #4 python.008 18v/16t = rounds; #5 python.009 18v/16t = rounds; #6 python.010 18v/16t = rounds; #7 python.011 18v/16t = rounds; #8 python.012 18v/16t = rounds; #9 python.013 18v/16t = rounds; #10 python.014 257v/252t = speedloader

- **barrel** (own surface: python.007#3 105): hinge axis (-0, -1, 0) through (9.4, -0, -1.7), 63.4 deg open (f25); closed centre (13.9, -0, 2.4), open centre (15.1, -0, -3.9)  
  _python.007: barrel + top strap of a TOP-BREAK revolver; tips down about the hinge at the front-bottom of the frame (f19-f31), closes f31-f33_
- **cylinder** (vertex group: python.005#1 50/63): hinge axis (-0, -1, 0) through (9.2, -0, -1.7), 63.4 deg open (f25); closed centre (6, -0, 1.5), open centre (10.7, -0, 2.6); chambers face (2.8, 0, 1.6) closed -> (9.2, -0, 5.5) open, bore axis open (0.448, -0, -0.894)  
  _python.005 without its rear disc: the cylinder (axis at L 0, U 1.55 when closed), tips with the barrel; rear_face_open = where the chambers face when open_
- **ejector** (vertex group: python.005#1 13/63): rest centre (2.8, 0, 1.5)  
  _13-vertex rear disc of python.005 (ejector star): pushed out of the cylinder when the action opens_
- **rounds** (own surface: python.008#4 18, python.009#5 18, python.010#6 18, python.011#7 18, python.012#8 18, python.013#9 18): port (9.4, 0.9, 6.9) (f23), approach dir (0.514, 0.247, -0.821), size 13 x 10.1 cm; hidden (collapsed) in the ready frame  
  _python.008-.013: six cartridges, collapsed (hidden) when closed; shown f20-f29 as the empties the ejector lifts (f20-f23 at the cylinder) and throws away (f24-f29)_
- **speedloader** (own surface: python.014#10 257): port (9, -0.1, 5.7) (f25), approach dir (0.482, -0, -0.876), size 10.3 x 5.3 cm; hidden (collapsed) in the ready frame  
  _python.014 (257 verts): new rounds in a loader, parked 1 m away (collapsed) when not used; comes down onto the open cylinder f21-f26, leaves and drops away f30-f37_

- HUD animation tilts the whole gun up to 31.9 deg (f23); removed in all numbers above.
- Lumps not in the uploaded set folder

**Reload flow, empty** (Clip=200, VR_RevLoaded=0; 40 tics, ends at ready):

- `reloada`: REVL Q*2·f16 [**snd** weapons/9mmclip1] REVL R*2·f17 REVL S*2·f18 REVL T*2·f19 REVL U*2·f20 REVL V*2·f21 REVL W*2·f22 REVL X*2·f23 REVL Y*2·f24 REVL Z*2·f25 REVO A·f26 [**snd** weapons/9mmclip2] REVO B*2·f27 REVO C*2·f28 REVO D*2·f29 REVO E*2·f30 REVO F*2·f31 REVO G*2·f32 REVO H*2·f33 REVO I·f34 [**snd** weapons/9mmslide] REVO J·f35 REVO K·f36 REVO L·f37 REVL A·f0
- `(end)`: - [ammo VR_RevLoaded+6, Clip-6]

**Reload flow, partial** (Clip=200, VR_RevLoaded=3; 40 tics, ends at ready):

- `reloada`: REVL Q*2·f16 [**snd** weapons/9mmclip1] REVL R*2·f17 REVL S*2·f18 REVL T*2·f19 REVL U*2·f20 REVL V*2·f21 REVL W*2·f22 REVL X*2·f23 REVL Y*2·f24 REVL Z*2·f25 REVO A·f26 [**snd** weapons/9mmclip2] REVO B*2·f27 REVO C*2·f28 REVO D*2·f29 REVO E*2·f30 REVO F*2·f31 REVO G*2·f32 REVO H*2·f33 REVO I·f34 [**snd** weapons/9mmslide] REVO J·f35 REVO K·f36 REVO L·f37 REVL A·f0
- `(end)`: - [ammo VR_RevLoaded+3, Clip-3]

Sound lumps: weapons/9mmclip1 = 9mmclip1 (file not found); weapons/9mmclip2 = 9mmclip2 (file not found); weapons/9mmslide = 9mmslide (file not found)

![V+_VR_Revolver_geometry_side.png](img/V+_VR_Revolver_geometry_side.png)
![V+_VR_Revolver_open_side.png](img/V+_VR_Revolver_open_side.png)
![V+_VR_Revolver_open_front.png](img/V+_VR_Revolver_open_front.png)
![V+_VR_Revolver_storyboard.png](img/V+_VR_Revolver_storyboard.png)

## BD22/BrutalSMG

- DECORATE: `brutal22test6.pk3:actors/Weapons/SubMachinegun.dec`; model `RS_BD22_Models_v8.pk3:models/bd/BrutalSMG/BrutalSMG.md3` (21 frames), ready SMGS A = mesh f3, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Sights 239v/182t = charging_handle; #1 Sights 17897v/15078t; #2 Trigger 222v/196t; #3 Lipas 2714v/2520t = magazine

- **magazine** (own surface: Lipas#3 2714): well (17.8, -0, -4.8), mouth (13.7, -0, -17.8), insert dir (0.299, 0.001, 0.954), depth 13.6 cm; base (10.3, 0, -28.3); farthest out (-5.1, 0, -16.3) (f8, 17.1 cm)
- **charging_handle** (own surface: Sights#0 239): grab (22.4, 2.4, -2.7), pull (-0.96, 0.279, 0), travel 10.8 cm (max at f19)  
  _surface 0 is named 'Sights' but is the MP5-style cocking lever on the left of the cocking tube: flips out up to 90 deg and goes back 10.4 cm (f16-f20), after the magazine is in_

- **Mag-out pose:** ready frame f3 with the magazine surface(s) #3 'Lipas' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f8 (SMGR O/SMGR P/SMGR Q): magazine at (-5.1, 0, -16.3) from seated, body tilt 0.4 deg
- Mag-out frames (magazine out of the well): f8 SMGR O/SMGR P/SMGR Q mag at (-5.1, 0, -16.3) body tilt 0.4 deg; f9 SMGR R mag at (-4.8, -0, -15.4) body tilt 1.5 deg; f10 SMGR S mag at (-4.3, -0, -13.6) body tilt 3.1 deg
- HUD animation tilts the whole gun up to 21.3 deg (f15); removed in all numbers above.
- Empty and tactical reloads are the same sequence (no rechamber branch)

**Reload flow, empty** (Clip1=200, BDSMGAmmo=0; 42 tics, ends at Ready):

- `reload`: SMGR B·f7 SMGR C·f7 SMGR D·f7 SMGR E·f7 SMGR F·f7 SMGR G·f7 SMGR G·f7 SMGR H·f7 SMGR H·f7 SMGR H·f7 SMGR I·f8 [**snd** SMG/Reload1] SMGR J·f8 SMGR K·f8 SMGR L·f8 SMGR M·f8 SMGR N·f8 SMGR O·f8 SMGR O·f8 [spawn EmptyClip2Spawn]
- `continuereload`: SMGR P·f8 SMGR P·f8 SMGR P·f8 SMGR Q·f8 SMGR R·f9 SMGR S·f10 SMGR T·f11 SMGR U·f12 SMGR U·f12 SMGR U·f12 SMGR U·f12 SMGR V·f13
- `finishreload`: SMGR X·f14 [**snd** SMG/Reload2; ammo BDSMGAmmo+40, BDDualSMGAmmo+40, Clip1-40] SMGR W·f15 SMGR X·f14 SMGR Y·f16 SMGR Z·f17 SMGR Z·f17 SMGR [·f18 SMGR \·f19 SMGR ]·f20 SMGR D·f7 SMGR C·f7 SMGR B·f7

**Reload flow, partial** (Clip1=200, BDSMGAmmo=1; 42 tics, ends at Ready):

- `reload`: SMGR B·f7 SMGR C·f7 SMGR D·f7 SMGR E·f7 SMGR F·f7 SMGR G·f7 SMGR G·f7 SMGR H·f7 SMGR H·f7 SMGR H·f7 SMGR I·f8 [**snd** SMG/Reload1] SMGR J·f8 SMGR K·f8 SMGR L·f8 SMGR M·f8 SMGR N·f8 SMGR O·f8 SMGR O·f8 [spawn EmptyClip2Spawn]
- `continuereload`: SMGR P·f8 SMGR P·f8 SMGR P·f8 SMGR Q·f8 SMGR R·f9 SMGR S·f10 SMGR T·f11 SMGR U·f12 SMGR U·f12 SMGR U·f12 SMGR U·f12 SMGR V·f13
- `finishreload`: SMGR X·f14 [**snd** SMG/Reload2; ammo BDSMGAmmo+40, BDDualSMGAmmo+40, Clip1-40] SMGR W·f15 SMGR X·f14 SMGR Y·f16 SMGR Z·f17 SMGR Z·f17 SMGR [·f18 SMGR \·f19 SMGR ]·f20 SMGR D·f7 SMGR C·f7 SMGR B·f7

Sound lumps: SMG/Reload1 = SMGREL1 524 ms; SMG/Reload2 = SMGREL2 429 ms

![BD22_BrutalSMG_geometry_side.png](img/BD22_BrutalSMG_geometry_side.png)
![BD22_BrutalSMG_storyboard.png](img/BD22_BrutalSMG_storyboard.png)

## BD22/MP40

- DECORATE: `brutal22test6.pk3:actors/Weapons/Mp40.dec`; model `RS_BD22_Models_v8.pk3:models/bd/MP40/MP40.md3` (14 frames), ready MP40 A = mesh f2, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 zamek_low_Cube 259v/272t = bolt_handle; #1 korpus_low_Cube 3098v/3547t; #2 srodek1_low_Cube 66v/80t; #3 kolba1_low_Cube 242v/264t; #4 lock_low_Cube 36v/44t; #5 pokretlo_low_Cube 101v/130t; #6 szczerbinka_low_Cube 48v/44t; #7 srodek_low_Cube 289v/352t; #8 kolba_low_Cube 303v/392t; #9 spust_low_Cube 73v/92t; #10 magazynek_low_Cube 364v/442t = magazine

- **magazine** (own surface: magazynek_low_Cube#10 364): well (31.4, -0, 1.8), mouth (31.4, -0, -4.4), insert dir (0, -0.001, 1), depth 6.2 cm; base (31.4, -0, -22.3); farthest out (-0, 0, -25.5) (f13, 25.5 cm)
- **bolt_handle** (own surface: zamek_low_Cube#0 259): grab (22.7, 1.2, 3.2), pull (-1, 0, 0), travel 17.1 cm (max at f9)  
  _'zamek' (bolt) with its handle on the left: back 17.1 cm (f8-f9), then turned 44 deg into the safety notch (f10-f13); released forward at the end of the empty reload_

- **Mag-out pose:** ready frame f2 with the magazine surface(s) #10 'magazynek_low_Cube' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f13 (3P4R E/MP4R Z/MP4R [): magazine at (-0, 0, -25.5) from seated, body tilt 18.3 deg
- Mag-out frames (magazine out of the well): f10 3P4R I/MP4R W/2P4R G mag at (-0, 0, -11.8) body tilt 18.3 deg; f11 3P4R H/MP4R X/2P4R F mag at (-0, 0, -18.3) body tilt 18.3 deg; f12 3P4R F/3P4R G/MP4R Y mag at (-0, 0, -23.4) body tilt 18.3 deg; f13 3P4R E/MP4R Z/MP4R [ mag at (-0, 0, -25.5) body tilt 18.3 deg
- HUD animation tilts the whole gun up to 18.3 deg (f9); removed in all numbers above.
- Empty reload: bolt back FIRST, then magazine; tactical: magazine only
- v8 maps the BD22 frames onto 7 BD21 poses (f7-f13), so the "seated" frames of FullReload still show the magazine 5.7 cm low (f9) until MP4R H/A

**Reload flow, empty** (Mauser9mm=200, MP40Ammo=0; 97 tics, ends at Ready3):

- `reload`: MP40 A·f2 MP4R A·f7 MP4R B·f7 MP4R C·f7 MP4R D·f7 MP4R E·f7 MP4R F·f7 MP4R F·f7 MP4R G·f7 MP4R G·f7 MP4R G·f7 MP4R H·f8 [**snd** MP40/Bolt1] MP4R I·f9 MP4R I·f9 MP4R J·f9 MP4R K·f9 MP4R K·f9 MP4R K·f9 MP4R K·f9 MP4R L·f9 MP4R L·f9 MP4R M·f9 MP4R N·f9 MP4R O·f9 MP4R O·f9 MP4R P·f9 MP4R Q·f9 MP4R Q·f9 [**snd** Weapon/Empty] MP4R Q·f9 MP4R R·f9 MP4R S·f9 MP4R T·f9 MP4R U·f9 MP4R U·f9 MP4R V·f9 MP4R V·f9 MP4R V·f9 MP4R W·f10 [**snd** MP40/Reload1] MP4R W·f10 MP4R X·f11 MP4R Y·f12 MP4R Z·f13 MP4R [·f13 [spawn EmptyClip2Spawn] MP4R \·f13 MP4R ]·f13 2P4R A·f13 2P4R B·f13
- `reloadafterunload2`: 2P4R C·f13 2P4R C·f13 2P4R C·f13 2P4R C·f13 2P4R C·f13 2P4R C·f13 2P4R D·f13 2P4R E·f12 2P4R F·f11 2P4R G·f10 2P4R H·f9 2P4R H·f9 2P4R H·f9
- `fullreload`: 2P4R I·f9 [**snd** MP40/Reload2; ammo MP40Ammo+32, DualMP40Ammo+32] 2P4R J·f9 2P4R K·f9 2P4R L·f9 MP4R V·f9 MP4R V·f9 MP4R V·f9 MP4R V·f9 MP4R V·f9 MP4R V·f9 MP4R U·f9 2P4R N·f9 MP4R P·f9 MP4R O·f9 MP4R O·f9 MP4R N·f9 MP4R M·f9 MP4R L·f9 MP4R L·f9 MP4R K·f9 MP4R K·f9 MP4R K·f9 MP4R K·f9 MP4R J·f9 [**snd** MP40/Bolt2] MP4R I·f9 MP4R I·f9 MP4R H·f8 MP4R G·f7 MP4R G·f7 MP4R G·f7 MP4R F·f7 MP4R F·f7 MP4R E·f7 MP4R D·f7 MP4R C·f7 MP4R B·f7 MP4R A·f7

**Reload flow, partial** (Mauser9mm=200, MP40Ammo=1; 60 tics, ends at Ready3):

- `reload`: MP40 A·f2
- `reloadnotempty`: MP4R A·f7 MP4R B·f7 2P4R O·f8 2P4R P·f8 2P4R Q·f9 2P4R R·f9 2P4R R·f9 2P4R S·f9 [**snd** Weapon/Empty] 2P4R S·f9 2P4R S·f9 2P4R T·f9 2P4R U·f9 2P4R V·f9 2P4R W·f9 2P4R X·f9 2P4R X·f9 2P4R X·f9 2P4R Y·f9 2P4R Z·f10 [**snd** MP40/Reload1] 2P4R [·f11 2P4R \·f12 2P4R ]·f13 3P4R A·f13 [spawn EmptyClip2Spawn] 3P4R B·f13 3P4R C·f13 3P4R D·f13 3P4R E·f13 3P4R E·f13 3P4R E·f13 3P4R E·f13 3P4R E·f13 3P4R E·f13 3P4R E·f13 3P4R F·f12 3P4R G·f12 3P4R H·f11 3P4R I·f10 3P4R I·f10 3P4R J·f9 3P4R J·f9 3P4R J·f9
- `continuereloading`: 3P4R K·f9 [**snd** MP40/Reload2; ammo MP40Ammo+31, DualMP40Ammo+31] 3P4R L·f9 3P4R M·f9 3P4R N·f9 3P4R N·f9 3P4R O·f9 3P4R O·f9 3P4R O·f9 3P4R O·f9 3P4R P·f9 2P4R U·f9 2P4R T·f9 2P4R R·f9 2P4R Q·f9 2P4R P·f8 2P4R O·f8 MP4R B·f7 MP4R A·f7

Sound lumps: MP40/Bolt1 = BOLTBACK 207 ms; Weapon/Empty = DRYFIRE 139 ms; MP40/Reload1 = MP401 390 ms; MP40/Reload2 = MP402 412 ms; MP40/Bolt2 = BOLTRELE 444 ms

![BD22_MP40_geometry_side.png](img/BD22_MP40_geometry_side.png)
![BD22_MP40_storyboard.png](img/BD22_MP40_storyboard.png)

## BD22/AssaultShotgun

- DECORATE: `brutal22test6.pk3:actors/Weapons/AssaultShotgun.dec`; model `RS_BD22_Models_v8.pk3:models/bd/AssaultShotgun/AssaultShotgun.md3` (32 frames), ready USAS A = mesh f4, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Sights 665v/566t; #1 Trigger 847v/288t = top_shell; #2 Receiver 38v/28t = charging_handle; #3 Frame 2776v/1826t; #4 Sights 436v/314t; #5 Trigger 44v/34t; #6 Mag 196v/168t = magazine

- **magazine** (own surface: Mag#6 196): well (15.6, 0, -4.2), mouth (15.6, -0, -5.1), insert dir (-0, 0.002, 1), depth 0.9 cm; base (15.6, 0, -16); farthest out (-0, 0, -28.6) (f16, 28.6 cm)
- **charging_handle** (own surface: Receiver#2 38): grab (11.7, -0.7, -0.8), pull (-1, 0, 0), travel 10.2 cm (max at f14)  
  _surface 'Receiver' (38 verts) = charging handle on the top-left; back 10.2 cm from f14 to f27, home f28-f31_
- **top_shell** (own surface: Trigger#1 847): rest centre (14.6, -0.1, -1.1)  
  _surface 1 is named 'Trigger' (847 verts) but is the shell on top of the magazine / in the feed: rides with the magazine, chambered f29-f31_

- **Mag-out pose:** ready frame f4 with the magazine surface(s) #6 'Mag' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f16 (USAR N/USAR P/USAR Q): magazine at (-0, 0, -28.6) from seated, body tilt 0 deg
- Mag-out frames (magazine out of the well): f14 USAR H/USAR I/USAR J mag at (0, 0, -6.9) body tilt 0 deg; f15 USAR L/USAR M mag at (-0, 0, -21.7) body tilt 0 deg; f16 USAR N/USAR P/USAR Q mag at (-0, 0, -28.6) body tilt 0 deg; f17 USAR T/USAR U mag at (-0, -0, -6.9) body tilt 7.5 deg; f18 USAR V/USAR W mag at (0, -0, -4.1) body tilt 15 deg; f19 USAR X mag at (0, -0, -2.4) body tilt 15 deg
- HUD animation tilts the whole gun up to 15.8 deg (f25); removed in all numbers above.
- Tactical reload plays raw lump USASPUL1 @2SAR [ (no SNDINFO entry and no such lump in brutal22test6.pk3)
- The authored charging handle goes back silently at USAR B-H (f12-f14) and stays back through the magazine change

**Reload flow, empty** (AmmoShell=200, AssaultShotgunAmmo=0; 87 tics, ends at Ready3):

- `reload`: USAR A·f11 USAR B·f12 USAR C·f12 USAR D·f13 USAR E·f13 USAR F·f13 USAR G·f13 USAR H·f14 USAR I·f14 USAR I·f14 USAR J·f14 USAR J·f14 USAR J·f14 [**snd** ASG/Reload1] USAR J·f14 USAR K·f14 USAR L·f15 USAR M·f15 USAR N·f16 USAR O·f16
- `continuereload`: USAR P·f16 [ammo HasUnloadedASG+1; spawn EmptyASGAmmoSpawn] USAR Q·f16 USAR R·f16 USAR R·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR T·f17 USAR U·f17 USAR V·f18 USAR W·f18 USAR X·f19 [**snd** ASG/Reload2] USAR X·f19 USAR Y·f20 USAR Y·f20 USAR Z·f21
- `cr3`: 2SAR A·f21 [ammo HasUnloadedASG-1, AssaultShotgunAmmo+20, AmmoShell-20] 2SAR A·f21 2SAR B·f22 2SAR C·f22 2SAR D·f23 2SAR D·f23 2SAR D·f23 2SAR D·f23 2SAR E·f24 2SAR F·f24 2SAR G·f24 2SAR H·f24 2SAR I·f24 2SAR J·f24 2SAR K·f25 2SAR L·f25 2SAR M*3·f28 2SAR Q·f26 [**snd** asg/bolt1] 2SAR S·f26 2SAR R·f26 2SAR Q·f26 2SAR Q·f26 2SAR P·f27 2SAR P·f27 2SAR P·f27 2SAR P·f27 2SAR P·f27 2SAR P·f27 2SAR O·f28 [**snd** asg/bolt2] 2SAR N·f29 2SAR N·f29 2SAR M·f28 2SAR M·f28 2SAR M·f28 2SAR M·f28 2SAR M·f28 2SAR T·f30 2SAR U·f30 2SAR V·f30 2SAR W·f31 2SAR X·f31 2SAR Y·f31 2SAR Z·f31 2SAR [·f31 2SAR \·f4

**Reload flow, partial** (AmmoShell=200, AssaultShotgunAmmo=1; 56 tics, ends at Ready3):

- `reload`: USAR A·f11 USAR B·f12 USAR C·f12 USAR D·f13 USAR E·f13 USAR F·f13 USAR G·f13 USAR H·f14 USAR I·f14 USAR I·f14 USAR J·f14 USAR J·f14 USAR J·f14 [**snd** ASG/Reload1] USAR J·f14 USAR K·f14 USAR L·f15 USAR M·f15 USAR N·f16 USAR O·f16
- `continuereload`: USAR P·f16 [ammo HasUnloadedASG+1; spawn EmptyASGAmmoSpawn] USAR Q·f16 USAR R·f16 USAR R·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR S·f16 USAR T·f17 USAR U·f17 USAR V·f18 USAR W·f18 USAR X·f19 [**snd** ASG/Reload2] USAR X·f19 USAR Y·f20 USAR Y·f20 USAR Z·f21
- `cr2`: 2SAR A·f21 [ammo HasUnloadedASG-1, AssaultShotgunAmmo+19, AmmoShell-19] 2SAR A·f21 2SAR B·f22 2SAR C·f22 2SAR D·f23 2SAR D·f23 2SAR D·f23 2SAR D·f23 2SAR E·f24 2SAR F·f24 2SAR G·f24 2SAR X·f31 2SAR Y·f31 2SAR Z·f31 2SAR [·f31 [**snd** USASPUL1] 2SAR \·f4

Sound lumps: ASG/Reload1 = USASOUT 685 ms; ASG/Reload2 = USASIN 554 ms; asg/bolt1 = ASGBOLT1 244 ms; asg/bolt2 = ASGBOLT2 500 ms; USASPUL1 = USASPUL1 (file not found)

![BD22_AssaultShotgun_geometry_side.png](img/BD22_AssaultShotgun_geometry_side.png)
![BD22_AssaultShotgun_storyboard.png](img/BD22_AssaultShotgun_storyboard.png)

## BD22/Revolver

- DECORATE: `brutal22test6.pk3:actors/Weapons/Revolver.dec`; model `RS_BD22_Models_v8.pk3:models/bd/Revolver/Revolver.md3` (31 frames), ready REVO A = mesh f0, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 frame_low 5169v/8391t; #1 frame_low 2141v/3478t = cylinder; #2 frame_low 420v/600t = cylinder; #3 frame_low 606v/980t; #4 frame_low 583v/886t = hammer; #5 shells 586v/1056t = shells; #6 shells 586v/1056t = shells; #7 shells 586v/1056t = shells; #8 shells 586v/1056t = shells; #9 shells 586v/1056t = shells

- **cylinder** (own surface: frame_low#1 2141, frame_low#2 420): hinge axis (1, 0, -0) through (-0, 0, -3.4), 90 deg open (f24); closed centre (9, 0.1, -0), open centre (9, 3.3, -3.4); chambers face (3.6, 0, 0) closed -> (3.6, 3.4, -3.4) open, bore axis open (1, 0, -0)  
  _surfaces 1+2: cylinder with crane and ejector rod; swings out to the LEFT (+L) 90 deg about an axis along the barrel_
- **shells** (own surface: shells#5 586, shells#6 586, shells#7 586, shells#8 586, shells#9 586): port (7, 3.6, -3.3) (f26), approach dir (1, 0.001, -0.001), size 11.1 x 5.2 cm  
  _five 'shells' surfaces (586 verts each) sit in the chambers and swing out with the cylinder; f27 shows them pushed 5 cm out of the rear (ejector), f26 back in. The per-shell insert loop alternates f26/f27_
- **hammer** (own surface: frame_low#4 583): rest centre (-0.7, -0, 0.5)  
  _hammer, rotated 39 deg in all reload frames_

- HUD animation tilts the whole gun up to 55 deg (f27); removed in all numbers above.
- One round per pass (ammo +1 at each REVR Z) until full

**Reload flow, empty** (AmmoShell=200, RevolverAmmo=0; 105 tics, ends at Ready):

- `reloadwithnoammoleft`: REVR A·f0 REVR B·f18 REVR C·f19 REVR D·f20 REVR E·f21 REVR F·f22 REVR F·f22 REVR G·f23 [**snd** Revolver/Open] REVR H·f24 REVR I·f24 REVR J·f25 REVR K·f25 REVR K·f25 REVR K·f25 REVR L·f26 REVR M·f26 REVR N·f26 REVR O·f26 REVR P·f26 REVR Q*2·f26
- `insertshellanimation`: REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26
- `finishedinsertingshells`: REVR Q·f26 REVR P·f26 REVR O·f26 REVR N·f26 REVR M·f26 REVR L·f26 REVR K·f25 REVR J·f25 REVR I·f24 REVR H·f24 REVR G·f23 [**snd** Revolver/Close] REVR F·f22 REVR E·f21 REVR E·f21 REVR D·f20 REVR C·f19 REVR B·f18 REVR A·f0

**Reload flow, partial** (AmmoShell=200, RevolverAmmo=1; 94 tics, ends at Ready):

- `reloadwithnoammoleft`: REVR A·f0 REVR B·f18 REVR C·f19 REVR D·f20 REVR E·f21 REVR F·f22 REVR F·f22 REVR G·f23 [**snd** Revolver/Open] REVR H·f24 REVR I·f24 REVR J·f25 REVR K·f25 REVR K·f25 REVR K·f25 REVR L·f26 REVR M·f26 REVR N·f26 REVR O·f26 REVR P·f26 REVR Q*2·f26
- `insertshellanimation`: REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26 REVR Z*2·f26 [ammo RevolverAmmo+1, AmmoShell-1; spawn SSGCaseSpawner] REVR R·f27 REVR S·f27 REVR T·f26 [**snd** Shotgun/Reload] REVR T·f26 REVR U·f26 REVR V·f26 REVR W·f26 REVR X·f26 REVR Y·f26
- `finishedinsertingshells`: REVR Q·f26 REVR P·f26 REVR O·f26 REVR N·f26 REVR M·f26 REVR L·f26 REVR K·f25 REVR J·f25 REVR I·f24 REVR H·f24 REVR G·f23 [**snd** Revolver/Close] REVR F·f22 REVR E·f21 REVR E·f21 REVR D·f20 REVR C·f19 REVR B·f18 REVR A·f0

Sound lumps: Revolver/Open = revop 325 ms; Shotgun/Reload = SHTLOAD1 219 ms, SHTLOAD2 326 ms, SHTLOAD3 315 ms, SHTLOAD4 221 ms; Revolver/Close = revlose 359 ms

![BD22_Revolver_geometry_side.png](img/BD22_Revolver_geometry_side.png)
![BD22_Revolver_open_side.png](img/BD22_Revolver_open_side.png)
![BD22_Revolver_open_front.png](img/BD22_Revolver_open_front.png)
![BD22_Revolver_storyboard.png](img/BD22_Revolver_storyboard.png)

## BD22/SSG

- DECORATE: `brutal22test6.pk3:actors/Weapons/SSG.dec`; model `RS_BD22_Models_v8.pk3:models/bd/SSG/SSG.md3` (46 frames), ready SHTZ A = mesh f1, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Cube 1785v/2557t = barrels; #1 Runko 12019v/22544t; #2 Trigger 848v/288t = shells; #3 Trigger 848v/288t = shells; #4 Open 960v/1820t = lever; #5 Trigger 416v/720t; #6 Runko 1075v/1980t

- **barrels** (own surface: Cube#0 1785): hinge axis (0, -1, -0) through (10.7, 0, -2.5), 30.2 deg open (f22); closed centre (21.6, 0, 0.4), open centre (21.5, 0, -5.5)  
  _surface 0 'Cube' = both barrels; break open 30 deg down_
- **shells** (own surface: Trigger#2 848, Trigger#3 848): port (10.9, 0.1, 1.6) (f27), approach dir (0.865, 0, -0.502), size 5.8 x 2.2 cm  
  _surfaces 2+3 (named 'Trigger', 848 verts each) = the two shells: come from behind/above into the open chambers f22-f27_
- **lever** (own surface: Open#4 960): rest centre (4.4, 0, 1.9)  
  _surface 'Open' = top lever, turned 20 deg while open_

- HUD animation tilts the whole gun up to 50 deg (f32); removed in all numbers above.
- weapons/sshoto / sshotl / sshotc are not in BD22's SNDINFO: they are the engine's Doom 2 sounds (DSDBOPN, DSDBLOAD, DSDBCLS)
- BD22 shows TNT1 for 4 tics between SHTZ Y and SHTZ Z (the v8 pack keeps the gun on screen there)

**Reload flow, empty** (AmmoShell=200, SSGAmmo=0; 49 tics, ends at Ready):

- `reload`: SHTZ A·f1 SHTZ A·f1 SHTZ B·f12 SHTZ C·f13 [**snd** SSG/Lever2] SHTZ D·f14 SHTZ E·f16 SHTZ F·f18 SHTZ G·f20 SHTZ H·f21 SHTZ I·f21 SHTZ I·f21 SHTZ I·f21 SHTZ H·f21 SHTZ J·f21 SHTZ K·f21
- `raisereloading`: SHTZ L·f22 [**snd** weapons/sshoto; spawn SSGCaseSpawner, SSGCaseSpawner] SHTZ M·f22 SHTZ [·f22 SHTZ N·f22 SHTZ O·f22 SHTZ P·f22 SHTZ Q·f23 SHTZ S·f24 SHTZ T·f25 SHTZ T·f25 SHTZ U·f26 SHTZ V·f27 [**snd** weapons/sshotl; ammo SSGLoaded+1, SSGAmmo+2, AmmoShell-2] SHTZ W·f27 SHTZ X·f27 SHTZ Y·f28 TNT1 A*4 SHTZ Z·f29 SHZ2 A·f30 [**snd** weapons/sshotc] SHZ2 B·f31 SHZ2 C·f32 SHZ2 D·f38 SHZ2 E·f38 SHZ2 F·f38 SHZ2 F·f38 SHZ2 G·f39 SHZ2 H·f39 SHZ2 I·f40 SHZ2 J·f41 [**snd** SSG/Lever1] SHTZ B·f12 SHTZ A·f1 SHTZ A·f1

**Reload flow, partial** (AmmoShell=200, SSGAmmo=1; 49 tics, ends at Ready):

- `reload`: SHTZ A·f1 SHTZ A·f1 SHTZ B·f12 SHTZ C·f13 [**snd** SSG/Lever2] SHTZ D·f14 SHTZ E·f16 SHTZ F·f18 SHTZ G·f20 SHTZ H·f21 SHTZ I·f21 SHTZ I·f21 SHTZ I·f21 SHTZ H·f21 SHTZ J·f21 SHTZ K·f21
- `raisereloading`: SHTZ L·f22 [**snd** weapons/sshoto; spawn SSGCaseSpawner, SSGCaseSpawner] SHTZ M·f22 SHTZ [·f22 SHTZ N·f22 SHTZ O·f22 SHTZ P·f22 SHTZ Q·f23 SHTZ S·f24 SHTZ T·f25 SHTZ T·f25 SHTZ U·f26 SHTZ V·f27 [**snd** weapons/sshotl; ammo SSGLoaded+1, SSGAmmo+1, AmmoShell-2] SHTZ W·f27 SHTZ X·f27 SHTZ Y·f28 TNT1 A*4 SHTZ Z·f29 SHZ2 A·f30 [**snd** weapons/sshotc] SHZ2 B·f31 SHZ2 C·f32 SHZ2 D·f38 SHZ2 E·f38 SHZ2 F·f38 SHZ2 F·f38 SHZ2 G·f39 SHZ2 H·f39 SHZ2 I·f40 SHZ2 J·f41 [**snd** SSG/Lever1] SHTZ B·f12 SHTZ A·f1 SHTZ A·f1

Sound lumps: SSG/Lever2 = SSGCLIP2 162 ms; weapons/sshoto = weapons/sshoto (file not found); weapons/sshotl = weapons/sshotl (file not found); weapons/sshotc = weapons/sshotc (file not found); SSG/Lever1 = SSGCLIP1 104 ms

![BD22_SSG_geometry_side.png](img/BD22_SSG_geometry_side.png)
![BD22_SSG_open_side.png](img/BD22_SSG_open_side.png)
![BD22_SSG_open_front.png](img/BD22_SSG_open_front.png)
![BD22_SSG_storyboard.png](img/BD22_SSG_storyboard.png)

## BD22/Rocket_Launcher

- DECORATE: `brutal22test6.pk3:actors/Weapons/RocketLauncher.dec`; model `RS_BD22_Models_v8.pk3:models/bd/RPG/RPG.md3` (30 frames), ready MISG A = mesh f5, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Frame 3762v/5559t; #1 Frame 300v/426t; #2 Cube 151v/62t; #3 Frame 48v/57t; #4 Trigger 46v/44t; #5 Cube 2549v/856t = drum; #6 Cube 234v/78t = drum; #7 Cube 230v/78t = drum; #8 Cube 232v/78t = drum; #9 Cube 234v/78t = drum; #10 Cube 234v/78t = drum; #11 Cube 234v/78t = drum; #12 Cube 228v/78t = drum

- **drum** (own surface: Cube#5 2549, Cube#6 234, Cube#7 230, Cube#8 232, Cube#9 234, Cube#10 234, Cube#11 234, Cube#12 228): well (-12.2, 2.2, 6.7), mouth (-12.2, -6.3, 10), insert dir (-0, 0.932, -0.362), depth 9.1 cm; base (-12.3, -19, 14.5); farthest out (0, -22.4, -46.3) (f23, 51.4 cm)  
  _surfaces 5-12: the rotary drum (5) with its seven rockets (6-12); taken out to the right and down (f16-f23), a full one goes in from the right (f24-f29)_


**Reload flow, empty** (AmmoRocket=200, RocketRounds=0; 46 tics, ends at Ready):

- `reload`: MISR A·f16 [**snd** rocket/reload1] MISR B·f17 MISR C·f18 MISR C·f18 MISR D·f19 MISR D·f19 MISR E·f20 MISR F·f21 [spawn RocketCaseSpawn] MISR G·f22 MISR H·f23
- `reloadunloaded`: MISR I·f24 MISR J·f24 MISR K·f24 MISR L·f24 MISR M·f24 MISR M·f24 MISR N*3·f24 MISR O·f24 MISR P·f24 MISR Q·f24 MISR R·f24 MISR S·f24 MISR S·f24 MISR T·f24 MISR T·f24 MISR T·f24 MISR T·f24
- `finishreloadanim`: MISR U·f25 [**snd** rocket/reload2; ammo RocketRounds+6, AmmoRocket-6] MISR V·f26 MISR V·f26 MISR V·f26 MISR W·f27 MISR X·f28 MISR Y*4·f29 MISR Z·f29 MISR Z·f29 MIR2 A·f29 MIR2 B·f29 MIR2 C·f29 MIR2 D·f29 MIR2 E·f5

**Reload flow, partial** (AmmoRocket=200, RocketRounds=1; 46 tics, ends at Ready):

- `reload`: MISR A·f16 [**snd** rocket/reload1] MISR B·f17 MISR C·f18 MISR C·f18 MISR D·f19 MISR D·f19 MISR E·f20 MISR F·f21 [spawn RocketCaseSpawn] MISR G·f22 MISR H·f23
- `reloadunloaded`: MISR I·f24 MISR J·f24 MISR K·f24 MISR L·f24 MISR M·f24 MISR M·f24 MISR N*3·f24 MISR O·f24 MISR P·f24 MISR Q·f24 MISR R·f24 MISR S·f24 MISR S·f24 MISR T·f24 MISR T·f24 MISR T·f24 MISR T·f24
- `finishreloadanim`: MISR U·f25 [**snd** rocket/reload2; ammo RocketRounds+5, AmmoRocket-5] MISR V·f26 MISR V·f26 MISR V·f26 MISR W·f27 MISR X·f28 MISR Y*4·f29 MISR Z·f29 MISR Z·f29 MIR2 A·f29 MIR2 B·f29 MIR2 C·f29 MIR2 D·f29 MIR2 E·f5

Sound lumps: rocket/reload1 = RLREL1 441 ms; rocket/reload2 = RLREL2 499 ms

![BD22_Rocket_Launcher_geometry_side.png](img/BD22_Rocket_Launcher_geometry_side.png)
![BD22_Rocket_Launcher_storyboard.png](img/BD22_Rocket_Launcher_storyboard.png)

## BD22/RailGun

- DECORATE: `brutal22test6.pk3:actors/Weapons/Railgun.dec`; model `RS_BD22_Models_v8.pk3:models/bd/RailGun/RailGun.md3` (32 frames), ready RAIL A = mesh f3, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Scope 2672v/2155t; #1 ScopeGlass 18v/8t; #2 Gun 4660v/3418t; #3 Trigger 46v/48t; #4 Mag-Bat 156v/104t = magazine

- **magazine** (own surface: Mag-Bat#4 156): well (22.1, 0, -3.5), mouth (22.1, 0, -8), insert dir (0.001, -0, 1), depth 4.4 cm; base (23.6, -0, -13.6); farthest out (-0, -0, -30.6) (f11, 30.6 cm)  
  _surface 'Mag-Bat': battery magazine_

- **Mag-out pose:** ready frame f3 with the magazine surface(s) #4 'Mag-Bat' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f11 (RAIR I): magazine at (-0, -0, -30.6) from seated, body tilt 15 deg
- Mag-out frames (magazine out of the well): f19 RAIR S/RAIR G mag at (-0, -0, -11.7) body tilt 15 deg; f15 RAIR H/RAIR O mag at (-0, -0, -25.1) body tilt 15 deg; f11 RAIR I mag at (-0, -0, -30.6) body tilt 15 deg; f12 RAIR J/RAIR K mag at (-0, 0, -30.3) body tilt 15 deg; f13 RAIR L/RAIR M mag at (-0, 0, -29.2) body tilt 15 deg; f14 RAIR N mag at (-0, 0, -27.5) body tilt 15 deg; f16 RAIR P mag at (-0, -0, -22.2) body tilt 15 deg; f17 RAIR Q mag at (-0, -0, -18.8) body tilt 15 deg; f18 RAIR R mag at (-0, -0, -15.3) body tilt 15 deg; f20 RAIR T mag at (-0, -0, -8.4) body tilt 15 deg; f21 RAIR U mag at (-0, 0, -5.5) body tilt 15 deg
- HUD animation tilts the whole gun up to 15.3 deg (f25); removed in all numbers above.

**Reload flow, empty** (AmmoCell=200, RailgunAmmo=0; 71 tics, ends at Ready):

- `reload`: RAIR A·f30 [**snd** Railgun/Reload1; spawn PlasmaCaseSpawn] RAIR B·f29 RAIR C·f28 RAIR D·f27 RAIR E·f26 RAIR F·f23 RAIR G·f19 RAIR H·f15 RAIR H·f15 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR J·f12 RAIR K·f12 RAIR L·f13 RAIR M·f13 RAIR N·f14 RAIR O·f15 RAIR O·f15 [**snd** Railgun/Reload2] RAIR P·f16 RAIR P·f16 RAIR P·f16 RAIR Q·f17 RAIR Q·f17 RAIR R·f18 RAIR S·f19
- `finishreload`: RAIR T·f20 [ammo RailgunAmmo+5, AmmoCell-50] RAIR T·f20 RAIR U·f21 RAIR V·f22 RAIR W·f23 RAIR X·f24 RAIR X·f24 RAIR X·f24 RAIR X·f24 RAIR X·f24 RAIR Y·f24 RAIR Z·f24 RAIR F·f23 RAIR [·f25 RAIR ]·f26 RAR2 A·f27 RAR2 B·f28 RAR2 C·f29 RAR2 D·f30 RAR2 D·f30 RAR2 E·f3 RAR2 F·f3 RAR2 G·f3 [**snd** Plasma/Beep] RAR2 H·f3 RAR2 H·f3 RAR2 H·f3 RAR2 I·f3 [**snd** Railgun/Recharge] RAR2 I·f3 RAR2 I·f3 RAR2 I·f3 RAR2 J·f3 RAR2 K·f3 RAR2 L·f3 RAR2 M·f3 RAR2 N·f3 RAR2 O·f3 RAR2 P·f3 RAR2 Q·f3

**Reload flow, partial** (AmmoCell=200, RailgunAmmo=1; 71 tics, ends at Ready):

- `reload`: RAIR A·f30 [**snd** Railgun/Reload1; spawn PlasmaCaseSpawn] RAIR B·f29 RAIR C·f28 RAIR D·f27 RAIR E·f26 RAIR F·f23 RAIR G·f19 RAIR H·f15 RAIR H·f15 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR I·f11 RAIR J·f12 RAIR K·f12 RAIR L·f13 RAIR M·f13 RAIR N·f14 RAIR O·f15 RAIR O·f15 [**snd** Railgun/Reload2] RAIR P·f16 RAIR P·f16 RAIR P·f16 RAIR Q·f17 RAIR Q·f17 RAIR R·f18 RAIR S·f19
- `finishreload`: RAIR T·f20 [ammo RailgunAmmo+4, AmmoCell-40] RAIR T·f20 RAIR U·f21 RAIR V·f22 RAIR W·f23 RAIR X·f24 RAIR X·f24 RAIR X·f24 RAIR X·f24 RAIR X·f24 RAIR Y·f24 RAIR Z·f24 RAIR F·f23 RAIR [·f25 RAIR ]·f26 RAR2 A·f27 RAR2 B·f28 RAR2 C·f29 RAR2 D·f30 RAR2 D·f30 RAR2 E·f3 RAR2 F·f3 RAR2 G·f3 [**snd** Plasma/Beep] RAR2 H·f3 RAR2 H·f3 RAR2 H·f3 RAR2 I·f3 [**snd** Railgun/Recharge] RAR2 I·f3 RAR2 I·f3 RAR2 I·f3 RAR2 J·f3 RAR2 K·f3 RAR2 L·f3 RAR2 M·f3 RAR2 N·f3 RAR2 O·f3 RAR2 P·f3 RAR2 Q·f3

Sound lumps: Railgun/Reload1 = RGREL1 751 ms; Railgun/Reload2 = RGREL2 772 ms; Plasma/Beep = BEP 78 ms; Railgun/Recharge = RAILR1 1260 ms

![BD22_RailGun_geometry_side.png](img/BD22_RailGun_geometry_side.png)
![BD22_RailGun_storyboard.png](img/BD22_RailGun_storyboard.png)

## BD22/Plasma_Gun

- DECORATE: `brutal22test6.pk3:actors/Weapons/Plasma.dec`; model `RS_BD22_Models_v8.pk3:models/bd/Plasma_Gun/Plasma.md3` (26 frames), ready PRSG F = mesh f4, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 Frame 4v/2t; #1 Battery 34v/12t = magazine; #2 Trigger 88v/84t; #3 Frame 7467v/8580t

- **magazine** (own surface: Battery#1 34): well (12.6, 0, -10), mouth (13.2, -0.5, -13.5), insert dir (-0.192, 0.132, 0.973), depth 3.6 cm; base (25.4, -0.2, -20.3); farthest out (6.6, -0.7, -41.3) (f15, 41.8 cm)  
  _surface 'Battery' (34 verts, a box): the cell_

- **Mag-out pose:** ready frame f4 with the magazine surface(s) #1 'Battery' not drawn (MODELDEF SurfaceSkin <surface> on a blank skin, as RS_BD22_Models already does for the HK416 hands); authored alternative f15 (PRSR G/PRSR H/PRSR I): magazine at (6.6, -0.7, -41.3) from seated, body tilt 0.8 deg
- Mag-out frames (magazine out of the well): f15 PRSR G/PRSR H/PRSR I mag at (6.6, -0.7, -41.3) body tilt 0.8 deg; f16 PRSR J/PRSR K mag at (3, -0.6, -15.3) body tilt 2.9 deg; f17 PRSR L mag at (1.8, -0.6, -8.9) body tilt 6 deg; f18 PRSR M mag at (0.9, -0.4, -4.8) body tilt 9.9 deg
- HUD animation tilts the whole gun up to 21.9 deg (f22); removed in all numbers above.

**Reload flow, empty** (AmmoCell=200, PlasmaAmmo=0; 55 tics, ends at Ready):

- `reload`: PRSR A·f14 [**snd** Plasma/Reload1; spawn PlasmaCaseSpawn] PRSR A·f14 PRSR Z·f14 PRSR B·f14 PRSR C·f14 PRSR D·f15 PRSR E·f15 PRSR F·f15 PRSR G·f15 PRSR H·f15 PRSR H·f15 PRSR I*10·f15 PRSR J·f16 PRSR K·f16 PRSR L·f17 PRSR M·f18 PRSR N·f19 PRSR N·f19 PRSR O·f20 PRSR O·f20 [**snd** Plasma/Reload2] PRSR O·f20 PRSR O·f20 PRSR O·f20
- `finishreload`: PRSR P·f20 [ammo PlasmaAmmo+50, DoublePlasmaAmmo+50, AmmoCell-50] PRSR Q·f20 PRSR R·f20 PRSR S·f20 PRSR T·f20 PRSR T·f20 PRSR T·f20 PRSR T·f20 PRSR U·f21 PRSR V·f22 PRSR W·f23 PRSR X·f24 PRSR Y·f25 PRSR C·f14 PRSR Z·f14 PRSR A·f14 PRSR A·f14 PRSG I*2·f4 PRSG F*2·f4 PRSG I*2·f4

**Reload flow, partial** (AmmoCell=200, PlasmaAmmo=1; 55 tics, ends at Ready):

- `reload`: PRSR A·f14 [**snd** Plasma/Reload1; spawn PlasmaCaseSpawn] PRSR A·f14 PRSR Z·f14 PRSR B·f14 PRSR C·f14 PRSR D·f15 PRSR E·f15 PRSR F·f15 PRSR G·f15 PRSR H·f15 PRSR H·f15 PRSR I*10·f15 PRSR J·f16 PRSR K·f16 PRSR L·f17 PRSR M·f18 PRSR N·f19 PRSR N·f19 PRSR O·f20 PRSR O·f20 [**snd** Plasma/Reload2] PRSR O·f20 PRSR O·f20 PRSR O·f20
- `finishreload`: PRSR P·f20 [ammo PlasmaAmmo+49, DoublePlasmaAmmo+49, AmmoCell-49] PRSR Q·f20 PRSR R·f20 PRSR S·f20 PRSR T·f20 PRSR T·f20 PRSR T·f20 PRSR T·f20 PRSR U·f21 PRSR V·f22 PRSR W·f23 PRSR X·f24 PRSR Y·f25 PRSR C·f14 PRSR Z·f14 PRSR A·f14 PRSR A·f14 PRSG I*2·f4 PRSG F*2·f4 PRSG I*2·f4

Sound lumps: Plasma/Reload1 = PLSREL1 1501 ms; Plasma/Reload2 = PLSREL2 984 ms

![BD22_Plasma_Gun_geometry_side.png](img/BD22_Plasma_Gun_geometry_side.png)
![BD22_Plasma_Gun_storyboard.png](img/BD22_Plasma_Gun_storyboard.png)

## BD22/GrenadeLauncher

- DECORATE: `brutal22test6.pk3:actors/Weapons/GrenadeLaunch.dec`; model `RS_BD22_Models_v8.pk3:models/bd/M79/M79.md3` (26 frames), ready GRLN A = mesh f3, scale (-1, 1, 1) offset (0, 0, -5)
- Surfaces: #0 pCylinder10 241v/200t = latch; #1 pCylinder10 2980v/3246t; #2 pCylinder10 142v/92t; #3 Shell 828v/638t = grenade; #4 pCylinder10 2667v/2292t = barrel

- **barrel** (own surface: pCylinder10#4 2667): hinge axis (-0.001, 1, 0) through (18.3, 0, -3.7), 30 deg open (f15); closed centre (30.2, -0.1, 1), open centre (31, -0.1, -5.6)  
  _M79 barrel, breaks open 30 deg down_
- **grenade** (own surface: Shell#3 828): port (15.4, -0, 2.3) (f20), approach dir (0.867, -0.001, -0.499), size 11.2 x 3.7 cm  
  _surface 'Shell' = the 40 mm round: the empty is drawn out backwards f11-f15 (GrenadeCasingSpawner), the new one goes into the open barrel f16-f20_
- **latch** (own surface: pCylinder10#0 241): rest centre (3.2, -0, 2.7)  
  _top latch, turned 45 deg while open_

- HUD animation tilts the whole gun up to 25 deg (f15); removed in all numbers above.
- GrenadeCasingSpawner + SmokeSpawner @GRLN L (f13, empty drawn out)
- Loaded gun: Reload goes to Inspect

**Reload flow, empty** (AmmoRocket=200, GLAmmo=0; 47 tics, ends at Ready):

- `reload`: GRLN F·f7 GRLN G·f8 GRLN H·f9 GRLN I·f10 GRLN I·f10
- `raisereloading`: GRLN J·f11 [**snd** GrenadeLauncher/Open] GRLN K·f12 GRLN L·f13 [spawn GrenadeCasingSpawner, SmokeSpawner] GRLN L·f13 GRLN M·f14 GRLN N·f15 GRLN O·f15 GRLN O·f15 GRLN P·f15 GRLN Q·f16 GRLN R·f16 GRLN T·f17 GRLN T·f17 GRLN U·f17 GRLN U·f17 GRLN U·f17 [**snd** GrenadeLauncher/Load; ammo GLAmmo+1, GLLoaded+1, AmmoRocket-1] GRLN V·f18 GRLN W·f18 GRLN X·f19 GRLN Y·f20 TNT1 A*4 GRLN Z·f21 GRLN [·f22 [**snd** GrenadeLauncher/Close] GRLN \·f23 GRLN ]·f24 GRL2 A·f25 GRL2 B·f25 GRL2 C·f25 GRL2 C·f25 GRL2 D·f25 GRL2 D·f25 GRL2 E·f25 GRL2 F·f25 GRL2 G·f25 GRL2 H·f3 GRL2 I·f3 GRL2 J·f3 GRL2 K·f3 GRL2 L·f3

**Reload flow, partial** (AmmoRocket=200, GLAmmo=1; 7 tics, ends at Ready3):

- `inspect`: GRLN A*6·f3 GRLN A·f3

Sound lumps: GrenadeLauncher/Open = DSGROPEN 208 ms; GrenadeLauncher/Load = DSGRLOAD 186 ms; GrenadeLauncher/Close = DSGRCLOS 359 ms

![BD22_GrenadeLauncher_geometry_side.png](img/BD22_GrenadeLauncher_geometry_side.png)
![BD22_GrenadeLauncher_open_side.png](img/BD22_GrenadeLauncher_open_side.png)
![BD22_GrenadeLauncher_open_front.png](img/BD22_GrenadeLauncher_open_front.png)
![BD22_GrenadeLauncher_storyboard.png](img/BD22_GrenadeLauncher_storyboard.png)

## BD22/Sniper

- DECORATE: `brutal22test6.pk3:actors/Weapons/Sniper.dec`; model `RS_BD22_Models_v8.pk3:models/bd/HK416/hk416.iqm` (360 frames), ready X21G A = mesh f25, scale (-1.35, 1.35, 1.35) offset (6.499, -3.835, 10.913)
- Surfaces: #0 SUP.bmp 613v/504t; #1 Grip2.bmp 1684v/1652t; #2 1.bmp 4110v/3303t = charging_handle; #3 9.bmp 1628v/1242t; #4 cock.bmp 771v/707t; #5 marg-ris.bmp 1053v/604t; #6 f1.bmp 808v/761t; #7 mag.bmp 132v/96t = magazine_new+magazine; #8 Magpul_Diffuse.bmp 1890v/1528t = magazine_new+magazine; #9 eotech553.bmp 2394v/2238t; #10 glass.bmp 8v/6t; #11 anpaq.bmp 1265v/1296t

- **magazine_new** (vertex group: mag.bmp#7 66/132, Magpul_Diffuse.bmp#8 945/1890): port (12.4, 0.5, -9.6) (f110), approach dir (-0.066, -0.149, 0.987), size 19.1 x 9.2 cm  
  _second copy of the magazine (Magpul PMAG mesh + its rounds), parked 1.7 m below the gun when unused; brought up and seated f79-f110, swapped back for the seated copy at f142_
- **magazine** (vertex group: mag.bmp#7 66/132, Magpul_Diffuse.bmp#8 945/1890): well (11.6, 0.6, 3.2), mouth (11.9, 1.4, -2.1), insert dir (-0.066, -0.149, 0.987), depth 5.3 cm; base (13, 0.7, -14.3); farthest out (-56, 50.6, -149.8) (f130, 167.7 cm)  
  _IQM mesh 9 (Magpul_Diffuse) + mesh 8 (mag.bmp, rounds), skinned to joints j_mag1/j_mag2 under tag_mag_attach; seated copy. Pulled out f91-f118 and thrown f124-f134 (insert_dir taken from the new copy's last approach)_
- **charging_handle** (vertex group: 1.bmp#2 366/4110): grab (-4.6, -0.3, 10.2), pull (-1, 0, -0), travel 7.6 cm (max at f302)  
  _part of IQM mesh 3 (1.bmp) skinned to j_charginghandle: AR T-handle, pulled at X22R L-M_

- **Mag-out pose:** ready frame f25 with the magazine vertex group in #7 'mag.bmp', #8 'Magpul_Diffuse.bmp' not drawn (needs a mesh copy with those vertex ranges collapsed or split into their own surface); authored alternative f95 (X21R O): magazine at (0.3, -2, -14.3) from seated, body tilt 36.8 deg
- Mag-out frames (magazine out of the well): f92 X21R L mag at (-0, 0.2, -9.1) body tilt 41.7 deg; f93 X21R M mag at (1.1, -1.8, -12.7) body tilt 38.1 deg; f94 X21R N mag at (1.4, -3.2, -13.7) body tilt 35.1 deg; f95 X21R O mag at (0.3, -2, -14.3) body tilt 36.8 deg; f96 X21R P mag at (0.8, -0.2, -13.3) body tilt 40.2 deg; f97 X21R Q mag at (1.4, 2.2, -9.9) body tilt 45.9 deg; f98 X21R R mag at (1, 4.3, -6.9) body tilt 52.1 deg; f99 X21R S mag at (-0, 5, -5.5) body tilt 55.3 deg; f100 X21R T mag at (-0.5, 4.2, -5.9) body tilt 53 deg; f101 X21R U mag at (-0.4, 3.4, -6.2) body tilt 53.5 deg; f102 X21R V mag at (-0.3, 3.4, -6.2) body tilt 54.2 deg; f103 X21R W mag at (-0.5, 3.4, -6) body tilt 54.9 deg; f104 X21R X mag at (-0.5, 3.5, -5.8) body tilt 55.4 deg
- HUD animation tilts the whole gun up to 68.2 deg (f322); removed in all numbers above.
- Class Sniper (BD22 XM21 sprites X21R/X22R) drawn with the HK416 IQM (hk416.iqm, 360 frames); joints j_mag1, j_mag2, tag_mag_attach, j_charginghandle, j_bolt exist in the skeleton

**Reload flow, empty** (SniperAmmo=200, xm21Ammo=0; 80 tics, ends at Ready3):

- `reload`: X21R A·f25 X21R B·f63 X21R C·f67 X21R D·f70 X21R E·f73 X21R F·f76 X21R G·f79 X21R H·f82 X21R H·f82 X21R I·f88 X21R I·f88 X21R I·f88 [**snd** Sniper/MagOut] X21R I·f88 X21R J·f90 X21R K·f91 X21R L·f92 X21R M·f93
- `continuereload`: X21R N·f94 [spawn EmptySniperAmmoSpawn] X21R O·f95 X21R P·f96 X21R P·f96 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R R·f98 X21R S·f99 X21R T·f100 X21R U·f101 X21R U·f101 [**snd** Sniper/MagIn] X21R U·f101 X21R V·f102 X21R V·f102 X21R W·f103
- `finishreload`: X21R X·f104 [ammo xm21Ammo+10, SniperAmmo-10] X21R X·f104 X21R Y·f110 X21R Z·f114 X21R [·f118 X21R [·f118 X21R [·f118 X21R [·f118 X21R [·f118 X21R \·f124 X21R ]·f130 X22R A·f134 X22R B·f138 X22R C·f142 X21R B·f63 X22R D·f286 X22R E·f288 X22R F·f290 X22R G·f292 X22R H·f294 X22R I·f296 X22R J·f298 X22R K*5·f299 X22R L·f302 [**snd** Sniper/BoltBack] X22R M·f305 X22R M·f305 X22R M·f305 X22R M·f305 X22R M·f305 X22R N·f317 [**snd** Sniper/BoltForward] X22R N·f317 X22R O·f322 X22R P·f327 X22R Q·f332 X22R R·f337 X22R S·f343

**Reload flow, partial** (SniperAmmo=200, xm21Ammo=1; 56 tics, ends at Ready3):

- `reload`: X21R A·f25 X21R B·f63 X21R C·f67 X21R D·f70 X21R E·f73 X21R F·f76 X21R G·f79 X21R H·f82 X21R H·f82 X21R I·f88 X21R I·f88 X21R I·f88 [**snd** Sniper/MagOut] X21R I·f88 X21R J·f90 X21R K·f91 X21R L·f92 X21R M·f93
- `continuereload`: X21R N·f94 [spawn EmptySniperAmmoSpawn] X21R O·f95 X21R P·f96 X21R P·f96 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R Q·f97 X21R R·f98 X21R S·f99 X21R T·f100 X21R U·f101 X21R U·f101 [**snd** Sniper/MagIn] X21R U·f101 X21R V·f102 X21R V·f102 X21R W·f103
- `fullreload`: X21R X·f104 [ammo xm21Ammo+10, SniperAmmo-10] X21R X·f104 X21R Y·f110 X21R Z·f114 X21R [·f118 X21R [·f118 X21R [·f118 X21R [·f118 X21R [·f118 X21R \·f124 X21R ]·f130 X22R A·f134 X22R B·f138 X22R C·f142 X21R B·f63 X21R A·f25

Sound lumps: Sniper/MagOut = X21MGOUT 714 ms; Sniper/MagIn = X21MGIN 1426 ms; Sniper/BoltBack = X21BACK 590 ms; Sniper/BoltForward = X21FORW 1100 ms

![BD22_Sniper_geometry_side.png](img/BD22_Sniper_geometry_side.png)
![BD22_Sniper_storyboard.png](img/BD22_Sniper_storyboard.png)

## V+/VR_Revolver2

- DECORATE: `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/revolver.txt`; model `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/gats/rev.md3` (41 frames), ready REVL A = mesh f0, scale (1.35, 1.35, 1.35) offset (0, 0, 0)
- Surfaces: #0 python.004 298v/336t; #1 python.005 63v/60t = cylinder+ejector; #2 python.006 28v/34t; #3 python.007 105v/126t = barrel; #4 python.008 18v/16t = rounds; #5 python.009 18v/16t = rounds; #6 python.010 18v/16t = rounds; #7 python.011 18v/16t = rounds; #8 python.012 18v/16t = rounds; #9 python.013 18v/16t = rounds; #10 python.014 257v/252t = speedloader

- **barrel** (own surface: python.007#3 105): hinge axis (-0, -1, 0) through (9.4, -0, -1.7), 63.4 deg open (f25); closed centre (13.9, -0, 2.4), open centre (15.1, -0, -3.9)  
  _python.007: barrel + top strap of a TOP-BREAK revolver; tips down about the hinge at the front-bottom of the frame (f19-f31), closes f31-f33_
- **cylinder** (vertex group: python.005#1 50/63): hinge axis (-0, -1, 0) through (9.2, -0, -1.7), 63.4 deg open (f25); closed centre (6, -0, 1.5), open centre (10.7, -0, 2.6); chambers face (2.8, 0, 1.6) closed -> (9.2, -0, 5.5) open, bore axis open (0.448, -0, -0.894)  
  _python.005 without its rear disc: the cylinder (axis at L 0, U 1.55 when closed), tips with the barrel; rear_face_open = where the chambers face when open_
- **ejector** (vertex group: python.005#1 13/63): rest centre (2.8, 0, 1.5)  
  _13-vertex rear disc of python.005 (ejector star): pushed out of the cylinder when the action opens_
- **rounds** (own surface: python.008#4 18, python.009#5 18, python.010#6 18, python.011#7 18, python.012#8 18, python.013#9 18): port (9.4, 0.9, 6.9) (f23), approach dir (0.514, 0.247, -0.821), size 13 x 10.1 cm; hidden (collapsed) in the ready frame  
  _python.008-.013: six cartridges, collapsed (hidden) when closed; shown f20-f29 as the empties the ejector lifts (f20-f23 at the cylinder) and throws away (f24-f29)_
- **speedloader** (own surface: python.014#10 257): port (9, -0.1, 5.7) (f25), approach dir (0.482, -0, -0.876), size 10.3 x 5.3 cm; hidden (collapsed) in the ready frame  
  _python.014 (257 verts): new rounds in a loader, parked 1 m away (collapsed) when not used; comes down onto the open cylinder f21-f26, leaves and drops away f30-f37_

- HUD animation tilts the whole gun up to 31.9 deg (f23); removed in all numbers above.
- As VR_Revolver
- Hand Cannon: same mesh, frames, flow and sounds as VR_Revolver (skin WPN-REV2.png); every number of VR_Revolver applies

**Reload flow, empty** (Clip=200, VR_RevLoaded2=0; 40 tics, ends at ready):

- `reloada`: REVL Q*2·f16 [**snd** weapons/9mmclip1] REVL R*2·f17 REVL S*2·f18 REVL T*2·f19 REVL U*2·f20 REVL V*2·f21 REVL W*2·f22 REVL X*2·f23 REVL Y*2·f24 REVL Z*2·f25 REVO A·f26 [**snd** weapons/9mmclip2] REVO B*2·f27 REVO C*2·f28 REVO D*2·f29 REVO E*2·f30 REVO F*2·f31 REVO G*2·f32 REVO H*2·f33 REVO I·f34 [**snd** weapons/9mmslide] REVO J·f35 REVO K·f36 REVO L·f37 REVL A·f0
- `(end)`: - [ammo VR_RevLoaded2+6, Clip-6]

**Reload flow, partial** (Clip=200, VR_RevLoaded2=3; 40 tics, ends at ready):

- `reloada`: REVL Q*2·f16 [**snd** weapons/9mmclip1] REVL R*2·f17 REVL S*2·f18 REVL T*2·f19 REVL U*2·f20 REVL V*2·f21 REVL W*2·f22 REVL X*2·f23 REVL Y*2·f24 REVL Z*2·f25 REVO A·f26 [**snd** weapons/9mmclip2] REVO B*2·f27 REVO C*2·f28 REVO D*2·f29 REVO E*2·f30 REVO F*2·f31 REVO G*2·f32 REVO H*2·f33 REVO I·f34 [**snd** weapons/9mmslide] REVO J·f35 REVO K·f36 REVO L·f37 REVL A·f0
- `(end)`: - [ammo VR_RevLoaded2+3, Clip-3]

Sound lumps: weapons/9mmclip1 = 9mmclip1 (file not found); weapons/9mmclip2 = 9mmclip2 (file not found); weapons/9mmslide = 9mmslide (file not found)

![V+_VR_Revolver2_geometry_side.png](img/V+_VR_Revolver2_geometry_side.png)
![V+_VR_Revolver2_open_side.png](img/V+_VR_Revolver2_open_side.png)
![V+_VR_Revolver2_open_front.png](img/V+_VR_Revolver2_open_front.png)
![V+_VR_Revolver2_storyboard.png](img/V+_VR_Revolver2_storyboard.png)

## V+/VR_Shotgun

- DECORATE: `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/shotty.txt`; model `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/guns/shotgun.md3` (32 frames), ready SHTG A = mesh f0, scale (1.35, 1.35, 1.35) offset (0, 0, 0)
- Surfaces: #0 doomshot 494v/450t; #1 doomshot.001 69v/44t = pump; #2 shotshl 34v/32t = shell

- **pump** (own surface: doomshot.001#1 69): grab (34.5, -0, 1.3), pull (-1, -0, 0.002), travel 10.2 cm (max at f13)  
  _doomshot.001 = fore-end; the pump after every shot is SHTG J-Z (Fire, sound 'shotpump' at SHTG J); the reload's per-shell animation is that clip played backwards (SHTG R..J)_
- **shell** (own surface: shotshl#2 34): port (12.5, -0.5, 3.3) (f12), approach dir (0.892, 0.429, -0.14), size 5.2 x 2.4 cm; hidden (collapsed) in the ready frame  
  _shotshl: the ejected shell (collapsed at rest). Played backwards in the reload it flies INTO the ejection port; the set has no loading-port shell_

- HUD animation tilts the whole gun up to 1.1 deg (f12); removed in all numbers above.
- Reload never pumps; the pump is only in Fire (SHTG J-Z)

**Reload flow, empty** (VR_Shell=200, VR_ShotLoaded=0; 87 tics, ends at Ready):

- `startreload`: SHTG A*3·f0
- `reloadloop`: SHTG A·f0
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `reloadend`: SHTG A*3·f0

**Reload flow, partial** (VR_Shell=200, VR_ShotLoaded=4; 47 tics, ends at Ready):

- `startreload`: SHTG A*3·f0
- `reloadloop`: SHTG A·f0
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `insertshell`: SHTG R·f17 SHTG Q·f16 SHTG P·f15 SHTG O·f14 SHTG N·f13 SHTG M·f12 SHTG L·f11 SHTG K·f10 SHTG J·f9
- `reloadloop`: SHTG A·f0 [**snd** Shotgun/Reload; ammo VR_ShotLoaded+1, VR_Shell-1]
- `reloadend`: SHTG A*3·f0

Sound lumps: Shotgun/Reload = Shotgun/Reload (file not found)

![V+_VR_Shotgun_geometry_side.png](img/V+_VR_Shotgun_geometry_side.png)
![V+_VR_Shotgun_storyboard.png](img/V+_VR_Shotgun_storyboard.png)

## V+/VR_SuperShotgun

- DECORATE: `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/shotty.txt`; model `1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/models/weapons/hud/guns/ssg.md3` (26 frames), ready SHT2 A = mesh f0, scale (1.35, 1.35, 1.35) offset (0, 0, 0)
- Surfaces: #0 newshell1.006 34v/32t = new_shells; #1 newshell2.006 34v/32t = new_shells; #2 shotshell1.006 34v/32t = spent_shells; #3 shotshell2.007 34v/32t = spent_shells; #4 ssgbarrel.006 160v/152t = barrels; #5 ssgbase.006 379v/302t

- **barrels** (own surface: ssgbarrel.006#4 160): hinge axis (0, -1, 0) through (12.5, 0, 0.2), 58.5 deg open (f12); closed centre (24.9, -0, 3.2), open centre (21.5, -0, -8.8)  
  _ssgbarrel: breaks open 59 deg_
- **spent_shells** (own surface: shotshell1.006#2 34, shotshell2.007#3 34): rest centre (8, 0, 3.5)  
  _shotshell1/2: in the chambers at rest, thrown out f9-f20, back in the chambers at f21-f24_
- **new_shells** (own surface: newshell1.006#0 34, newshell2.006#1 34): port (12.8, 0, 6) (f21), approach dir (0.618, 0, -0.786), size 5.2 x 2.4 cm; hidden (collapsed) in the ready frame  
  _newshell1/2: collapsed (hidden) 53 cm behind the gun at rest; brought to the open chambers f14-f21_

- HUD animation tilts the whole gun up to 4 deg (f11); removed in all numbers above.
- Fire always goes to Reload afterwards (no half-load); lumps are the engine's Doom 2 ones

**Reload flow, empty** (VR_Shell=200, VR_SSGLoaded=0, VR_SSGAlt=0; 45 tics, ends at Ready):

- `reload`: SHT2 I*2·f8 [**snd** weapons/sshoto (implicit, A_OpenShotgun2)] SHT2 J*3·f9 SHT2 K*3·f10 SHT2 L*3·f11 SHT2 M*3·f12 SHT2 N*3·f13 SHT2 O*3·f14 SHT2 P*3·f15 SHT2 Q*3·f16 SHT2 R*3·f17 SHT2 S*2·f18 [**snd** weapons/sshotl (implicit, A_LoadShotgun2); ammo VR_SSGLoaded+1] SHT2 T*3·f19 SHT2 U*3·f20 SHT2 V*3·f21 SHT2 X*2·f23 [**snd** weapons/sshotc (implicit, A_CloseShotgun2)] SHT2 Y*2·f24 SHT2 Y·f24

Sound lumps: weapons/sshoto = dsdbopn (file not found); weapons/sshotl = dsdbload (file not found); weapons/sshotc = dsdbcls (file not found)

![V+_VR_SuperShotgun_geometry_side.png](img/V+_VR_SuperShotgun_geometry_side.png)
![V+_VR_SuperShotgun_open_side.png](img/V+_VR_SuperShotgun_open_side.png)
![V+_VR_SuperShotgun_open_front.png](img/V+_VR_SuperShotgun_open_front.png)
![V+_VR_SuperShotgun_storyboard.png](img/V+_VR_SuperShotgun_storyboard.png)
