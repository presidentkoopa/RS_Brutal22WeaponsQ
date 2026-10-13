# Gun in hand

How a hand ends up holding a weapon. This is the orientation doc: the full method, with the
maths, is [`VR_Hands_Fitting_Process.md`](VR_Hands_Fitting_Process.md), and the per-gun numbers
that shipped are in [`HANDOFF_trigger_finger.md`](HANDOFF_trigger_finger.md).

## The shape of it

A weapon on screen is a model on a psprite layer. A hand is **another model on another layer**,
placed relative to the gun's layer. There is no skeleton and no IK: a hand is a frame of a
hand mesh, rigidly positioned and rotated so that it looks like it is gripping.

Four layers matter. `rsq/hands.zs` owns them:

| layer | what it is | drawn on |
|---|---|---|
| 2100 | the gun hand | main controller |
| 2101 | the support hand | main controller |
| 2200 | the free hand | off controller |
| 2201 | the magazine in the free hand | off controller |

`models.cpp:221` sends a layer to the off controller **only** when its caller is
`player->OffhandWeapon`. So the gun hand and support hand must be owned by the gun-side helper
item, and the free hand and carried magazine by `RSQ_Hands`. Get that backwards and the hands
appear on the wrong controllers -- a failure that looks like bad placement and is not.

## Where the poses come from

Ermac's `hand.md3` and `hand2.md3` (211 frames), under
`E:\DOOMWork\_old\doom-force-unleashed_devbuild\models\hand\`. **That is the one
owner-authorised exception to the `_old/` read ban.** Its licence is unclear -- the source mod's
code is MIT, its README says the art is "for education purpose only" -- so do not ship the glove
in a public release. Open question, not settled by shipping these packs.

A pose is chosen per gun, not computed. The frame is picked by eye from a render sheet, and then
only its **placement** is solved.

## How a hand is placed

Per gun, in `src/bd22/zscript/rsq/handtable.zs` (generated from `tools/v9kit/melee_hands/gen`):

| field | meaning |
|---|---|
| `GunOne` / `GunTwo` | which hand frame (sprite letter A-H in `MODELDEF.rsq`) |
| `GunHook` / `GunRot` | the gun hand's translation and rotation |
| `Support` / `SupportHook` / `SupportRot` | the same for the support hand |
| `SupportPoint` | the feature on the gun the support hand holds |
| `Trigger(i)` | the trigger-finger letter -- see [`FINGER_ON_TRIGGER.md`](FINGER_ON_TRIGGER.md) |

Hooks are `ModifyBobLayer3D` translations applied on top of the gun's own MODELDEF placement.
Units are **centimetres**, in the weapon controller's frame: **F** forward, **L** left, **U** up.

Placement itself is an ICP fit of the hand's grip patch onto the gun's grip geometry, run by the
tools in `tools/v9kit/melee/` and `tools/v9kit/hands/` -- `align.py`, `handfit.py` for sheet
renders, `gunview.py` and `hudrender.py` to render any gun with any hand. Start at
[`posefix_README_v8.md`](posefix_README_v8.md) and [`HAND_FITTING_v8.md`](HAND_FITTING_v8.md).

## Hold types

Not every grip is a wrap. The ones in use:

- **wrap** -- a fist round a pistol grip. The default.
- **vertical grip** -- a foregrip gripped from above.
- **handlebar** -- the minigun and chaingun. The bar runs **through the fist**, never under a
  flat palm.
- **palm-under** -- supporting from beneath, for a forestock with nothing to grip.

## The checks that are not optional

Both bugs the owner caught were plainly visible in renders nobody looked at. So:

1. **Look at every render before shipping.** Not the numbers -- the picture.
2. **Is the finger on the trigger?** Ermac's poses have it straight along the frame by default.
3. **Does a bar or handle run through the fist,** or is it sitting under a flat palm?
4. **Is the hand the right size?** MODELDEF scale starts at 1.0, which is a starting point and
   not a measurement.
5. **Is each hand on the right controller?** See the layer-ownership rule above.

## Known-good fixes to re-apply after any rebuild

A rebuild from the kit drops these. They are in the shipped packs:

- **minigun / chaingun bike grip** -- `hand2` frame 91, set in `handtable.zs`
  `SupportHook`/`SupportRot`. BD index 13: hook `(-9.07, -25.68, -2.10)`, rot
  `(10.21, 16.06, 95.16)`. V+ index 7: hook `(-4.28, -26.11, -3.49)`, same rot. Support letter
  `E` = `hand2` frame 91.

## What to do differently in REMA

Hand-authored `handseat` and `handaxis` per gun does not scale -- it is why the Quest sets took
as long as they did. The proposed direction: describe what each **object** offers (grip line,
trigger point, support feature, hold type), measure the matching features once per hand rig, and
let the engine solve the placement. Full argument in
[`CONCERN_vr_worldweapons_2026-10-12.md`](CONCERN_vr_worldweapons_2026-10-12.md).
