# Finger on the trigger

The gun hand's index finger sits **on** each gun's trigger, and squeezes when the gun fires.
Shipped in both packs 2026-10-12. The full record, per gun, is in
[`HANDOFF_trigger_finger.md`](HANDOFF_trigger_finger.md); the tools are in
`tools/trigger_finger/`.

## The problem it solved

The gun hand was Ermac's `hand.md3` grip pose, fitted only by the grip (ICP on the grip patch).
Its index finger points **straight forward along the receiver, above the trigger guard** -- the
side view of `fit_Rifle.png` shows it clearly. Not on the trigger. The same on every gun.

And Ermac's `hand.md3` has **no trigger-pulled frames**. All 211 were checked against every grip
pose, including with rigid recoil removed. So the finger had to be bent by us.

## How it was done

The index finger is **mesh component 1** of `hand.md3` -- 79 vertices, a separate piece, same
topology in every frame. That is what makes this tractable: the finger can be posed without
touching the rest of the hand.

Rig (`tools/trigger_finger/rig.py`): MCP / PIP / DIP hinges along the finger, plus MCP abduction,
plus a small root slide (never more than 0.9 cm) for the guns where the trigger was simply out
of reach of the fitted grip.

Per gun, the trigger blade is picked by a bounding box (`boxes.py`) and the fingertip **pad** is
solved onto its front face (`trig.py` for BD22, `vpsolve.py` for V+).

Guns with **no trigger mesh at all** -- Devastator, Flamethrower2, Minigun, Unmaker, both BFGs,
Hellish, Rocket_Launcher -- use a **virtual trigger** at the mean trigger offset of the
rifle-type guns (`virt.py`). The V+ low-poly guns (revolvers, M16, shotgun, SSG) have no trigger
blade either; their target is a point inside the guard opening (`vpsolve.py` `TG`).

## The frames and how they are chosen

Two new frames per pose, written into the pack's cut `hand.md3` at about 8 KB each:

- **on trigger** -- the finger bent at its joints so the pad of the fingertip touches the
  trigger face. Sprite `RQGT`.
- **squeeze** -- a further curl of 15-20 degrees. Sprite `RQGU`.

| pack | unique poses | new frames | frame range |
|---|---|---|---|
| BD22 | 17 | 34 | 10..43 |
| V+ | 8 | 16 | -- |

`handtable.zs` `RSQ_HandTable.Trigger(i)` gives the letter per gun. `rsq/hands.zs` uses the
squeeze letter (`SqzX`) while `BT_ATTACK` is held, and the on-trigger letter (`TrgX`) otherwise.

The axe, the chainsaw -- and the removed sniper -- keep the plain grip frame. Nothing to pull.

### V+ borrows from BD22

The V+ chaingun, rocket launcher, plasma rifle and BFG **are** the BD22 meshes, placed 5 cm
higher with the hand hooks 5 cm higher too. So their finger poses are copied straight across:
`sol_vp.json` marks them `"from_bd"`.

## Re-applying after a rebuild

Built only on each pack's own cut `hand.md3`; nothing from `_old/` was read for this.

```bash
python3 -I -B tools/trigger_finger/patch.py bd tools/trigger_finger/sol_bd.json <in.pk3> <out.pk3>
python3 -I -B tools/trigger_finger/patch.py vp tools/trigger_finger/sol_vp.json <in.pk3> <out.pk3>
```

`patch.py` asserts that the `hand.md3` in the pack matches the one the solution was built
against, so it refuses to apply a stale solution rather than producing a quietly wrong hand.

## The tools

| file | what it does |
|---|---|
| `rig.py` | the finger rig: joints, limits, forward kinematics |
| `boxes.py` | the per-gun trigger-blade boxes |
| `trig.py` | solves the BD22 fingertip onto the blade face |
| `vpsolve.py` | the same for V+, including the inside-the-guard target |
| `virt.py` | the virtual trigger for guns with no trigger mesh |
| `batch.py` | runs the whole set |
| `build.py` | writes the new frames into the cut `hand.md3` |
| `patch.py` | patches a shipped pack in place |
| `sol_bd.json`, `sol_vp.json` | the per-gun results |
| `shots_bd.png`, `shots_vp.png` | the render sheets. **Look at these.** |
| `rend.py`, `shots.py`, `zoom.py`, `review.py` | renders and review sheets |
| `slabs.py`, `hm.py`, `md3w.py`, `tab.py` | mesh and MD3 helpers |
| `noreload.py` | switches VR reloading off. **Superseded** -- see below |

## `noreload.py` is history

It switched the VR reload off in a pack. It has been undone: reloading is back on by default in
both packs as of 2026-10-13. The script is kept only so the mechanism is on record. Note that it
only ever ran against the V+ pack -- BD22 shipped with the reload live the whole time, which is
why the owner's "too strict" verdict came from BD22. See
[`RELOAD_ON_QUEST.md`](RELOAD_ON_QUEST.md).

## If the vertex maths ever stalls again

The documented fallback, which was not needed:

1. Export the 8 cut gun-hand frames (`models/rsq/hand.md3`, letters A-H per `MODELDEF.rsq`) for
   hand-posing in Blender.
2. Do the rest in code: new MODELDEF letters, and the squeeze letter while firing in `hands.zs`.
