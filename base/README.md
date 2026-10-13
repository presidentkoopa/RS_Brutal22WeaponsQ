# base/

The mods each pack loads on top of. A pack is an add-on and will not load without its base, so
both bases live here.

| | what it is | whose |
|---|---|---|
| `1.0b_Weapons_VanillaVRPlus_v1.2/` | the Vanilla VR Plus weapon set. A folder, not a pk3 | **ours** |
| `brutal22test6.pk3` | a Brutal Doom 22 test build, 152 MB | third party |

**Do not edit either copy.** Not a question of ownership -- our packs are add-ons that sit on
top, so every change we make belongs in `../packs/`. Editing a base here just makes the pack and
the base disagree, and the pack is what ships.

The Vanilla VR Plus original also sits in the live play rotation at a **read-only** path; see the
end of `../docs/v8_PROVING_PLAN.md`. Read it there for class names and frames, never write to it.

Both are in Git LFS. `brutal22test6.pk3` has to be: GitHub hard-blocks any single file over
100 MB.

The warnings each base produces at load are its own, not the pack's. Expected counts are in
`../LOAD_ORDER.md` -- baseline against them, or a pre-existing warning reads as one you caused.
