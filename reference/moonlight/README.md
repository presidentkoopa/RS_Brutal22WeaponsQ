# Moonlight: the normal revolver for BD22 (owner, 2026-10-27)

A six-shooter, break action, with a speedloader. It replaces the normal revolver's mesh; the shotvolver keeps its own mesh.

- `Modeldef.Weapons2.original` is the original mod's MODELDEF, from the owner:
  - `Models/Weapons/hud/gats/rev.md3`, 41 frames: REVL A-Z (26) and REVO A-o (15, "draw, cowboy");
  - flash `revF.MD3`;
  - Scale 1.35.
- **The 41-frame mesh, already on disk:**
  - RS_ModelSwapper `models/vplus/gats/rev.md3` (11 surfaces, sha1 81e48872) and `revf.md3`. The original's `hud/gats` path matches this copy.
  - `models/hud/Revolver/rev.md3` is a different build (sha1 a0f9cab5).
- **The Depot copy** (`sets/plus_0.7/.../rev_wm.md3`) has 1 frame and 10 surfaces. It is measured and hand-fitted, but has the stock reload only.
- **To do:**
  - measure which REVL frames are the break-open / eject / speedloader;
  - build a hand-driven break-open + speedloader reload;
  - make it the BD22 revolver mesh.
