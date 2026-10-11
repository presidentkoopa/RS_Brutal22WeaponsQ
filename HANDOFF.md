# RS_QuestHands — state, 2026-10-03

## The mission

**BD22 playable in VR on Quest, with 3D weapon models you physically reload with
your hands.** Sprite weapons are unusable in VR; that is the whole reason this
exists.

It is an **addon that requires BD22 and cannot run without it**. Our guns are
BD22's guns — its damage, ROF, alt-fires and effects — because we never touch its
weapon classes. We only attach models and add hands/reload on top.

Two further modes: **V** (vanilla Doom roster) and **V+** (more guns, new
alt-fires), both inheriting vanilla Doom weapons.

Target: stock QuestZDoom 17.3 (`qzd17.3` = `9afc750917bf54870f2d16b7ba0d00f2b77e6fb5`,
GZDoom 4.14.3 base). **No engine changes.**

## Paths that matter

| what | where |
|---|---|
| this pack | `E:/DOOMWork/RS_QuestHands` |
| BD22 | `D:/SteamLibrary/steamapps/common/DooM VR/BD22 ModelDefs/brutal22test6/brutaldoom22` |
| BD21 VR set (models + 5,145 authored FrameIndex lines) | `E:/DOOMWork/VR_WeaponSetRebuild/WeaponSets/br_vr/PK3_pbr` |
| Vanilla VR Plus (read-only, live rotation) | `D:/SteamLibrary/steamapps/Common/DooM VR/__CurrentRotationDONOTDELETE/1.0b_Weapons_VanillaVRPlus_v1.2` |
| measured vanilla meshes | `E:/DOOMWork/RS_VR_Weapons/models/vanilla` |
| plan | `E:/DOOMWork/_reports/QUEST_RELOAD_DIAGNOSIS_2026-10-02.md` |
| source audit | `E:/DOOMWork/_reports/qzd17_stock_audit_2026-10-02/5_audit_of_the_audit.md` |

**THE AUTHORED MODELDEFS ALREADY EXIST.** BD21 has 5,145 hand-authored
`FrameIndex` lines across 37 files; Vanilla VR Plus has 852. Do not measure, infer
or reconstruct frame mappings. Re-key the originals with
`tools/rekey_modeldef.py`. I wasted a long stretch of this session rebuilding a
nine-row table from the first block of each file before being told.

## Built and working

**Hands + reload layer** (`zscript/`, ~2,400 lines, 8 files)

- `qh_hands.zs` — `QH_Hands` off-hand weapon carrying `ModifyBobLayer3D`,
  `QH_GunSide` helper item, steadying guard. Four layers: gun hand and support
  hand on the main controller (helper-owned), free hand and carried magazine on
  the off controller (hands-weapon-owned). That ownership split is load-bearing:
  `models.cpp:221` sends a layer to the off controller **only** if its caller is
  the off-hand weapon.
- `qh_metric.zs` — the pixelstretch correction. `AttackPos`/`OffhandPos` differ in
  Z by `1/pixelstretch`, so a raw `.Length()` under-reads vertical hand separation
  by 17%. Never measure hand distance without it.
- `qh_reload.zs` — the from-outside tic-hold and the card table. **13 guns carded**
  (see below).
- `qh_ride.zs` — the support hand riding the magazine, from frames measured out of
  `m16.md3`.
- `qh_surfaces.zs` — reimplements the engine's `TexMan.GetSurface` in script,
  since QZD has no such native. Data is `SURFACES.txt`, copied unchanged.
- `qh_ballistics.zs` / `qh_tracer.zs` — enhanced ballistics, additive only.

**Reload cards, 13 guns**

| set | guns | shape |
|---|---|---|
| BD22 | `Rifle`, `BrutalPistol`, `BrutalSMG`, `MP40`, `Sniper`, `AssaultShotgun` | magazine swap |
| BD22 | `Shot_Gun`, `Revolver` | per-shell loop |
| BD22 | `SSG` | break action |
| VVP | `VR_Rifle`, `VR_Revolver` ×2 | magazine swap |
| VVP | `VR_Shotgun` | per-shell loop |

Not carded, correctly: `MiniGun` and `MG42` have no `Reload` label at all.

**Modeldefs re-keyed from the authored originals**

- `MODELDEF.vanilla.txt` — 821 lines, 10 classes → `QHV_*`
- `MODELDEF.bd.txt` — ~4,800 lines. **32 of its classes are BD22's own names**, so
  those attach directly with no re-keying. Three dropped as fatal.

## Hard-won findings — do not rediscover these

- **A `Goto` REWRITES the preceding state's `NextState`, so `Resolve()` and
  `dec_reload_map.py` walk two different chains.** `FStateDefinitions::SetGotoLabel`
  (`p_states.cpp`:886) does `laststate->NextState = <target>`. Every BD22 reload
  label opens with a block of **0-tic** guards ending in `Goto Ready`, and the
  animation is reached only by those guards' *relative* jump
  (`A_JumpIfInventory("AmmoRocket",1,3)` — a jump of +3 **state slots**; a `Goto`
  occupies no slot). So:
  - `dec_reload_map.py` continues in **file order** past the `Goto`, which models
    the path the gun actually takes at runtime. Its step numbers are right.
  - `QH_ReloadCard.Resolve()` walks `st.NextState`, counts nothing in the 0-tic
    guards, **follows the rewritten pointer into `Ready`**, and resolves every
    step against the Ready loop instead of the reload.
  Nothing about it shows up in a parse — it is a wrong `State` pointer at
  runtime, which is why no amount of static checking found it.

  **FIXED 2026-10-09, by dropping step addressing entirely.** It cannot be
  repaired as written: stock QZD's ZScript `State` exposes only `NextState`,
  `sprite`, `Tics` and `Frame` (`doombase.zs`:577), so there is no array
  arithmetic and no `DistanceTo` — **execution order is not reachable from
  script at all**, and the relative jump the gun really takes cannot be
  followed. The replacement is `QHSM_SEQFRAME`: a stop is a **frame, matched as
  the layer plays it, in sequence**, where stop *i* is not even looked at until
  stop *i-1* has released. That observes the path the gun took instead of
  predicting it, so a `Goto`, an `A_Jump`, a random duration or a branch nobody
  read cannot shift it.
  - Being ordered is what makes repeated frames harmless — `RAIR I` ten times,
    `MISR T` four times — and it is also the only reason the rifle survives:
    its away and pullback are **both frame 7** (`RIFR H` and `2IFR H`), which
    the old mode told apart by label. **Push a card's stops in hand order.**
  - All **13 BD22 cards** are converted; each stop's comment keeps the step it
    came from, so the derivation is still auditable.
  - The **4 Vanilla VR Plus cards keep run/frame and were never affected**:
    `ReloadA` opens on a tic-bearing `RIFL LMN 2` with no guard block, and its
    only `goto` is past the end of the chain. Verified, not assumed.
  - `QHSM_STEPS` and `QH_ReloadCard.Resolve()` are left in place so nothing
    breaks, used by no card, and marked do-not-use.
  - No card false-arms from the Ready loop: every away frame is non-zero
    (7, 11, 13, 15, 20, 25, 26, and 5/8/8/11 on the new four) while Ready sits
    on frame A.

- **Three BD21 classes do not exist in BD22**: `HitlersBuzzsaw`, `Machinegun`,
  `Revolver2`. An unknown class in a MODELDEF is **fatal at startup**
  (`models.cpp:750` → `sc.ScriptError`). `Minigun` vs `MiniGun` is only case and
  is fine.
- **Sprites**: TNT1 cannot anchor an animation — it has one frame. Of the 159
  sprites the BD modeldefs key, **67 already ship with BD22**; the other 92 need
  placeholder lumps (BD21 ships none). A `FrameIndex` pointing at a missing sprite
  is a frame that silently never draws.
- **Sprite runs cap at 26 frames** in a folder pk3 — Doom frames continue into
  `[ \ ]` but a backslash is not a filename. Split across sprite names.
- **`NOINTERPOLATION` is on the gun bodies deliberately** in BD21. Reload stops
  work without blending; the magazine ride does not. Leave it alone.
- **Units differ between libraries**: RS_VR_Weapons meshes are centimetres
  (Scale 1.0), RS_Ballistics casings are millimetres (Scale 0.1), debris is
  world-scale. Measure each; never assume.
- **Netplay**: cvars read in `play` gate the simulation and must be `server`
  (11 of them); ui-only placement stays `user` (24). Hand gestures are detected
  locally and released via a `qh_rel` netevent, because VR hand poses are never
  sent over the wire.
- **Fork-only, no QZD equivalent**: `VOLUMEDEFS`, `DAMAGEDEFS`, `PARTICLEDEFS`
  (GPU particles), segment lights. Everything else in RS_Ballistics ports.

## Tools

| tool | what |
|---|---|
| `rekey_modeldef.py` | re-key an authored MODELDEF onto our classes. **Use this, never rebuild by hand.** Supports `--drop` for fatal classes. |
| `dec_reload_map.py` | enumerate a weapon's reload chain as numbered tic-bearing states, in both addressing modes the card accepts |
| `md3_part_track.py` | per-frame surface positions — finds a magazine by which surface moves |
| `md3_pose_survey.py` | mesh size and which frames are distinct poses |
| `md3_contact_sheet.py` | labelled renders for picking frames. **Side view is readable for hands; iso is not.** |
| `gen_vanilla_set.py` | **SUPERSEDED** by rekey_modeldef.py. Kept only for its sprite-lump generator. |

## What is left

The owner's framing: **BD22 guns, V guns, V+ guns, options menus, sounds, some
ballistics — done.** Status against each.

### 1. BD22 guns

- [x] Modeldef re-keyed. **32 of its classes are BD22's own names**, so those
      attach with no re-keying at all.
- [ ] Copy meshes into `models/bd` to match the re-keyed `Path` lines.
- [ ] 92 sprite lumps. Of the 159 sprites the modeldefs key, **67 already ship
      with BD22**; the rest are BD21's and BD21 ships no sprites.
- [x] **Reload cards: the BD22 roster is complete.** 13 guns carded as of
      2026-10-03: `Rifle`, `BrutalPistol`, `BrutalSMG`, `MP40`, `Sniper`,
      `AssaultShotgun`, `Shot_Gun`, `Revolver`, `SSG`, and the four added last —
      `Rocket_Launcher`, `RailGun`, `Plasma_Gun`, `GrenadeLauncher`. All mapped
      with `tools/dec_reload_map.py`; every stop's reasoning is in the comment
      above its card in `qh_reload.zs`.
      - `Rocket_Launcher` is the only one of the four that crosses a label — it
        closes under `FinishReload`, like `Rifle`.
      - `GrenadeLauncher` **must** be step-addressed: every state carries its
        sprite as `"####"`, so there is no run to name.
      - `Plasma_Gun`'s away and returned stops are **adjacent in steps and ten
        tics apart in time**, straddling one 10-tic state. Do not space them out.
      - `RailGun`'s `InsertBullets` is **not** a per-shell loop despite the name:
        no tic-bearing state, only 0-tic ammo accounting.
      - All four carry `CarryHand`: BD22 throws the spent round as a spawned
        actor in each, and there is no rocket, cell or grenade mesh yet.
- **`Flamethrower2` and `FlameCannon` need no card** — they *do* define a
  `Reload` label (`Flamethrower.dec`:93, `FlameCannon.dec`:65) but it is a **Ready
  loop**: one 1-tic `A_WeaponReady`, the standard jump block, then `Loop` /
  `Goto Ready3`. BD22 provides the label only so
  `A_JumpIfInventory("Reloading",1,"Reload")` has somewhere to land. Read in the
  .dec, not inferred.
- **The six `Dual*` variants are out of scope** — owner's call, 2026-10-03:
  flatscreen dual-wield, and in VR both hands are already real hands.

**Eleven have no reload at all and need no card** — verified, not assumed:
Unmaker, NukeLauncher, MiniGun, MG42, IncendiaryLauncher, HellishMissileLauncher,
HandGrenades, Devastator, DSweap, BIG_FUCKING_GUN, BFG10k.

### 2. V guns (vanilla roster)

- [x] Modeldef re-keyed — 821 authored lines, 10 classes → `QHV_*`.
- [ ] Copy meshes into `models/vanilla`; 208 sprite lumps.
- [ ] The `QHV_*` classes: inherit the vanilla weapon (so damage and ROF stay
      vanilla's), magazines at the owner's capacities — pistol 15, shotgun 8,
      SSG 2, chaingun 100, rocket 8, plasma 50, BFG 4, chainsaw and fist none —
      reload states over the re-keyed frames, and the toggle.
      **Toggle off means NO magazines at all — bullet hoses, fully vanilla ammo.**
- [ ] Reload cards for them.

### 3. V+ guns

Least done. Roster and meshes are located; Vanilla VR Plus has 219 authored lines
for rifle / revolver / shotty. Modeldefs, classes and cards all outstanding.
Capacities given: rifle 25, sunset and moonlight 6, flamethrower 100. Start
options: pistol, 2 pistols, pistol+revolver, 2 revolvers, rifle+shotgun.

### 4. Options menus

- [x] Hand placement, steadying, Vanilla VR Plus set, ballistics, trails.
      35 cvars, every one declared, read and slid.
- [ ] V and V+ set submenus, capacities, the reload toggle.
      The menu file documents how to add a set: one `Submenu` line plus one
      `OptionMenu` block.

### 5. Sounds

**Mostly free, and that is the addon design paying off.** BD22 and Vanilla VR
Plus play their own reload sounds because we never replace their states. Only
gesture feedback is ours, and the haptics are already in (off-hand buzz on
magazine release and seating, gun hand on the rack).

### 6. Ballistics

- [x] Hitscan impacts, projectile trails and impacts, 14 surfaces, debris,
      on/off, netplay-safe.
- [ ] Tuning in the headset; casing ejection if wanted.

### Not on the list, but true

**None of this has been loaded or run.** The first load will find things no
amount of static checking can — and the pack is deliberately built so that is
cheap: `qh_report` prints which layers exist, who owns each, and the
metric-corrected hand separation.


## Owner rules in force

- Reloading takes two hands → **never while steadying**. Guard reads
  `WF_TWOHANDSTABILIZED`; the reload **holds**, never aborts.
- **1–4 shells per insert**, any set, any shell-at-a-time gun.
- Enhanced ballistics is **on/off, and off means BD standard** — no `replaces`,
  no owned actors, no altered shots.
- Never write to `__CurrentRotationDONOTDELETE` or `BD22 ModelDefs`. Read only.
