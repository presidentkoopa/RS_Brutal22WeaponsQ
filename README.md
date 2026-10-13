# RS_Quest

Everything for the two **QuestZDoom** weapon packs: posed hands on the gun, the index finger on
the trigger, and a physical VR reload. Stock QuestZDoom 17.x, **no engine changes** anywhere in
here.

Target engine: `qzd17.3` = `9afc750917bf54870f2d16b7ba0d00f2b77e6fb5` (GZDoom 4.14.3 base).

> **Quest is closed after these packs.** The future is UZDXREMA, REMAROTH and REMASELACO. This
> repo is the finished record of the Quest work plus the lessons to carry forward -- see
> [`docs/CONCERN_vr_worldweapons_2026-10-12.md`](docs/CONCERN_vr_worldweapons_2026-10-12.md) for
> what to do differently next time.

## The packs

Both are shipped and current. **They are the source of truth: patch them in place.** A rebuild
from a kit silently drops later fixes -- that has happened repeatedly, see
[`CHANGELOG.md`](CHANGELOG.md).

| pack | load it after | holds |
|---|---|---|
| `packs/BD22_Models_v9.pk3` | `base/brutal22test6.pk3` | hands, trigger finger, VR reload, ballistics, for Brutal Doom 22 |
| `packs/RS_VanillaVRPlus_VR_v9.pk3` | `base/1.0b_Weapons_VanillaVRPlus_v1.2/` | the same, for the Vanilla VR Plus weapon set |

**Never load the two packs together.** Exact load orders and the launch command:
[`LOAD_ORDER.md`](LOAD_ORDER.md).

## Where to start, by subject

| you want | read |
|---|---|
| **Gun in hand** -- how a hand gets placed on a weapon | [`docs/GUN_IN_HAND.md`](docs/GUN_IN_HAND.md) |
| **Finger on trigger** -- bending the index finger, squeezing on fire | [`docs/FINGER_ON_TRIGGER.md`](docs/FINGER_ON_TRIGGER.md) |
| **Reloading on Quest** -- the physical reload and its capture zones | [`docs/RELOAD_ON_QUEST.md`](docs/RELOAD_ON_QUEST.md) |
| the whole method, start to finish | [`docs/VR_Hands_Fitting_Process.md`](docs/VR_Hands_Fitting_Process.md) |
| what is in the packs right now, and every number | [`docs/HANDOFF_trigger_finger.md`](docs/HANDOFF_trigger_finger.md) |
| what went wrong, and what it cost | [`docs/POSTMORTEM.md`](docs/POSTMORTEM.md) |
| how to run a pack to check a change | [`docs/engine/QZD17_TARGET.md`](docs/engine/QZD17_TARGET.md) |
| the v8 engine citations, netplay reasoning, open licence question | [`docs/v8_PROVING_PLAN.md`](docs/v8_PROVING_PLAN.md) |

## Layout

```
packs/      the two shipped pk3s                                 [Git LFS]
base/       the mods each pack loads on top of                   [Git LFS]
src/        the packs' own lumps, unpacked and greppable
  bd22/       everything in BD22_Models_v9.pk3 except models/
  vplus/      everything in RS_VanillaVRPlus_VR_v9.pk3 except models/
  v8_questhands/   the SUPERSEDED v8 generation (qh_*.zs)
models/     the loose gun meshes and skins: the fitting tools' input
sprites/    placeholder lumps (MODELDEF keys on sprite+frame; the model replaces them)
tools/
  posefix/         the hand-fitting pipeline: placement, renders, pack builders
  v9kit/           the v9 build kit: melee/, hands/, the builders, the reload sources
  trigger_finger/  the trigger-finger rig and solver, and its per-gun results
docs/       see the table above
skill/      vr-hand-fitting/SKILL.md -- the recipe a Claude session loads automatically
```

### Two generations live here, do not mix them

`src/bd22` and `src/vplus` are the **current** v9 packs: `zscript/rsq/` (hands, ballistics),
`zscript/rsr/` (the reload), `zscript/rsvr/` (melee, VR plumbing).

`src/v8_questhands/` is the **superseded** v8 generation, `zscript/qh_*.zs`. It is kept for its
reasoning, not for use. Nothing in the shipped packs references a `qh_` class.

### Why `src/` and `models/` both exist

`models/` holds the loose `.md3` meshes and `.png` skins -- the **input** to the fitting tools.
`src/bd22` and `src/vplus` hold the **text** lumps of each shipped pack: its ZScript, MODELDEF,
CVARINFO, MENUDEF and patched DECORATE, unpacked so they are greppable and diffable in git. The
meshes are deliberately not duplicated into `src/`; they are in `models/` and inside the pk3.

### Why Git LFS

`base/brutal22test6.pk3` is 152 MB and GitHub hard-blocks any single file over 100 MB, so it
cannot live in ordinary git at all. `packs/*.pk3` and everything under `base/` go to LFS
(~235 MB). `models/` and `sprites/` stay in ordinary git **on purpose** -- routing them to LFS
too would spend the whole free quota on content git already stores well.

Clone with LFS installed, or `packs/` and `base/` arrive as small text pointers:

```bash
git lfs install
git clone https://github.com/presidentkoopa/RS_Quest.git
```

### What is in `base/`

A pack is an add-on and will not load without its base, so both bases are here.
`1.0b_Weapons_VanillaVRPlus_v1.2/` is **our own** Vanilla VR Plus weapon set;
`brutal22test6.pk3` is a Brutal Doom 22 test build.

Do not edit either copy -- our packs sit on top of them, so every change we make belongs in
`packs/`. The Vanilla VR Plus original also sits in the live play rotation at a **read-only**
path; see the end of [`docs/v8_PROVING_PLAN.md`](docs/v8_PROVING_PLAN.md).

## State

Both packs are shipped, parse clean against the pinned engine, and **have never been tested in a
headset.** Every tolerance in the reload is a default chosen from mesh geometry rather than from
play, so expect the **Reload assist** slider to do real work on the first run.

Known open items are listed at the end of [`CHANGELOG.md`](CHANGELOG.md).
