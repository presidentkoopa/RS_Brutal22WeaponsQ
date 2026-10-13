# The target engine, and how to check a pack against it

Target: `qzd17.3` = `9afc750917bf54870f2d16b7ba0d00f2b77e6fb5` (GZDoom 4.14.3 base).
Both packs declare `version "4.10"` in their ZSCRIPT lump.

**Nothing in this repo requires an engine change.** That is a hard constraint, not an aspiration:
these packs run on stock QuestZDoom from the store build. If something seems to need an engine
addition, it belongs in UZDXREMA instead, not here.

## Why this is separate from RS_VR_Reload

`RS_VR_Reload` is built on `level.HandPos`, `SetModelJoint` and `SetModelFlag` -- **UZDXREMA
engine additions that do not exist in stock QZD.** It cannot run on this target. The two share
ideas (the capture spheres in particular) and no code.

## A local build for checking

A Windows build of the pinned engine lives at `E:\DOOMWork\QZD17-engine\`, with binaries at
`build\Release\qzdoom.exe` and `build\RelWithDebInfo\qzdoom.exe`, and `doom.wad` / `doom2.wad`
alongside the Release one.

Note: that tree is **not** stock -- it carries local changes. For a question about stock
behaviour, cite it with `git show` against the pinned commit rather than reading the working
tree.

The Linux headless build (`qzd_headless.zip`) is for a cloud container and is useless on Windows.
It is gitignored.

## Running a pack

```bash
cd E:/DOOMWork/QZD17-engine/build/Release
./qzdoom.exe -iwad doom2.wad -config SCRATCH/t.ini \
  -file E:/DOOMWork/RS_VR_Weapons/bd22/brutal22test6.pk3 E:/DOOMWork/BD22_Models_v9.pk3 \
  -nosound -nomusic +vr_mode 0 +logfile SCRATCH/bd.log +wait 30 +quit
```

For V+, swap in the V+ base folder and the V+ pack. `SCRATCH` is anywhere outside the repo.

### The traps, in order of how much they have cost

**1. `+vr_mode 0` is the guard, not `-config`.** A scratch config guards the owner's ini and
*nothing else*. An empty config means **defaults**, and the default on this machine is VR and
fullscreen -- it will start in the headset while he is using the computer. This has happened.
Afterwards, verify it held:

```bash
grep I_StartupOpenXR SCRATCH/bd.log   # expect nothing
```

**2. Ask the owner before launching anything.** Every time.

**3. `script parsing took` is the only proof of a clean parse.** ZScript load failures do not
reliably contain the word "error", so grepping for "error" alone will tell you a broken pack is
fine. Look for the line; if it is absent, the parse did not finish.

**4. Load the archive, not the folder.** A text-level check of loose files never catches a
load-time refusal. Load the actual `.pk3`.

**5. Baseline the warning count.** Neither pack loads with zero warnings and neither is supposed
to. Run the previous pack (or a `_backups` copy) through the **identical** command and compare
counts, or a pre-existing warning reads as one you just caused.

| pack | expected warnings | whose |
|---|---|---|
| BD22 | 8 | brutal22test6's own: `BrutalWeapon` / `BDMummy` states, `NormalWeaponStarter` |
| V+ | 9 | the V+ set's own `Decorate\`: unknown `postalpuff` / `vrshotpuff` / `vrssgpuff` classes, missing `RIFFG0` icon |

### Last known good

2026-10-13, after the reload-assist change:

| pack | script parsing | warnings before | after |
|---|---|---|---|
| BD22 | 3849.02 ms | 8 | 8 |
| V+ | 959.50 ms | 9 | 9 |

## Engine facts the packs rest on

Cited because they were expensive to establish. Line numbers are against the pinned tree.

| fact | where |
|---|---|
| a `ModifyBobLayer3D` override on our off-hand weapon is called for layers owned by our helper item | `hw_weapon.cpp:332`, `:941-951` |
| a layer goes to the off controller **only** if its caller is `player->OffhandWeapon` | `models.cpp:221` |
| `vr_weaponScale` and `vr_3dweaponOffset*` live **inside** the weapon transform, so they move every hand with the gun | `models.cpp:251`, `:277` |
| a layer drawn at `y = 0` is tilted: `(my - WEAPONTOP) / -4` | `hw_weapon.cpp` |
| the engine mirrors the physical left controller's model with a plain `scale(-1,1,1)`, applied **after** MODELDEF scale signs decide culling | `hw_vrmodes.cpp:469`, `models.cpp:279-281` |
| `RenderHUDModel` turns yaw about y, then pitch about x, then roll about z | `models.cpp` |
| setting a replacee to itself is ignored, so `Replacement = null` + `IsFinal = true` means "no replacement" | `events.cpp` |
| `give all` skips replaced weapons | `player.zs` `CheatGive` |
| a weapon's state is required on a layer whose caller is the off-hand weapon | `p_pspr.cpp` `SetState` |
| `A_SpawnParticle` offsets are world-space unless `SPF_RELPOS` is set | `constants.zs:733` |
| `Color(alpha, red, green, blue)` -- four args, alpha first | `base.zs:345` |

## MODELDEF traps

- One `Model` block binds **one class**, not its children.
- `FrameIndex <SPR> <letter>` needs **no sprite lump** for a model-only layer -- letters in use
  here have none, and letters need not be contiguous (`G` is skipped, `H` and `I` are used).
- Scale is **per block**. There is no inheritance.
- A piece is shown or hidden with a clear skin (`rsr_clear.png`) on its surface, which is how one
  mesh serves as the gun, the magazine, the hinged part and each loose round.
