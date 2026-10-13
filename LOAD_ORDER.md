# Load order, and how to run a pack

**Never load the two packs together.** They define overlapping classes and both claim the same
psprite layers. One pack, one base, one session.

## BD22

```
brutal22test6.pk3        <- base/, 152 MB, a Brutal Doom 22 test build
BD22_Models_v9.pk3       <- packs/, ours
```

IWAD: Doom 2.

## Vanilla VR Plus

```
1.0b_Weapons_VanillaVRPlus_v1.2/   <- base/, a FOLDER, not a pk3
RS_VanillaVRPlus_VR_v9.pk3         <- packs/, ours
```

IWAD: Doom or Doom 2. The V+ base is loaded as a directory; its `FILTER/` subtree applies per
game, which is why a few of its own DECORATE warnings appear at load (see below).

This pack also carries a crash fix for that set: with default weapon switching, switching away
from the M16 or the revolvers overflows the stack.

## Running one on the PC to check a change

Full detail and the traps: [`docs/engine/QZD17_TARGET.md`](docs/engine/QZD17_TARGET.md). The
short version, from a build of the pinned engine:

```bash
cd E:/DOOMWork/QZD17-engine/build/Release
./qzdoom.exe -iwad doom2.wad -config SCRATCH/t.ini \
  -file E:/DOOMWork/RS_VR_Weapons/bd22/brutal22test6.pk3 E:/DOOMWork/BD22_Models_v9.pk3 \
  -nosound -nomusic +vr_mode 0 +logfile SCRATCH/bd.log +wait 30 +quit
```

**`+vr_mode 0` is the guard, not `-config`.** A fresh scratch config means *defaults*, and the
default on this machine is VR and fullscreen -- it will take over the headset. After the run,
confirm it held: `grep I_StartupOpenXR` the log and expect nothing.

### Reading the result

`script parsing took ...` is the **only** line that proves a clean parse. ZScript load errors do
not necessarily contain the word "error", so never grep for that alone.

Warning counts are not zero and are not supposed to be. Baseline them by running the previous
pack through the identical command, or a pre-existing warning reads as one you caused:

| pack | expected | whose they are |
|---|---|---|
| BD22 | 8 warnings | brutal22test6's own: `BrutalWeapon` / `BDMummy` states, `NormalWeaponStarter` |
| V+ | 9 warnings | the V+ set's own `Decorate\`: unknown `postalpuff` / `vrshotpuff` / `vrssgpuff`, missing `RIFFG0` icon |

### On the headset

Sideload the base and the pack together in QuestZDoom and set the load order there. Nothing in
either pack needs an engine change, so stock QuestZDoom 17.x is enough.

## The options menu

Everything switchable is under **Options -> RS VR Hands, Reload, Ballistics**:

| row | cvar | values |
|---|---|---|
| VR hands | `rsq_hands` | on / off |
| Reloading | `rsr_reload` | **VR** (1) / Stock (0) |
| Reload assist | `rsr_assist` | 0.5 .. 3.0, default 1.0 |
| Where a magazine comes from | `rsr_pouch` | anywhere, 20 cm from the gun (0) / low, 40 cm below the eyes (1) |
| Ballistics | `rsq_ballistics` | Enhanced (1) / Stock (0) |

And in the **Reload: tuning and debug** submenu off that page:

| row | cvar | values |
|---|---|---|
| Reload assist | `rsr_assist` | the same slider, repeated so it can be moved while watching the zones |
| Show the capture zones | `rsr_assist_debug` | on / off, default off |
| Print each reload step | `rsr_debug` | on / off, default off |

**Everything you need while wearing the headset is in the menu.** A console command is no use
with a headset on, so the two debug toggles have menu rows rather than being console-only.

Still console-only, because they take a key code or a button mask and no menu widget fits:

| cvar | what it does |
|---|---|
| `rsr_grip_keys` | the off-hand grip's key codes, default `"443 436"` |
| `rsr_grab_buttons` | buttons that grab anywhere, default `BT_OFFHANDATTACK` |
| `rsr_magrelease` | buttons that drop the magazine, default `BT_OFFHANDRELOAD` |
| `rsr_eat_grip` | while a reload has the off hand, its grip key does nothing else |

To find your controller's grip codes: turn on **Print each reload step**, press the grip, and
read the codes it prints, then set `rsr_grip_keys` to them.
