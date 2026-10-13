# Changelog

Newest first. Dates are when the change landed in a shipped pack.

## 2026-10-13 -- reload assist, and VR reloading back ON

- **New `zscript/rsr/rsr_assist.zs`**: capture zones round every insertion point. 8 cm radius
  (was 3.5 cm on magazines, 1.4 cm on break-open chambers), 60 deg tilt (was 30-35), seated at
  60% of the way in (was fully home), handles grab at 10 cm and complete at 70% of travel.
  A caught part snaps to the insertion axis and is then pushed along it.
- **`rsr_assist` 0.5-3.0** (default 1.0) scales every radius and tolerance, with a slider in
  the options menu. **`rsr_assist_debug`** draws the zones as particle rings -- console only.
- **Fixed: the break-open entry gate was edge-triggered.** It required the round's tip to cross
  the chamber mouth plane within a single tic, so a hand moving faster than about 1.5 m/s was
  never caught. Now a zone test.
- **Fixed: the revolver jammed outright.** `RevolverAmmo` holds 6, the cylinder mesh has 5
  chambers; at 5+ rounds every chamber read full, `AnyEmpty()` was false and the hand could never
  take a round. `SetChambers` now clamps to the mesh count.
- **Fixed: double casings** on a speedloader eject -- the world throw is now gated on
  `WorldEject`.
- **BD revolver is now a speedloader**: all five of its own rounds as one piece down the cylinder
  axis. No new mesh or texture. Visual alignment knowingly imperfect, accepted by the owner.
- **V+ reloading switched back on** (`rsr_reload` 0 -> 1, the greyed menu row restored). Note
  that **BD22 was never switched off** -- `noreload.py` only ever landed in the V+ pack.
- Both packs parse clean: BD22 3849.02 ms / 8 warnings, V+ 959.50 ms / 9 warnings, both counts
  identical to before the change.

Detail: the "Reload assist" section of [`docs/HANDOFF_trigger_finger.md`](docs/HANDOFF_trigger_finger.md).

## 2026-10-12 -- the trigger finger

- The gun hand's index finger sits on each gun's trigger and squeezes on fire. 17 poses / 34 new
  `hand.md3` frames for BD22; 8 poses / 16 frames for V+.
- **VR reloading switched off in the V+ pack** -- "good stuff, not release-ready. Too strict."
  Undone 2026-10-13 above.
- **Sniper rifle (HK416) removed from BD22**: the model may not be usable. `RSQ_NoSniper`
  replaces Sniper -> Rifle, PuristSniper -> PuristRifle, SniperAmmo -> Clip2.
- **`give all` / `idkfa` now gives every modeled BD22 gun.** Two causes: the
  `+WEAPON.CHEATNOTWEAPON` flag on four actors, and four weapons being `replaces`-d, which
  `give all` skips.

Detail: [`docs/FINGER_ON_TRIGGER.md`](docs/FINGER_ON_TRIGGER.md).

## 2026-10-11 -- minigun support hand

- The minigun / chaingun support hand was a flat palm under the handlebar. Now `hand2` frame 91,
  a bike grip, with the bar **through** the fist.

## 2026-10-10 -- v8 packs shipped

- Posed hands on every gun, reload stock-or-immersive, ballistics stock-or-ours, all switchable
  in the options menu.
- The V+ pack also carries a crash fix for that set: with default weapon switching, switching
  away from the M16 or the revolvers overflows the stack.

## 2026-10-03 -- the v8 proving plan

- Four engine claims proved, one go/no-go. Kept for its engine citations:
  [`docs/v8_PROVING_PLAN.md`](docs/v8_PROVING_PLAN.md).

---

# Open items

Nothing below is waiting on code; all of it is waiting on a headset or a decision.

- **No headset test of anything.** Every reload tolerance is a default derived from mesh
  geometry, not from play. Expect the **Reload assist** slider to do real work on the first run.
- **The glove licence is unresolved.** The source mod's code is MIT; its README says the art is
  "for education purpose only". Fine in a private repo, not settled for any public release.
- **Mirrored-hand winding.** The engine mirrors the left controller's model with
  `scale(-1,1,1)` *after* MODELDEF scale signs decide culling, so the mirrored hand may need its
  own treatment. Chirality is resolved; winding is not.
- **The dropped speedloader is a single round.** Let go of the BD revolver's loader mid-insert and
  one round falls, not five. Cosmetic, accepted.
- **The v8 `qh_*` generation is still in the tree** at `src/v8_questhands/`, kept for its
  reasoning. Nothing in the shipped packs references it.

## The traps that have cost the most

1. **Look at every render before shipping.** Both bugs the owner caught -- the finger off the
   trigger, the flat palm on the handlebar -- were plainly visible in renders nobody opened.
2. **Patch the shipped pack; never rebuild from the kit.** A rebuild drops the minigun grip, the
   sniper removal, the `give all` fix and the trigger finger. Keep every fix as a source patch.
3. **One session per job, no agent swarms.** Parallel agents re-learning the same code burned
   most of a week's budget.
4. **`+vr_mode 0`, not `-config`,** is what keeps a desktop test out of the headset.
5. **`script parsing took` is the only proof of a clean parse.**
6. **A capture radius is a wrist angle.** Divide by the lever arm from the hand before calling a
   tolerance generous. See [`docs/RELOAD_ON_QUEST.md`](docs/RELOAD_ON_QUEST.md).
