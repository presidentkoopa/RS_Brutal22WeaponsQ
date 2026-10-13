# tools/

| | |
|---|---|
| `posefix/` | the hand-fitting pipeline: placement, renders, pack builders. Start at its `README.md` and `hands/HAND_FITTING.md` |
| `v9kit/` | the v9 build kit: `melee/`, `hands/`, the builders, and the reload sources under `team/reload_merged/` |
| `trigger_finger/` | the trigger-finger rig and solver, plus `sol_bd.json` / `sol_vp.json` and the render sheets |

Python with numpy and Pillow runs all of it.

## Read this before running a builder

**The builders rebuild a pack WITHOUT the later patches.** `v9kit/team/build_bd22_v9.py` and
`build_vplus_v9.py` produce a pack missing the minigun bike grip, the sniper removal, the
`give all` fix and the trigger finger. Prefer patching the shipped pack:
`trigger_finger/patch.py` is the model for how -- it asserts the target matches what the
solution was built against, so it refuses to apply a stale fit rather than quietly producing a
wrong one.

**The v9kit scripts hard-code an old Linux scratchpad path.** Every script begins from
`S = /tmp/claude-0/...`; sed it to your own working folder before running anything.

## Render sheets

`trigger_finger/shots_bd.png` and `shots_vp.png`. **Look at them.** Both bugs the owner caught
were plainly visible in render sheets nobody opened.
