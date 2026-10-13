# packs/

The two shipped pk3s. **These are the source of truth.** Patch them in place; a rebuild from
`tools/v9kit/` silently drops the minigun bike grip, the sniper removal, the `give all` fix and
the trigger finger.

Stored in Git LFS. Clone with `git lfs install` first or you get text pointers.

| pack | load after | base lives in |
|---|---|---|
| `BD22_Models_v9.pk3` | `brutal22test6.pk3` | `../base/` |
| `RS_VanillaVRPlus_VR_v9.pk3` | `1.0b_Weapons_VanillaVRPlus_v1.2/` | `../base/` |

**Never load the two together.** See `../LOAD_ORDER.md`.

Their text lumps are unpacked under `../src/bd22/` and `../src/vplus/` so they are greppable;
the meshes are in `../models/` and inside the pk3.
