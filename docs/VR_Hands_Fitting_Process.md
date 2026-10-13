# How the VR hands were fitted to BD22's and Vanilla VR Plus's guns

(Copy of the zDoomVR project doc claude/VR_Hands_Fitting_Process.md, 2026-10-12.)

The method in one line: **take Ermac's already-posed hands and move them onto
the new gun as rigid pieces, fitted against the part of the gun they hold.**
Nothing is posed by eye, and no hand is posed from scratch. It works on QuestZDoom
17.x with no engine changes. The same tools work for any HUD-model weapon set,
including RS_VR_Weapons.

## 1. Where the poses come from

`E:\DOOMWork\_old\doom-force-unleashed_devbuild` is Ermac's Rusted Legacy / Force
Unleashed (MIT). His `hand.md3` (gun hand) and `hand2.md3` (support hand) each
hold a frame posed **for every one of his weapons**. They are drawn inside the
weapon's own MODELDEF block with the weapon's placement (`Scale -1 1 1`,
`Offset 0 -24 -10`), so every pose is correct relative to his gun.

| Ermac set | gun hand (two hands) | support hand | gun hand (one hand) |
|---|---|---|---|
| pistol | 19 | 4 (cups the gun hand) | 6 |
| shotgun | 30 | 15 (round the pump) | 30 |
| ssg | 47 | 33 (fore-end) | 47 |
| chaingun | 84 | 70 (top handle) | 84 |
| rocket | 95 | 80 (palm under the tube) | 95 |
| plasma | 106 | 91 (fist on a vertical grip) | 106 |
| bfg | 113 | 98 | 113 |

`hands/ermac.py` lists these (his `modeldefs/weapons/*.txt`, "with both hands" blocks, frame A).
His off hand is `hand.md3` frame 0 (open) and frame 1 (fist). His `ammo_hand.md3`
frames 0-8 hold a pistol mag, shell, two shells, chaingun mag, rocket, cell, BFG
pod and so on, with the mag as a second model in the same block.

## 2. The transform chain (what every tool reproduces)

`models.cpp RenderHUDModel`, applied to a mesh vertex `v`:

    world = HandTransform * S(0.01) * T(0,5,30) * S(Scale.x, Scale.z, Scale.y)
            * T(Offset) * T(-vr_3dweaponOffsetX, Y, Z) * R(rotation) * T(translation)
            * Ry(90) * S(vr_weaponScale) * swap_yz(v)

- The MODELDEF Scale is applied **after** the jDoom 90-degree turn, so
  `Scale y` is the mesh's **length** axis and `Scale x` its width. (The HK416
  sniper had `Scale -1.35 -1.35 1.35`. That turned it round and put it 69 cm behind
  the hand, so from v4 to v7 it was never visible. Fixed in v8: `-1.35 1.35 1.35`, Offset recomputed.)
- `translation` / `rotation` are what `Weapon.ModifyBobLayer3D` returns for a
  layer: the **hook**. The rotation is yaw about y, then pitch about x, then roll
  about z (standard right-handed, `VSMatrix::rotate`), about pivot 0. The hook
  translation is added after the 90-degree turn and before the MODELDEF scale.
- `hands/hudrender.py: to_local()` is this chain (metres, x right, y up, z back).
  `hands/gunview.py: to_fl()` turns it into the controller frame in cm:
  **F forward, L left, U up**. Every number in these notes is in that frame.

## 3. Tools (all in `hands/`)

| File | What it does |
|---|---|
| `gunview.py` | Orthographic side / bottom / front / top views of any HUD model (md3 or IQM, skinned) on a 5 cm grid in F/L/U, with markers. This is how the grips, fore-ends, magazine wells and handles were measured. |
| `hudrender.py` | Shaded perspective render from any eye point (the "player view" sheets). |
| `guns.py` | The ready frame of each BD22 gun and its placement from the pack's MODELDEF. |
| `ermac.py` | Ermac's sets and placement. |
| `align.py` | The fit. It samples the surface of Ermac's gun, keeps the **patch the hand holds** (points within 3 cm of the hand), and fits that patch onto the BD22 gun by ICP (translation only, trimmed nearest points) inside a search box. Output: a shift in F/L/U, then `hook_from_shift()` converts it to the ModifyBobLayer3D hook. |
| `fitall.py` | Runs every gun from `handtable.py` and writes `fits.json` and the check sheets. |
| `minigun_fit.py` | `rot_hook()`: turns a pose by any rotation (given as the hand's axis and the back of the hand) about its centre and moves it to a target. It returns the hook and the rotation. Used for the minigun's side handle. |
| `support.py` | Cross-sections of a gun at any F (`section`, `front_point`): it finds the fore-end's centre or underside. |
| `../rsq_hands_gen.py` | Turns `fits.json` into the pack: `zscript/rsq/handtable.zs` (per-gun frames, hooks, support points), the `MODELDEF.rsq` hand blocks, and `hand.md3` / `hand2.md3` cut to the frames used (1.7 MB to 100 KB). |

## 4. Fitting modes (`handtable.py`)

- **Gun hand**: ICP of Ermac's grip patch onto the BD22 grip
  (box F -22..6, U -24..-1), then 1.5 cm down (4 cm on the rocket launcher, whose grip is long).
- **wrap** (rifles, shotguns, SMGs, rail, plasma, MG42, BFGs): Ermac's pump or
  fore-end patch is fitted at a chosen F on the front. For a part thicker than
  6 cm, only the underside is searched (a hand can't wrap a 10 cm body).
  The hand is centred left-right.
- **vgrip** (sniper HK416, M32, Devastator vertical foregrips): Ermac's
  vertical-grip fist (91), its centre put on the grip's centre.
- **under** (rocket launcher): Ermac's palm-under pose set on the tube's underside.
- **same** (pistol, revolver): the support hand keeps Ermac's arrangement with
  the gun hand, cupped under it.
- **handlebar** (minigun): fist 91 turned so the handle runs through it like a
  bicycle grip: knuckles forward, forearm back toward the player.
- No hands: melee weapons, grenades, two-gun weapons, and the flame cannon
  (the arm goes inside it).

## 5. In the engine (`zscript/rsq/hands.zs`)

- A layer is drawn on the **off** controller only when its caller is the player's
  off-hand weapon (`models.cpp:221`). So:
  - `RSQ_Hands` is an off-hand weapon that never fires. It owns the free hand (layer 2200).
  - `RSQ_GunSide` is a plain inventory item. It owns the gun hand (2100) and the
    support hand (2101) on the main controller.
- `hw_weapon.cpp` calls the off-hand weapon's `ModifyBobLayer3D` for every layer
  that isn't the ready weapon's. `RSQ_Hands` returns `bob + hook` for 2100 and 2101,
  looked up by the ready weapon's class (`RSQ_HandTable`).
- **Two-hand swap** (Ermac's idea): within 15 cm of the gun's support point the
  off hand takes hold. The free hand hides and the support hand shows; pistols
  also switch to the two-hand gun-hand pose. It lets go past 22 cm, and never
  holds while a reload needs the hand.
- Layers clear `bAddWeapon` and set `bAddBob`.

## 6. Checking

1. `fitall.py` sheets: a side view in cm plus a player-eye render for every gun
   (`review_*.png`). Each was looked at before it went in.
2. In the engine, desktop mode: the console commands `vr_3dweaponOffsetZ -45; vr_3dweaponOffsetY -15; fov 110`
   push the HUD models into view. These offsets sit inside the chain, so the hands
   and the gun move together and the screenshot shows how they sit on each other.
3. A test pack swaps `zscript/rsvr/vrhand.zs` for a fake (`rtest/vrhand_fake.zs`):
   - the gun hand is in front of the player;
   - the off hand is scripted. Mode 0 keeps it still, mode 1 makes it do each
     reload step, and mode 2 holds it on the support point.

   A logger prints the ammo, layer states and gate events, so stock and immersive
   reloads, waits, skips and holds are all checked headless.

## 7. Doing this for another weapon set (RS_VR_Weapons, avatar hands)

1. Point `guns.py` at the set's MODELDEF and ready frames.
2. Look at each gun with `gunview.py` and choose its mode in `handtable.py`
   (wrap F, vgrip box, and so on).
3. Run `fitall.py`. Check the sheets. Adjust the mode or F and run it again.
4. Run `rsq_hands_gen.py`, then build.

Ermac's frames carry the pose and the fit carries only the position, so a new
gun costs one line in `handtable.py`.

## 8. Vanilla VR Plus (RS_VanillaVRPlus_VR.pk3): what the second set added

Tools: `../vplus/fit/` (`vplus.py` teaches `guns.item()` the set's guns from its own
MODELDEF; `vfit.py`, `sawfit.py`, `vsheets.py`; results in `vfits.json`).

**Shared meshes carry their fit.** `meshsig.py` gives each md3 a signature (per surface:
vertex and triangle counts, a hash of the triangles and texture coordinates), so the same
mesh is found whatever frames it carries. Four of the set's guns are BD22's meshes:
chaingun = BD22 minigun, rocket launcher, plasma rifle, BFG. Their ready frames match
BD22's vertex for vertex, 5 cm higher (BD22's MODELDEF has `Offset 0 0 -5`, this set's
`0 0 0`). So every hand moves by the same 5 cm (`vfit.shared()`): no new fit. A rotated
support hand (the minigun's handlebar) takes the move inside its rotation:
`hook += R^-1 * move`.

**A hand can be turned as well as moved.** Some handles run a different way from the one
Ermac's hand closes round. `rot_hook()` in `minigun_fit.py` turns the pose about a point
and moves that point onto a target. `handtable.zs` now has `GunRot`, beside `SupportRot`,
and `hands.zs` adds it for the gun hand.
- Chainsaw, right hand: the tube Ermac's chainsaw hand (hand.md3 29) closes round runs
  forward and up at 38 degrees. This saw's rear-handle tube runs straight back. The hand is
  turned 35 degrees about its left axis and the held part of Ermac's tube is put on the
  middle of this one. The axes are each held patch's principal axis.
- Chainsaw, left hand: fist 91 turned palm-down onto the top bar of the front arch, thumb
  toward the middle. For a fist, use the slot inside the curl (cross-sections at U -6..-8
  put it at F 25, L -1.5, U -5.2 in Ermac's frame), not the patch centre: the centre of
  the gun points near his fist is the gun's underside.

**Check with cross-sections.** `xsec.py` cuts the gun and the hand with a plane and
draws both outlines. A grip is held when its section sits inside the hand's curl: palm on
one side, fingers round the front. It caught the first chainsaw fit, which had the hand
beside the tube.

**Pick reload pauses from the animation.** `board.py` draws a storyboard of a gun's
frames. That shows when the magazine drops (M16 O-U), when the new one rises (D-I) and
when the charging handle moves (K). It also shows what moves: diffs per surface between
frames gave the pump (8.8 cm back) and the charging handle.

## 9. Trigger finger (2026-10-12, both v9 packs)

Ermac's grip frames have the index finger straight along the receiver, above the
trigger guard, and hand.md3 has no trigger-pulled frames. So the finger is bent by us.

**The finger is its own mesh piece.** In the cut hand.md3 (one surface, 1021 verts) the
mesh splits into 8 connected pieces: palm 482, sleeve 136, cuff 15, thumb 66, and one per
finger. The index finger is piece 1 (79 verts), separate from the palm, so it can be
bent without touching anything else. Built only on the pack's own cut hand.md3; nothing
under `_old/` was read.

**Rig** (`rig.py`): three hinges along the finger, found from gaps in the vertex rings of
the straight pose: MCP at the root (s 0), PIP at s 2.09, DIP at s 4.39 (md3 units; tip
7.1). Flexion turns about the finger's lateral axis, toward the middle finger (the palmar
side). MCP also has abduction. Each joint blends its turn over a short band so the skin
does not tear, and the root ring stays on the knuckle. Joints are applied distal first
about fixed pivots, which gives correct forward kinematics. Normals turn with the
vertices. An optional root slide (up to 0.9 cm, blended to zero at the knuckle) covers
triggers just out of reach.

**Trigger per gun** (`trig.py`, `boxes.py`): the trigger blade is picked by a box in a
1 cm slab on the gun's centreline (side view). The target is the blade's front face at
20-80 % of its height, plus 0.2 cm of skin. The solver (grid start, then Powell)
minimises pad-to-target distance, with the pad facing back (-F), the DIP following the
PIP (about 0.65x), a penalty for any finger vertex inside the blade's box, and joint
limits. Pad = the palmar-most vertex of the distal segment at s 5.6-6.5.
- Guns with no trigger in the mesh (BD22 Devastator, Flamethrower2, Minigun, Unmaker,
  BFGs, Hellish, Rocket_Launcher) use a virtual trigger: the mean trigger offset from the
  MCP of the rifle-type guns, in the finger's own frame.
- V+'s low-poly revolver, M16, shotgun and SSG have a guard but no blade: the target is
  a point inside the guard opening. Its four BD22-mesh guns copy BD22's poses (hand and
  gun are both 5 cm higher, so the finger pose is identical).
- Squeeze = a further curl of about 18 degrees (MCP +0.2, PIP +0.5, DIP +0.3 of it).

**Reach is the limit.** Ermac's finger is short and the index root sits 3-5 cm to the
side of the gun's centreline. Most pads land within 0.5 cm. On the BD and V+ revolvers
and the BD pistol the trigger is almost under the knuckle, so the finger hooks down
hard; that is the grip fit, not the rig. Moving those gun hands back about 3 cm would
fix it (their fingers already float in front of the grip).

**In the pack** (`patch.py`, in place on the shipped pack, never a rebuild):
- one pose per unique (hand frame, angles): BD22 17 poses, V+ 8; two new hand.md3 frames
  each (on, squeezed), about 8 KB per frame before compression;
- MODELDEF.rsq: `FrameIndex RQGT X` (on the trigger) and `RQGU X` (squeezed);
- handtable.zs: `RSQ_HandTable.Trigger(i)`, a letter per gun ("" keeps the plain grip:
  axe, chainsaws);
- hands.zs: states `TrgX` / `SqzX`; the gun hand shows `SqzX` while `BT_ATTACK` is held
  (the synced usercmd, so it is netplay-safe), otherwise `TrgX`.

**Checks:** a side slab and a front slab per gun with the finger points, then one shaded
contact sheet of every gun (on and squeezed), then a headless load of the pack.

**Files:** `E:\DOOMWork\HANDOFF_trigger_finger.md` (status, how to re-apply) and
`E:\DOOMWork\RS_QuestHands\trigger_finger_kit.zip` (rig.py, trig.py, boxes.py,
vpsolve.py, build.py, patch.py, sol_bd.json, sol_vp.json, shots_*.png, noreload.py).

**Also on 2026-10-12:** VR reloading is switched off in both v9 packs (`noreload.py`:
the reload gate always says no, the menu row is greyed out, and the help text is gone).
Owner's verdict: not release-ready, too strict. BD revolver does not load, SSG too
tight, rocket launcher magazine does not catch.
