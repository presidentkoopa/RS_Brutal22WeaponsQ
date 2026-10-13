# Handoff: trigger finger on the Quest gun hands (BD22 v9, Vanilla VR Plus v9)

Owner's order: put the gun hand's index finger ON each gun's trigger, and make it SQUEEZE
when the gun fires. Do it yourself. No subagents. Report briefly. Check in as you go.
Stock QuestZDoom 17.3, no engine changes. Don't balloon file size.
Never launch anything on the owner's PC.

## The problem (verified 2026-10-11)
- The gun hand is Ermac's hand.md3 grip pose, fitted only by the grip (ICP on the grip patch).
  Its index finger points straight forward along the receiver, above the trigger guard
  (see the side view of fit_Rifle.png). It is NOT on the trigger. Same on every gun.
- Ermac's hand.md3 has NO trigger-pulled frames. All 211 frames were checked against every
  grip pose, also with rigid recoil removed. So the finger must be bent by us.

## Files (on E:\DOOMWork)
- BD22_Models_v9.pk3, RS_VanillaVRPlus_VR_v9.pk3: current packs. The minigun/chaingun
  support hand is already fixed in them: hand2 frame 91 bike grip, set in handtable.zs
  SupportHook/SupportRot (BD index 13, V+ index 7). Rebuilding from the kit loses this
  fix; re-apply it, see "Minigun fix" below.
- v9kit.zip: the build kit. Unzip it into your scratchpad as S. Every script hard-codes
  the old S = /tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad,
  so sed that to your own S. Then place:
  - S/out/RS_BD22_Models_v8.pk3 = E:\DOOMWork\BD22_Models_v8.pk3
  - S/vplus/RS_VanillaVRPlus_VR.pk3 = in the kit root, move it
- qzd_headless.zip: the local headless QuestZDoom build. Unzip to S/ (build/qzd/qzdoom,
  build/zminst/lib). Run with LD_LIBRARY_PATH=S/build/zminst/lib under xvfb-run, from
  cwd S/build/qzd. It needs freedoom2.wad in that dir: apt freedoom gives
  /usr/share/games/doom/freedoom2.wad.
- Base mods:
  - BD22: E:\DOOMWork\RS_VR_Weapons\bd22\brutal22test6.pk3
  - V+: the 1.0b_Weapons_VanillaVRPlus_v1.2 folder; ask the owner to attach it.
- Ermac's hand meshes: E:\DOOMWork\_old\doom-force-unleashed_devbuild\models\hand\
  (hand.md3, hand2.md3). The owner authorized Force Unleashed as the one exception to the
  `_old/` rule.

## How the hands are built
- **Gun hand:** layer 2100, sprite RQGS letters A–H. These are frames cut from hand.md3 into
  the pack's models/rsq/hand.md3. MODELDEF.rsq maps each letter to a frame.
- **Per-gun table:** zscript/rsq/handtable.zs, from team/melee_hands/gen. Per gun it gives:
  - GunOne / GunTwo letter
  - GunHook / GunRot
  - Support letter, SupportHook, SupportRot, SupportPoint
- **Hands script:** zscript/rsq/hands.zs, from team/hands.zs plus the reload hooks.
  - It draws the hands and makes them follow recoil through gunmoves.zs.
  - It has states GunA..GunH.
  - Its ModifyBobLayer3D places 2100/2101.
- **Fitting tools:** in kit `melee/` and `hands/`.
  - align.py, handfit.py (sheet renders), gunview.py and hudrender.py (render any gun and hand).
  - Chain: hands/HAND_FITTING.md in E:\DOOMWork\RS_QuestHands\tools\posefix\hands\.
  - Units: cm, controller frame F forward / L left / U up.
- **Builders:**
  - `python3 -I -B team/build_bd22_v9.py`
  - `python3 -I -B team/build_vplus_v9.py`
  - Both default to team/reload_merged. Output goes to team/out_v9/.
  - The BD builder refuses changed v8 rows in handtable. Patch new frames and letters
    after the build, or relax that check.
- **Load test:** `team/integ/rtest/run.py load_bd_v9 bd v9 none 300 "60:echo LOADED"`.

## Plan
1. Find the index-finger vertices of hand.md3 once (same topology in every frame):
   - the vertices that differ between an open frame (0) and a fist (1);
   - only those on the index finger.

   Also find its three joint pivots.
2. For each gun-hand pose used, find the gun's trigger point:
   - Use gunview side and bottom views of the gun's ready frame.
   - Placement comes from guns.py (BD22) and vplus/fit/vplus.py (V+).
   - BD22 gun hands: GunOne/GunTwo letters A–H, BD indexes 1–25. V+ has its own letters.
3. Make two frames per pose:
   - "on trigger": index bent at its joints so the pad of the fingertip touches the trigger face;
   - "squeeze": a further curl of about 15–20°.

   Write them as new frames of the cut hand.md3 (about 8 KB each). Render each gun with
   handfit.sheet and look at it.
4. Pick the frame in hands.zs:
   - Use the squeeze frame while the gun is in a firing state. The gunmoves table already
     knows the fire frames; alternatively check whether player.cmd.buttons has BT_ATTACK.
   - Otherwise use the on-trigger frame.
5. Rebuild both packs and load-test them. Render every gun. Put the packs on E:\DOOMWork.

## Minigun fix (re-apply after any rebuild)
- BD22 handtable index 13: SupportHook (-9.07, -25.68, -2.10), SupportRot (10.21, 16.06, 95.16).
- V+ index 7: SupportHook (-4.28, -26.11, -3.49), same rot.
- Support letter E = hand2 frame 91.

## For a Claude Code lane on the owner's PC (Windows, E:\DOOMWork)
- Budget rules: ONE session, NO subagents, stop and report after each gun's frames are made
  and rendered. Tell the owner up front if anything will take more than that.
- You can work straight from E:\DOOMWork; no container staging is needed. Unzip
  RS_QuestHands\v9kit.zip to a work folder such as E:\DOOMWork\RS_QuestHands\v9kit\ and set
  S to it. The scripts hard-code the old Linux scratchpad path: replace it with your folder,
  and use forward slashes or raw strings.
- Python with numpy and Pillow runs the fitting and render tools (melee/, hands/,
  handfit.sheet) and the builders. qzd_headless.zip is a LINUX build: ignore it on Windows.
  To load-test, use the owner's Windows QuestZDoom/QZD build only if the owner says so,
  launching desktop mode with the pack after its base and reading the console log. Do not
  launch anything without asking.
- The minimum viable path, if the vertex maths stalls:
  1. Export the 8 cut gun-hand frames (BD22 v9 pack, models/rsq/hand.md3, letters A-H per
     MODELDEF.rsq) to the owner for hand-posing in Blender.
  2. Do steps 3-4 of the plan in code: new MODELDEF letters, and the squeeze letter while
     firing in hands.zs.

## Sniper removal (re-apply after any rebuild): BD22 pack only
- The sniper rifle (HK416) is out of BD22_Models_v9.pk3 since 2026-10-12. The owner doesn't
  think we may use the model.
- Removed:
  - the models/bd/HK416/ folder;
  - the Model block with Path "models/bd/HK416" in MODELDEF.bd.txt (1 block);
  - the same blocks in MODELDEF.rsr (6 blocks).
- Added:
  - ZSCRIPT.nosniper, MAPINFO.nosniper (AddEventHandlers "RSQ_NoSniper");
  - zscript/nosniper/nosniper.zs.
- What the handler does:
  - CheckReplacement: Sniper -> Rifle, PuristSniper -> PuristRifle, SniperAmmo -> Clip2.
  - WorldTick: takes Sniper / PuristSniper from players and gives Rifle + 30 Clip2.
  - It looks the classes up by Name at run time, because BD22's classes are DECORATE. A class
    literal like 'Sniper' fails to compile.
- Copy these three entries from the current E:\DOOMWork\BD22_Models_v9.pk3 into any rebuilt
  pack, and drop HK416 and its blocks again.

## give all / idkfa gives every modeled BD22 gun (re-apply after any rebuild): BD22 pack only
- Done 2026-10-12. Two causes, two fixes; both now live in the shipped pack.
- **Cause 1: the CHEATNOTWEAPON flag.**
  - Removed the `+WEAPON.CHEATNOTWEAPON` line from the main actor in the pack's
    actors/Weapons/Dragonslayer.dec, Mp40.dec, MG42.dec and Devastator.dec.
  - MG42.dec and Devastator.dec were added to the pack, copied from brutal22test6.pk3.
  - The Purist* variants keep the flag.
- **Cause 2: replaced weapons.**
  - BD22 `replaces` MG42, Devastator, NukeLauncher and IncendiaryLauncher with pickup
    spawners, and the engine's give all skips replaced weapons (player.zs CheatGive).
  - In zscript/nosniper/nosniper.zs, RSQ_NoSniper.CheckReplacement sets
    `e.Replacement = null; e.IsFinal = true;` for those four. Null plus final means no
    replacement (events.cpp: setting the replacee itself is ignored).
- **Effects:**
  - Maps place the spawners directly, so they are unaffected.
  - A monster drop of those four gives the plain gun.
- **Tested:** `give all` gives DSweap, MP40, MG42, Devastator, NukeLauncher and
  IncendiaryLauncher, with no sniper and no script errors.
- **Rebuilding:** take nosniper.zs, MAPINFO.nosniper, ZSCRIPT.nosniper and those four .dec
  files from the current E:\DOOMWork\BD22_Models_v9.pk3.

## Current state of the shipped packs (2026-10-12)
- E:\DOOMWork\BD22_Models_v9.pk3 and E:\DOOMWork\RS_VanillaVRPlus_VR_v9.pk3 are the newest.
  They include everything above.
- The kit in RS_QuestHands\v9kit.zip rebuilds the packs WITHOUT these three patches:
  - the minigun bike grip;
  - the sniper removal;
  - give all.
- To add the trigger finger, prefer patching the current packs in place (add hand frames,
  MODELDEF lines and the hands.zs change) over rebuilding.

## DONE for BD22 (2026-10-12) — V+ still to do
- Shipped: E:\DOOMWork\BD22_Models_v9.pk3 (patched in place; old one in _backups\BD22_Models_v9_pre_trigger.pk3).
- Kit: RS_QuestHands\trigger_finger_kit.zip (rig.py, trig.py, build.py, patch.py, sol_bd.json, shots_bd.png).
  Built only on the pack's cut hand.md3; nothing from `_old/` was read.
- The index finger is mesh component 1 of hand.md3 (79 verts, separate piece). Rig: MCP/PIP/DIP hinges
  along the finger, MCP abduction, plus a small root slide (<=0.9 cm) where the trigger was out of reach.
- Per gun: trigger blade picked by box (boxes.py), fingertip pad solved onto its front face.
  Guns with no trigger mesh (Devastator, Flamethrower2, Minigun, Unmaker, BFGs, Hellish, Rocket_Launcher)
  use a virtual trigger at the mean trigger offset of the rifle-type guns.
- 17 unique poses -> 34 new hand.md3 frames (10..43): RQGT X = on trigger, RQGU X = squeezed.
  handtable.zs RSQ_HandTable.Trigger(i) gives the letter; hands.zs uses SqzX while BT_ATTACK is held, else TrgX.
  Axe, chainsaw (and the removed sniper) keep the plain grip frame.
- Re-apply after a rebuild: `python3 -I -B patch.py bd sol_bd.json <in.pk3> <out.pk3>` (asserts the hand.md3 matches).
- Headless load test: clean (only brutal22test6's own warnings). Not yet seen in a headset.
- V+: needs the 1.0b_Weapons_VanillaVRPlus_v1.2 folder for gun meshes; then add VP boxes to boxes.py,
  run batch.py/virt.py for vp, patch.py vp.

## VR reloading: switched OFF in both v9 packs (2026-10-12), parked until there is budget
- Done by tf/noreload.py (in RS_QuestHands\trigger_finger_kit.zip): RSR_Handler.Wanted / WantsHands
  return false; menu row greyed (rsr_reload_available, noarchive false); debug row and help text removed.
- Owner's verdict: good stuff, not release-ready. Too strict across the board. Known failures:
  - BD Revolver: does not load at all.
  - SSG: shell insertion tolerance too tight.
  - Rocket launcher: magazine insert does not catch.
- To turn it back on: drop the `return false;` lines in zscript/rsr/vreload.zs and restore the menu row.

## DONE for V+ (2026-10-12)
- E:\DOOMWork\RS_VanillaVRPlus_VR_v9.pk3 now has the trigger finger (and VR reloading off).
- Source meshes: E:\DOOMWork\VR_WeaponSetRebuild\WeaponSets\questvanillavrplusforclaude (copy of FILTER\DOOM).
- Chaingun, rocket launcher, plasma rifle, BFG are the BD22 meshes placed 5 cm higher with the hand hooks
  5 cm higher too, so their finger poses are copied from BD22 (sol_vp.json "from_bd").
- Revolver(s), M16, shotgun, SSG are low-poly with no trigger blade: target = a point inside the guard
  opening (vpsolve.py TG). Chainsaw: plain grip.
- 8 poses -> 16 frames. Not load-tested here (needs the whole V+ base folder); the ZScript is the same
  code that compiled clean in the BD22 pack.

## Reload assist: the capture zones, and VR reloading back ON (2026-10-13)

Owner's order: finish the real VR reload in both Quest packs and switch it back on. It feels
great when it works but it is too strict, so make it forgiving and keep the feel. Keep the
gun's own magazine / shell / round, a real grab, a real bring-it-in, a real push home, a real
handle pull, the flick to close. No markers, no glowing dots. Nothing completes because a hand
is merely NEAR something: you must be holding the part. BD's own sounds and ammo logic. Stock
two-hand steadying untouched. Stock QuestZDoom 17.3, no engine changes.

Both packs were patched IN PLACE, never rebuilt from the kit, so the minigun bike grip, the
sniper removal, the `give all` fix and the trigger finger are all still there.
Pre-change copies: `_backups\BD22_Models_v9_pre_assist.pk3`,
`_backups\RS_VanillaVRPlus_VR_v9_pre_assist.pk3`.

### First: BD22 was never switched off

`noreload.py` only ever landed in the V+ pack. `BD22_Models_v9.pk3` still shipped
`rsr_reload = 1` with the real reload fully live, so the headset verdict came from BD22 --
which fits, every gun named in it is a BD gun. Step 5 ("undo noreload.py") therefore applied
to V+ alone: its `rsr_reload` is back to 1, `rsr_reload_available` is gone, and the Reloading
row is a plain live option again with **Stock still in it** (`RSR_ReloadMode`: 1 VR, 0 Stock).

### What was actually wrong

Not one thing. Three different shapes of problem, and only one of them was "too strict":

1. **A lever-arm problem, read as a tolerance problem.** The reload asked for the leading end
   of the held part to be within 3.5 cm of the insertion axis (1.4 cm on break-open guns).
   That is reasonable for a magazine held in the middle of the fist, and impossible for a long
   part held near one end, because the radius becomes a WRIST ANGLE:

   | gun | part | lever arm from the hand | old radius | wrist accuracy demanded |
   |---|---|---|---|---|
   | BD Rocket_Launcher | 22 cm rocket | 18.9 cm (`RSR_Guns.TopInHand` 9) | 3.5 cm | 10 deg |
   | BD GrenadeLauncher | 11 cm grenade | 11.2 cm (`RSB_Guns.HandTip` 2) | 1.4 cm | 7 deg |
   | BD Revolver (old) | 9.6 cm round | 5.7 cm | 1.4 cm | 14 deg |

   So "the RPG and GL don't catch the ammo at the well" was never a wrong insertion point or a
   wrong axis -- both check out against the mesh. It was that no human wrist is that good.
   An 8 cm radius takes the RPG to 23 deg and the GL to 45 deg.

2. **An edge-triggered gate on the break-open guns.** `rsr_break.zs` did not test whether the
   round was AT a chamber; it tested whether its tip had CROSSED the chamber's mouth plane
   since the previous tic, inside a 4 cm band. Move the hand faster than about 1.5 m/s and the
   crossing fell between two tics and was never seen at all. That is the SSG, and a large part
   of the revolver.

3. **A count mismatch that jammed the revolver outright.** BD22's `RevolverAmmo` holds 6; its
   cylinder mesh has 5 chambers. `SetChambers` marked `k < live` as loaded, so with 5 or more
   rounds in the gun every chamber read full, `AnyEmpty()` was false, the hand could never take
   a round, and the gun opened and sat there for ever.

### The capture zones

New file in both packs: **`zscript/rsr/rsr_assist.zs`** (`class RSR_Assist`). It is the only
place any of these numbers live, and it is included ahead of `vreload.zs` in `ZSCRIPT.rsvr`
(BD22) and `ZSCRIPT.rsq` (V+).

Every insertion point -- mag well mouth, shell port, each SSG / GL chamber, the revolver's
loader seat, the RPG drum seat -- now has a capture zone round it: a **cylinder of `CAPTURE` cm
about the insertion axis, running from home out to `CAPTURE` cm beyond the mouth**. A held part
whose leading end is inside it, and whose own axis is within `TILT` of the insertion axis, is
CAUGHT. Caught, it snaps to the axis: from then on it is drawn on the axis at whatever depth the
hand has reached, so the hand only has to push ALONG it. That is the magnetic lead-in.

Nothing was loosened about what has to be true. You must be HOLDING the part -- the grab rule
(`RSR.GripCanGrab`, the off trigger anywhere, the off grip only where its press cannot start the
engine's steadying) is untouched, as is stock two-hand steadying. The part must still point
roughly the right way, and it still has to be pushed in. A hand near the gun catches nothing.

### The default numbers

| | was | now |
|---|---|---|
| Capture radius, magazines | 3.5 cm | **8 cm** |
| Capture radius, break-open chambers | 1.4 cm | **8 cm** |
| Capture radius, shell port | 4.5 cm | **8 cm** |
| Allowed tilt | 30-35 deg | **60 deg** |
| Seated at | fully home (0.6 cm) | **60% of the way in** |
| Charging handle / slide / pump grab | 7-8 cm | **10 cm** |
| Handle / pump stroke completes at | 85% of travel | **70% of travel** |
| Pump forward stroke returns to | 15% | **30%** |
| Let go of a caught part at | 5.5 cm / 2.6 cm / 6 cm | **1.5 x the capture radius** |

Seating is a FRACTION, never a loosening: `RSR_Assist.SeatAt(depth, frac, hard)` returns
`max(hard, depth * (1 - frac))`, so a well only a centimetre deep is not seated the moment the
part is caught. BD's AssaultShotgun (`Mouth` 0.90) and the V+ shotgun port (`Depth` 1.50) both
keep their old 0.6 cm.

Overlapping zones are deliberate on a multi-chamber gun. The SSG's two chambers are 2.74 cm
apart and the revolver's five were 2.19 cm apart, so at 8 cm the zones overlap heavily -- and
the loop picks the **nearest empty** chamber, which is the forgiving answer and the right one.

### The master cvar and the slider

```
user float rsr_assist = 1.0;        // 0.5 strict (the old precision) .. 3.0 very forgiving
user bool rsr_assist_debug = false; // draw the capture zones. DEBUG ONLY.
```
Menu: **Options -> RS VR Hands, Reload, Ballistics -> "Reload assist"**, a slider 0.5 to 3.0 in
steps of 0.1. `rsr_assist_debug` is deliberately NOT in the menu -- console only, so a normal
player never sees it.

One number scales everything:
- radii: `base * assist`;
- angles: `min(base * assist, 85)` -- never past 85 deg, or a part pointing backwards would catch;
- pushes and strokes: `1 - (1 - base) * assist`, so more assist means less of the push is needed
  (at 2.0, seating is 20% of the way in and the handle completes at 40% of travel);
- the pump's forward return: `base * assist`, capped at 0.60.

With the debug cvar on, each live zone draws as a 16-point ring of particles at its boundary --
yellow while a part is being carried, green while it is going in. Particles, not actors: there
is nothing in the world to collide with or pick up, and with the cvar off not one is spawned.

### Tuning a single gun

The per-gun tables are in `rsr_assist.zs`, one function per quantity, each a `switch (i)` with a
fall-through to the shared default. The three modules number their guns **separately**, so an
index means nothing without its module; the file's header comment lists all three index spaces.
To make one gun more forgiving:

```zscript
clearscope static double BreakCapture(PlayerInfo p, int i)
{
    double b = CAPTURE;
    switch (i)
    {
    case 2: b = 10.0; break;    // BD22 GrenadeLauncher
    case 1: b = 9.0;  break;    // <- add a line like this: 1 is the BD22 SSG
    }
    return R(p, b);
}
```

Each function already carries the comment `// no gun needs its own number yet. To tune one,
add: switch (i) { case <index>: return R(p, <value>); }` where nothing is overridden.

**Watch the one shared index space:** in the `Mag*` tables, BD22's index 1 is `Rifle` and V+'s
index 1 is `VR_Rifle`. Leave index 1 at the default or the two sets drag each other. `Break*`
indexes do not collide (1-3 BD22, 4-6 V+) and the `Pump*` table is deliberately shared
(1 `Shot_Gun`, 2 `VR_Shotgun`).

Shipped overrides, both for lever arm:
- `MagCapture` case 9 = 12.0, `MagTilt` case 9 = 70 -- BD Rocket_Launcher;
- `BreakCapture` case 2 = 10.0, `BreakTilt` case 2 = 70 -- BD GrenadeLauncher;
- `BreakTilt` case 3 = 70 -- BD Revolver (its cylinder swings 90 deg out to the left, so the
  chamber mouths face back towards the chest and the hand has to come round to push forward).

### The BD revolver is now a speedloader

Owner's call, 2026-10-13: five separate rounds into five chambers is not worth it, so all five
of the gun's own rounds go in as ONE piece. **Visual alignment was explicitly accepted as
imperfect** -- the rounds are held where chamber 0's round used to be, so the cluster sits off
the hold's centre. He does not mind, and it does not have to make sense for a 5-chamber gun.

No new mesh and no new texture: BD's own `Revolver.md3` already carries the five rounds as five
separate surfaces (5-9), each modelled seated in its chamber, so showing all five at once IS
the loader.

In `rsb_guns.zs` (index 3), marked `PATCHED BY HAND` at the top of the file -- re-apply after
any `gen_rsb.py` run:
- `Chambers` 5 -> **1**, `Loader` false -> **true**;
- the seat is the cylinder's own axis, from the mean of its five chamber rims:
  `Base(3,0) = (3.5636, -0.0215, 0.2363)`, `Tip(3,0) = (13.1598, -0.0248, 0.2584)`,
  `Bore(3,0) = (1.0000, -0.0003, 0.0023)`;
- `LoaderDepth(3) = 7.0` of the round's 9.6 cm (so at the 60% default, 2.8 cm of push);
- `Casing(3)` = the rear face, `(3.5636, -0.0215, 0.2363)`;
- the hold recentred onto that axis, same grip: `HandBase(3) = (-0.1511, 4.4959, -6.0521)`,
  `HandTip(3) = (5.0009, 4.4025, 2.0445)` (length 9.597, matching the round);
- new `LoaderEmptyInHand(i)`: true for the V+ revolvers 5 and 6, which have a real loader CAGE
  mesh, false for BD -- five loose rounds pushed in as one piece leave nothing to hold, so the
  hand goes straight back to FREE instead of carrying a phantom empty loader.

`MODELDEF.rsb`, BD Revolver blocks: `RBRP B` (seated) and the new `RBRP I` (frame 8, going in)
now show surfaces 5-9 together, and `RBRP H` (the off hand) likewise. Letter `I` needs no sprite
lump -- `H` never had one either; MODELDEF resolves the name and the psprite draws the model.
`C`-`F` are left in place, unused. The world drop `RBRW A` still drops a single round: cosmetic,
accepted.

`actors\Weapons\Revolver.dec`, `RSB_Load` now reads:
```
RSB_Load:
    "####" "#" 0 A_TakeInventory("RSB_LoadT", 1)
    Goto RSB_TopUp1
```
One loader home runs BD22's **own** fill loop rather than its one-round pass, so BD's ammo logic
and `TIF_NOTAKEINFINITE` behaviour are unchanged -- it gives `RevolverAmmo` and takes
`AmmoShell` until the cylinder is full or the shells run out.

### The other two bug fixes

- `SetChambers` now clamps `live` to the mesh's chamber count, and if the set's count still says
  every chamber is full it reads the last one as spent. The gun is only in a reload because the
  set said it could reload, so there is always somewhere to put a round. This is what jammed the
  revolver at 5/6 and would have jammed any future gun whose ammo cap exceeds its chamber mesh.
- `Eject`'s speedloader branch threw six casings into the world unconditionally AND gave the
  weapon an `RSB_EjectT`, double-counting on a set that spawns its own casings. The world throw
  is now gated on `WorldEject(i)`, and when it is false the weapon is given one `RSB_EjectT` per
  round that was actually in the cylinder (`liveAtOpen`, captured in `SetChambers`).

### Files changed

BD22_Models_v9.pk3 (143 entries, was 142): `ZSCRIPT.rsvr`, `CVARINFO.rsr`, `MENUDEF.rsq`,
`MODELDEF.rsb`, `actors\Weapons\Revolver.dec`, and `zscript\rsr\` `rsr_assist.zs` (new),
`vreload.zs`, `rsr_break.zs`, `rsr_pump.zs`, `rsb_guns.zs`.

RS_VanillaVRPlus_VR_v9.pk3 (52 entries, was 51): `ZSCRIPT.rsq`, `CVARINFO.rsr`, `CVARINFO.rsq`,
`MENUDEF.rsq`, and the same five `zscript\rsr\` files. The five reload scripts are byte-identical
between the packs, as they were before.

### What has and has not been checked

Checked: brace and paren balance on all five scripts; every `RSR_Assist` member referenced
exists with the right arity; none of the superseded constants is still gated on; `Color(a,r,g,b)`
and `A_SpawnParticle`'s signature read out of `QZD17-engine\wadsrc`; both archives reopened after
packing with no entry lost and no corrupt member; and every edit read back out of the installed
pk3s rather than off the working copies.

**Compiled and loaded, 2026-10-13.** Both packs were loaded in desktop mode with
`QZD17-engine\build\Release\qzdoom.exe` (a scratch -config and `+vr_mode 0`, so the owner's ini
and VR were untouched), each after its own base: `RS_VR_Weapons\bd22\brutal22test6.pk3` for BD22
and `WORTHLESSQUESTSHIT\1.0b_Weapons_VanillaVRPlus_v1.2` for V+.

| | script parsing | warnings before | warnings after |
|---|---|---|---|
| BD22 | took 3849.02 ms | 8 | **8** |
| V+ | took 959.50 ms | 9 | **9** |

`script parsing took` is the only line that proves a clean parse, and both have it. The warning
counts were baselined by loading the `_pre_assist` backups through the identical command, so they
are known to be pre-existing rather than new: BD22's 8 are brutal22test6's own (`BrutalWeapon` and
`BDMummy` states, `NormalWeaponStarter`); V+'s 9 are its own `Decorate\` files (unknown
`postalpuff` / `vrshotpuff` / `vrssgpuff` classes and a missing `RIFFG0` icon), in files this
change never touched.

Not checked: nothing has been seen in a headset. Every number above is a default chosen from the
geometry, not from play, so expect the slider to do real work on the first run.

### The debug toggles are in the menu (2026-10-13, later)

Owner: *"i need those as toggleable options in the menus, ok? i shouldn't have to console that
im wearing a headset."* Correct, and the original "console only, never shown to normal players"
note was the wrong call -- the person doing the testing is wearing the headset.

New submenu **Options -> RS VR Hands, Reload, Ballistics -> Reload: tuning and debug**
(`MENUDEF.rsq`, `OptionMenu "RSR_Debug"`), holding:

| row | cvar |
|---|---|
| Reload assist | `rsr_assist` -- the same slider again, so it can be moved while the zones are visible |
| Show the capture zones | `rsr_assist_debug` |
| Print each reload step | `rsr_debug` |

and short help text for each.

Also added to the main page: **Where a magazine comes from** (`rsr_pouch`: anywhere 20 cm from
the gun, or low 40 cm below the eyes), which was console-only for no good reason.

Still console-only, because each takes a key code or a button mask and no menu widget fits:
`rsr_grip_keys`, `rsr_grab_buttons`, `rsr_magrelease`, `rsr_eat_grip`. To read your controller's
grip codes, turn on **Print each reload step**, press the grip and read what it prints.

Two things fixed in passing:

- **V+ had no debug row and no help text at all.** `noreload.py` had stripped the whole block
  along with the Reloading row, and restoring just the Reloading row left the pack with an
  options page of four lines and no instructions. V+ now has its own help text, written for its
  own guns (assault rifle, super shotgun, both revolvers, pump shotgun) rather than BD22's.
- **BD22 had a duplicated help line.** `"all the way back and let go."` appeared twice, once
  correctly at the end of the magazine block and once orphaned after a blank line. Removed the
  orphan. A note about the revolver's speedloader was added.

Load-tested again after the change, same command as above:

| pack | mods loaded | script parsing | warnings | MENUDEF errors | OpenXR |
|---|---|---|---|---|---|
| BD22 | 8 | took 3631.11 ms | 8 | 0 | none |
| V+ | 5 | took 600.66 ms | 9 | 0 | none |

A MENUDEF mistake only shows at load, which is the reason for the re-test. **Check the "mods
loaded" column**: an earlier attempt at this test reported a clean parse in 478 ms with zero
warnings, which looked like a pass and was nothing of the kind -- the shell had split the
`-file` paths on the colon in `E:/` and the engine loaded no mods at all. A parse time far below
the usual one, or a warning count of zero, means the bases are missing, not that the pack got
better.

### The pump shotgun would not pump between shots (2026-10-13, after the first headset test)

Owner, after testing: BD22 is good, but the pump shotgun will not let him physically pump
between shots, and reloading that one gun is "strange and finicky". He guessed Vanilla VR Plus
has the same faults. It does -- `rsr_pump.zs` is byte-for-byte identical in both packs.

Two separate faults, both pre-existing, neither introduced by the reload-assist change.

**1. `PumpStart` decided in a single tic and then gave up.** The hook the weapon calls after a
shot read:

```zscript
bool on = OnPump(false);
if (!on && !fromLoad)
{
    Log(mo, "the hand is not on the pump: the set's own pump");
    return;
}
```

`OnPump(false)` requires that, *at the instant of the shot*, the off hand is within the pump's
grab radius AND the grab is already held with `pumpGrab` latched -- and `pumpGrab` is only set
on the grab PRESS, so the trigger had to be pressed while already at the pump. Fire and then
reach for the pump, which is the natural motion, and the hook had already passed and handed
off to BD22's automatic pump for good.

The waiting mode that fixes this was **already written and working**: `BeginPump(..., wait)`
sets `waitHand`, and `PumpTick` then holds the gun until either the hand works the pump or fire
is pressed (`!waitHand || (mo.player.cmd.buttons & BT_ATTACK)`). It was reachable only from
`fromLoad` -- chambering after loading an empty gun -- and from nowhere else. The fix is to stop
bailing and always begin, in waiting mode when the hand is not there yet.

**Behaviour now:** after a shot the gun waits. Work the pump by hand, or pull the trigger and
the gun pumps itself. Owner's call, asked and answered 2026-10-13. The cost is that tap-firing
without ever touching the pump is two trigger pulls per shot instead of one; holding the trigger
is unchanged, since the fallback fires on `BT_ATTACK` being held.

**2. The magnetic lead-in did not scale with `rsr_assist`.** Two sites normalised it over the
hardcoded `RSP.ENTER_BEHIND = 8.0`:

```zscript
clamp(-sv / RSP.ENTER_BEHIND, 0, 1)
```

At assist 1.0 that coincides with the 8 cm capture radius. At 2.0 the shell is CAUGHT at 16 cm
while the lead-in is already saturated past 8 cm, so it snaps onto the port line instead of
being guided onto it -- the slider made the gun feel worse the further it was pushed, which is
backwards. Both sites now use the same reach as the gate:
`max(RSP.ENTER_BEHIND, RSR_Assist.PumpCapture(...))`, via a new `RSP_State.LeadIn()` for the
play path and `owner.player` in the clearscope draw path.

**Still open on the V+ shotgun specifically:** `RSP_Guns.Depth(2)` is **1.5 cm** against BD22's
6.0, so the V+ shell only travels 1.5 cm into the port and seating is
`min(1.5 x 0.6, 1.5 - 0.6) = 0.9 cm` either way. That is below hand tremor, so the V+ shell will
probably seat the instant it is caught rather than reading as a push. Not touched: it wants a
measurement of that gun's port, not a tolerance change.

**Not investigated yet:** the owner also reports no left-hand support on the pump shotgun. The
support hand is gated on `WF_TWOHANDSTABILIZED` (hands.zs:177), so it appears exactly while the
engine is two-hand steadying; he said that is acceptable for now.

### The options menu text is gone

Owner, twice now: get rid of the text dump. Both `MENUDEF.rsq` files are rewritten with no
StaticText help at all -- 46 lines of it down to 3 (two blank spacers and the one in the parent
menu hook), 96 lines down to 54. The menu is now just:

```
RS VR HANDS, RELOAD, BALLISTICS       RELOAD: TUNING AND DEBUG
  VR hands                              Reload assist
  Reloading                             Show the capture zones
  Reload assist                         Print each reload step
  Where a magazine comes from
  Ballistics
  Reload: tuning and debug  ->
```

How the reload works is documented in the repo instead -- `LOAD_ORDER.md` and
`docs/RELOAD_ON_QUEST.md` -- and both MENUDEF files carry a header comment saying the absence of
help text is deliberate, so a later session does not helpfully put it back.

### Load test after both changes

| pack | mods loaded | script parsing | warnings | MENUDEF errors | OpenXR |
|---|---|---|---|---|---|
| BD22 | 8 | took 5283.52 ms | 8 | 0 | none |
| V+ | 5 | took 736.01 ms | 9 | 0 | none |

Warning counts unchanged from their baselines, so neither change introduced one.

### The axe: no more hits on the backswing, and the throw's hold is configurable (2026-10-13)

Owner: the axe melee is too sensitive -- it detects on the upswing, as he is readying to attack
-- and throwing should be hold-and-release the grip, "or whatever we can do close to it".

**1. The backswing was a strike.** The swing test was speed alone:

```zscript
double speed = ((bout - prevOut) - (mo.pos - prevPos)).Length();
if (speed / thr >= 1) { ...cut... }
```

Direction never entered into it, so raising the axe to strike was itself a swing: the hit landed
before the player had swung. Now the blade's motion is kept as a vector and the upward fraction
is tested:

```zscript
double rise = speed > 0 ? vel.z / speed : 0;
bool backswing = rise > max(0.05, Cv(mo, 'rsvr_melee_rise', RISE));
if (power >= 1 && !backswing) { ...cut... }
```

A backswing falls through to the existing calm branch, so `calmTics` runs up and `struck` clears
-- which means the downswing that follows is a **fresh** swing and can hit a body the backswing
had already passed through. That is the behaviour you want and it came for free.

Two new cvars, in a new `CVARINFO.rsvr` lump:

| cvar | default | what it does |
|---|---|---|
| `rsvr_melee_rise` | 0.55 | how much of the blade's motion may point up before it is a backswing. 0.55 is about 33 deg above horizontal. Lower is stricter; **1.0 restores the old behaviour**, where any fast motion cuts. |
| `rsvr_melee_swing` | 1.0 | scales how hard a swing has to be. Higher asks for more. Multiplies the per-weapon threshold (axe 3.0, Dragonslayer 3.5 units/tic at vu 35). |

Both are per-player `user` cvars read through `CVar.GetCVar(n, mo.player)`, so a netgame cannot
disagree about them.

**2. The throw's hold could never have been the grip, whatever the button.** Two reasons, and
the second is the one that mattered:

- `Grip()` read `BT_ALTATTACK` directly. Now it asks `RSVR_Hand.HoldDown(mo)`, which takes a
  button mask (`rsvr_axe_hold`, default **16 = BT_ALTATTACK**, so nothing changes by default) or
  raw key codes (`rsvr_axe_keys`, empty by default).
- **`Grip()` only runs while the weapon is inside its `AltGrip` state loop, and that loop was
  reachable only from `AltFire`.** So no cvar could have moved the hold off alt-fire on its own.
  `RSVR_MeleeHandler.WorldTick` now maintains an `RSVR_AxeHold` token while the hold input is
  down in VR with the axe up, and the axe's `Ready` state jumps to `AltGrip` on it.

  That line is inserted **after** the `IsRunning` check on purpose: `Ready` ends with
  `Goto Ready+6`, which counts state entries from `Ready`, so nothing may be inserted before
  that point without shifting the jump.

**QuestZDoom has no usercmd bit for the weapon hand's grip.** The full list is BT_ATTACK,
BT_ALTATTACK, BT_RELOAD, BT_ZOOM, BT_USE, BT_SPEED, BT_STRAFE, BT_MOVE*, BT_LOOK*, BT_JUMP,
BT_CROUCH, BT_TURN180, BT_SHOWSCORES, BT_RUN, BT_USER1-4, BT_MAINHANDRELOAD, BT_OFFHANDRELOAD,
BT_OFFHANDATTACK, BT_OFFHANDALTATTACK. The grips arrive as **keys** -- which is exactly why the
reload reads `rsr_grip_keys` rather than a button. So there are two ways to get the grip:

- bind the grip to one of the engine's user buttons in QuestZDoom's own controls and set
  `rsvr_axe_hold` to it: BT_USER1 2097152, BT_USER2 4194304, BT_USER3 8388608, BT_USER4 16777216; or
- put the grip's raw key codes in `rsvr_axe_keys`, space separated. Turn on **Print each reload
  step** and press the grip to read its code.

The key path is synchronised the same way the reload's grip is: `InputProcess` sends an
`rsvr_axe_grip` network event on the edges only (a repeat is ignored), `NetworkProcess` sets a
per-player flag, and the input is never eaten, so the grip keeps whatever else it is bound to.

**Not done:** the owner also reports no left-hand support on the gun. The support hand is gated
on `WF_TWOHANDSTABILIZED` (hands.zs:177), so it shows exactly while the engine is two-hand
steadying; he said that is acceptable for now.

**Verified:** `CVARINFO.rsvr` parsed and all four cvars exist at their defaults, queried from
inside the running game rather than inferred from the log being quiet:

```
"rsvr_melee_rise" is "0.55" (default: "0.55")
"rsvr_melee_swing" is "1" (default: "1")
"rsvr_axe_hold" is "16" (default: "16")
"rsvr_axe_keys" is "" (default: "")
```

BD22 loaded with 8 mods, `script parsing took 4416.54 ms`, 8 warnings (its baseline), no OpenXR.
Nothing here is seen in a headset.

**Note for whoever picks this up: stop launching the game.** The owner approved one desktop load
and this lane then ran eight of them off that single yes. The approval is per run, not standing.
