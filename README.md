# RS_QuestHands

Hands and physical reload for **stock QuestZDoom 17.x**. No engine changes.

Target engine: `qzd17.3` = `9afc750917bf54870f2d16b7ba0d00f2b77e6fb5` (GZDoom 4.14.3 base).

- Plan and build order: `E:/DOOMWork/_reports/QUEST_RELOAD_DIAGNOSIS_2026-10-02.md`
- Source audits: `E:/DOOMWork/_reports/qzd17_stock_audit_2026-10-02/`

## Status

**BOTH QUEST PACKS ARE DONE AND SHIPPED (2026-10-10).** Only a headset test is
outstanding; nothing below is waiting on code.

| pack | file | built |
|---|---|---|
| BD22 hands, reload and ballistics | `E:\DOOMWork\BD22_Models_v8.pk3` | 2026-10-10 18:44 |
| Vanilla VR Plus add-on | `E:\DOOMWork\VanillaVRPlus_VR.pk3` | 2026-10-10 19:45 |

Posed hands on every gun. Reload stock or immersive, ballistics stock or ours,
both switchable in the options menu. The Vanilla VR Plus pack also carries a fix
for a crash in that set: with default weapon switching, switching away from the
M16 or the revolvers overflows the stack. **Never load the two packs together.**

Load orders: `brutal22test6.pk3` then the BD22 pack; or Doom/Doom 2, then the
owner's `1.0b_Weapons_VanillaVRPlus_v1.2` set, then the Vanilla VR Plus pack.

Sources for both are under `tools/posefix/` — start with its `README.md` and
`hands/HAND_FITTING.md`; the Vanilla VR Plus half is in `tools/posefix/vplus/`.

**The rest of this file is the ORIGINAL STAGED PROVING PLAN, written 2026-10-03,
and it is kept for its engine citations, not as a statement of what is left.**
Every claim below cites the engine file and line it rests on, and that is still
worth having. The step numbering is historical: step 1 proved the four claims,
and the reload that step 2 described shipped in both packs above.

This pack is separate from `RS_VR_Reload` on purpose: that one is built on
`level.HandPos`, `SetModelJoint` and `SetModelFlag`, which are UZDXREMA engine
additions and do not exist in stock QZD. It cannot run on this target.

## What step 1 is for

Four claims, one go/no-go:

1. A `ModifyBobLayer3D` override on **our** off-hand weapon is called for layers
   owned by **our** helper item — `hw_weapon.cpp:332` and `:941-951`
2. The axis and unit convention — X right, Y up, Z back toward the player,
   1 unit = 1 cm × MODELDEF scale
3. Four model layers drawing together on Quest
4. Which controller each lands on — `models.cpp:221`

## How to try it

1. Load the pack.
2. Open **Options → Quest Hands** and run **Baseline**. Do this first.
   `vr_weaponScale` and `vr_3dweaponOffset*` live inside the weapon transform
   (`models.cpp:251`, `:277`), so anything you have set moves every hand with it
   and makes the sliders meaningless.
3. Console: `qh_report`. It prints which of the four layers exist, who owns each,
   whether `bAddBob` is set, the metric-corrected hand separation, and the
   steadying state.
   - If `OffhandWeapon : none`, stop — the hook is not being called at all
     (`hw_weapon.cpp:941` finds `w.weapon` null) and nothing else will work.
4. Slide the hands into place and tell me what you see.

## Layout

| File | What it is |
|---|---|
| `zscript/qh_metric.zs` | The metric distance helper. Read its header before touching any distance test. |
| `zscript/qh_hands.zs` | `QH_Hands` (off-hand weapon, carries the hook), `QH_GunSide` (helper item), the steadying guard. |
| `zscript/qh_testgun.zs` | `QH_TestGun`, and `QH_Boot` which hands out the kit and prints the report. |
| `MODELDEF.txt` | Four blocks: two keyed to `QH_Hands`, two to `QH_GunSide`. |
| `CVARINFO.txt` | Every placement number, as a slider. |
| `MENUDEF.txt` | Options → Quest Hands. |
| `KEYCONF.txt` | `qh_baseline`, `qh_baseline_show`, `qh_report`. |
| `sprites/` | Six 1×1 transparent placeholder lumps. MODELDEF keys on sprite+frame, so each layer needs one; the model replaces it. |
| `tools/make_placeholder_sprites.py` | Regenerates those lumps. |
| `models/` | Rusted Legacy hands, MIT per `LICENSE_RustedLegacy_MIT.txt`. |

## The two things most likely to be wrong

Both are mine to fix, not yours to work around.

**Layer ownership.** `models.cpp:221` sends a layer to the off controller *only*
if its caller is `player->OffhandWeapon`. So the free hand and carried magazine
must be owned by `QH_Hands`, and the gun hand and support hand by `QH_GunSide`.
Get that backwards and hands appear on the wrong controllers. `qh_report` prints
the owner of each layer so this is visible rather than guessed at.

**Scale.** `MODELDEF` scale is `1.0` across the board, which is a starting point
and not a measurement. If the hands come out wildly wrong-sized, that is this
and not the hook.

## Netplay

Quest has no multiplayer today. The pack is written to survive its forthcoming
update anyway, because the three things that break a mod in a netgame are all
cheap to get right now and expensive to retrofit.

**Cvar scope follows the engine's own ui/play split.** A cvar read in `play`
decides something the simulation does, so every machine must agree on it:
`qh_enhanced`, `qh_debris_scale`, `qh_fetch_m`, `qh_insert_m`, `qh_rack_m`,
`qh_rack_m`, `qh_stale_latch_m` and `qh_shells_per_insert` are **server**. A
reload that releases at 0.35 m for one player and 0.20 m for another is a
desync, not a preference. Everything read only in the `ui` hook — all the hand
and magazine placement — stays **user**, because it moves pixels on one screen
and forcing those to match would be the worse bug.

**Hand gestures are detected locally and decided over the net.** `AttackPos` and
`OffhandPos` are per-client VR poses that are never sent over the wire; stock
QZD already desyncs when a VR player aims by hand. So the gesture test is
advisory and runs only on the owning client, which then sends a `qh_rel`
netevent. Every machine receives that identically, and it is the only thing that
touches `psp.Tics`, poses or haptics. `consoleplayer` appears in exactly one
place, to ask "are these my hands" — the gameplay decision still travels by
netevent.

**Debris RNG is safe because its gates are server cvars.** Every machine reaches
the spawn on the same shots and draws in the same order. Had `qh_enhanced` been
a user cvar, a player who turned debris off would stop consuming draws the
others still consumed and the streams would walk apart. The named `[qhb]` stream
also keeps those draws out of every other mod's sequence.

## Uncalibrated

- `MODELDEF` scale and every placement offset.
- Which frame of `hand2.md3` is the grip pose, and of `ammo_hand.md3` the
  magazine pose, is a headset call. Both are frame 0 for now.
- Mirrored-hand winding. The engine mirrors the physical left controller's model
  with a plain `scale(-1,1,1)` at `hw_vrmodes.cpp:469`, applied *after*
  `models.cpp:279-281` decides culling from the MODELDEF scale signs, so the
  mirrored hand may need its own treatment. Chirality itself is resolved in the
  plan; this is winding.
- The glove licence. The source mod's code is MIT; its README says the art is
  "for education purpose only". Open question, not settled by shipping this.

## What came next -- DONE, 2026-10-10

**This section described step 2, the reload with pauses, as the work ahead. It
shipped.** Both packs carry the reload, and Vanilla VR Plus went from "the thing
step 2 will need" to a shipped add-on of its own. Kept because the read-only
warning below still stands and still matters.

The set it reads from, which is **read-only** and sits in the live play rotation:

```
D:\SteamLibrary\steamapps\Common\DooM VR\__CurrentRotationDONOTDELETE\1.0b_Weapons_VanillaVRPlus_v1.2\
```

That sits in the live play rotation and is **read-only** — read
`Modeldef.Doom.Weapons.def` and `Models/` for class names and frames, never
write there.
