# Reloading on Quest

A physical VR reload: the gun's own magazine, shell or round, a real grab, a real bring-it-in, a
real push home, a real handle pull, the flick to close. Stock QuestZDoom 17.3, no engine changes.

**On by default in both packs** as of 2026-10-13, with **Stock** still available in the menu.
Every number and the full change record: the "Reload assist" section of
[`HANDOFF_trigger_finger.md`](HANDOFF_trigger_finger.md). A survey of how each gun's own reload
works is [`RELOAD_SURVEY.md`](RELOAD_SURVEY.md).

## The rules it is built to

These are the owner's, and they are not negotiable:

- The gun's **own** magazine, shell or round -- its mesh, its surface. Never a stand-in.
- **No markers, no glowing dots.**
- **Nothing completes because a hand is near something.** You must be *holding* the part.
- The set's **own** sounds and **own** ammo logic. We move the ammo through the weapon's own
  states, never by hand.
- **Stock two-hand steadying untouched.**

## Three modules

| file | covers | guns |
|---|---|---|
| `zscript/rsr/vreload.zs` | magazines, drums, cells, and the charging handle | BD22: Rifle, BrutalPistol, BrutalSMG, MP40, AssaultShotgun, RailGun, Plasma_Gun, Sniper, Rocket_Launcher. V+: VR_Rifle |
| `zscript/rsr/rsr_break.zs` | break-open guns and revolvers | BD22: SSG, GrenadeLauncher, Revolver. V+: VR_SuperShotgun, VR_Revolver, VR_Revolver2 |
| `zscript/rsr/rsr_pump.zs` | hand-fed shells and a hand-worked pump | BD22 Shot_Gun, V+ VR_Shotgun |
| `zscript/rsr/rsr_assist.zs` | **the capture zones.** All three modules read it | all |

Per-gun geometry sits in generated tables -- `rsr_guns.bd.zs`, `rsr_guns.vp.zs`, `rsb_guns.zs`,
`rsr_pump_guns.zs` -- all in centimetres in the weapon controller's frame (F forward, L left,
U up).

## How a reload runs

The weapon's own `Reload` state reaches `RSR_Start` **after all of its own checks**, so the set
decides whether a reload is legal and we only take over the performance. The gun then sits in a
`RSR_Wait` state giving `RSR_Tick` every tic, and the script drives phases:

```
DROP -> EMPTY -> CARRY -> INSERT -> SEATED -> CHARGE -> PULL -> RELEASED -> DONE
```

At `SEATED` the weapon runs the set's own fill loop; at `DONE`, the set's own end of a reload.
Break-open guns use `OPENING / OPEN / CLOSING / DONE` with a separate hand state machine, and
close on a **flick** of the gun hand about the hinge or an off-hand push.

### The input rule

Deliberately narrow, so stock steadying keeps working:

- the off **trigger** (`rsr_grab_buttons`, `BT_OFFHANDATTACK`) grabs **anywhere**;
- the off **grip** grabs only where its press *cannot* start the engine's steadying -- the
  controllers at least 50 cm apart, or `vr_two_handed_weapons 0` (read, never written);
- a steadied grip (`WF_TWOHANDSTABILIZED`) is **never** a grab.

Nothing here writes `vr_two_handed_weapons`.

## The capture zones

Every insertion point -- mag well mouth, shell port, each SSG/GL chamber, the revolver's loader
seat, the RPG drum seat -- has a **capture zone**: a cylinder of `CAPTURE` cm about the insertion
axis, running from home out to `CAPTURE` cm beyond the mouth. A held part whose leading end is
inside it, and whose own axis is within `TILT` of the insertion axis, is **caught**.

Caught, it **snaps to the axis**: from then on it is drawn on the axis at whatever depth the hand
has reached, so the hand only has to push **along** it. That is the magnetic lead-in.

### Defaults

| | before 2026-10-13 | now |
|---|---|---|
| capture radius, magazines | 3.5 cm | **8 cm** |
| capture radius, break-open chambers | 1.4 cm | **8 cm** |
| capture radius, shell port | 4.5 cm | **8 cm** |
| allowed tilt | 30-35 deg | **60 deg** |
| seated at | fully home (0.6 cm) | **60% of the way in** |
| handle / slide / pump grab | 7-8 cm | **10 cm** |
| stroke completes at | 85% of travel | **70% of travel** |
| let go of a caught part at | 5.5 / 2.6 / 6 cm | **1.5x the capture radius** |

Seating is a fraction and never a loosening: `RSR_Assist.SeatAt(depth, frac, hard)` returns
`max(hard, depth * (1 - frac))`, so a well a centimetre deep is not seated the moment the part is
caught.

Overlapping zones on a multi-chamber gun are **intended**. The loop picks the nearest empty
chamber, which is the forgiving answer and the right one. Do not shrink a radius to keep zones
disjoint.

### The slider

```
rsr_assist        0.5 .. 3.0, default 1.0   Options -> RS VR Hands, Reload, Ballistics
rsr_assist_debug  off by default. Console only -- never shown to a normal player.
```

One number scales everything: radii `base * assist`; angles `min(base * assist, 85)`; pushes and
strokes `1 - (1 - base) * assist`, so more assist means less of the push is needed.

With `rsr_assist_debug 1`, each live zone draws as a 16-point particle ring at its boundary --
yellow while carrying, green while inserting. Particles, not actors: nothing to collide with, and
with the cvar off not one is spawned. This is the only thing in the whole system that draws a
hint, and it exists for tuning, not for play.

### Tuning one gun

Per-gun tables are in `rsr_assist.zs`, one function per quantity, each a `switch (i)` falling
through to the shared default. **The three modules number their guns separately** -- an index
means nothing without its module, and the file header lists all three index spaces. In the `Mag*`
tables, BD22 index 1 is `Rifle` and V+ index 1 is `VR_Rifle`, so leave index 1 at the default or
the two sets drag each other.

## The lesson worth carrying: a radius is a wrist angle

All three guns the owner called impossible had **correct** insertion points and axes. The
difficulty was never the centimetres -- it was `atan(radius / lever_arm)`, where the lever arm is
the distance from the controller to the part's leading end:

| gun | part | lever arm | old radius | wrist accuracy demanded |
|---|---|---|---|---|
| BD Rocket_Launcher | 22 cm rocket, held near its tail | 18.9 cm | 3.5 cm | **10 deg** |
| BD GrenadeLauncher | 11 cm grenade | 11.2 cm | 1.4 cm | **7 deg** |
| BD Revolver | 9.6 cm round | 5.7 cm | 1.4 cm | **14 deg** |

A magazine held in the middle of the fist has a lever arm of about 4 cm, so the same 3.5 cm
radius is a comfortable 40 degrees. That is why one number felt fine on rifles and impossible on
launchers -- and why a long part wants **more** radius than a short one, not the same.

**So: when a part "doesn't catch", measure the lever arm before touching the insertion point.**

## Two bugs that were not strictness

- **An edge-triggered gate** on the break-open guns. `rsr_break.zs` never asked whether the round
  was *at* a chamber; it asked whether its tip had *crossed* the mouth plane since the previous
  tic, inside a 4 cm band. Faster than ~1.5 m/s and the crossing fell between tics and was never
  seen. That was the SSG, and much of the revolver.
- **A count mismatch** that jammed the revolver outright. `RevolverAmmo` holds 6; the cylinder
  mesh has 5 chambers. With 5 or more rounds every chamber read full, `AnyEmpty()` was false, the
  hand could never take a round, and the gun opened and sat there. `SetChambers` now clamps to the
  mesh's count and always leaves somewhere to put a round.

## The BD revolver is a speedloader

Owner's call, 2026-10-13: five rounds into five chambers is not worth it. All five of the gun's
own rounds now go in as **one piece** down the cylinder axis. No new mesh and no new texture --
BD's `Revolver.md3` already carries the five rounds as five separate surfaces (5-9), each modelled
seated in its chamber, so showing all five at once *is* the loader.

**Visual alignment is knowingly imperfect** and was accepted: the cluster is held where chamber
0's round used to be, so it sits off the hold's centre.

`RSB_Load` in `Revolver.dec` now runs BD22's **own** fill loop rather than its one-round pass, so
its ammo logic and `TIF_NOTAKEINFINITE` behaviour are unchanged.

## Traps

- **Patch the shipped pack, never rebuild from the kit.** The kit rebuilds without the minigun
  bike grip, the sniper removal, the `give all` fix or the trigger finger.
- **`script parsing took` is the only proof of a clean parse.** Load errors do not reliably say
  "error". And baseline the warning count against the previous pack -- see
  [`../LOAD_ORDER.md`](../LOAD_ORDER.md).
- **`+vr_mode 0`, not `-config`,** is what keeps a desktop test out of the headset.
- **Netplay:** gestures are detected locally and decided over the net. Anything that changes the
  simulation keys on the owning player and travels by netevent; `consoleplayer` appears only to
  ask "are these my hands". Reasoning in [`v8_PROVING_PLAN.md`](v8_PROVING_PLAN.md).

## Not done

Nothing has been seen in a headset. Every tolerance above is a default derived from mesh
geometry, not from play.
