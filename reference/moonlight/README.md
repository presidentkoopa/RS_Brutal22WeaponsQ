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

## Measured (lane B, 2026-10-27): `measure_moonlight.py`, output in `measured.txt`
Every number from the mesh (`rev.md3`, 41 frames, 11 surfaces) through the Depot's model chain
(`tools/kit/rgeo.py`, cm in the weapon controller's frame, F forward, L left, U up).

- **What each surface is:**
  - 0 `python.004`: frame and grip;
  - 1 `python.005`: cylinder;
  - 3 `python.007`: barrel and top strap;
  - 2: a small part fixed to the frame;
  - 4-9: the six rounds, collapsed (hidden) except in frames 20-29;
  - 10 (257 verts): the speedloader, hidden except in frames 21-38.
- **Frames:**
  - ready / fire 0-15, rest again 37-40;
  - break-open 17-19 (snaps to 82°, then 70°, 61-66° while loading);
  - eject 20-29 (the rounds appear, then fly out one by one, 24-29);
  - speedloader in 21-25, seated 25-30, away 31-38;
  - close 30-33.
- **Placement:** the Depot's hand-fitted `rev_wm.md3` IS `rev.md3` frame 0 moved (-25.08, 0, 3.47)
  mesh units (rotation identity, residual 0.0000). So rev.md3 at the Depot's fit is:
  `Scale 1.35 1.35 1.35 / Offset 0.0262 0.9224 / ZOffset 0.5878`.
  Rig (QZD 17.3, test-only MODELDEF on BD22's Revolver): it sits in the existing revolver hand fit,
  grip in the palm; frame 26 shows the break-top open (`moonlight_rig_frame0_vs_26.png`).
- **Break-top hinge:**
  - the part is surfaces 1 + 3, rigid (fit 0.02-0.04 cm), relative to the frame;
  - it turns barrel-down about +L, through F 8.46, L 0, U -1.14 at the loading pose (frame 26);
  - opening 63.3° there (61.5-66.0 over frames 22-30);
  - the axis point drifts to F 9.2-9.6 in the snap frames 19 and 31.
- **Cylinder and chambers (closed frame):**
  - cylinder F 1.85-8.30 (rear face 1.85), centre L -0.03, U 2.12;
  - six chambers on radius 1.8-2.0 cm about L -0.01, U 2.15.
- **Speedloader seat (frames 25-26, closed frame):** centre F 1.65, L -0.15, U 1.88, axis along F
  (1, -0.004, -0.01), F -2.23 to 8.08 (rounds inside the cylinder, body behind its rear face).

## Owner's decisions (2026-10-27 06:09)
- **Name:** Moonlight is renamed **Revolver**. BD22 already has a class called `Revolver`, the shotgun-shell revolver (the Shotvolver), so the class becomes `BrutalRevolver` with the tag/name "Revolver". The owner allowed "BrutalRevolver if we absolutely have to".
- **Ammo: BD22 has no revolver ammo of its own** (parsed from brutal22test6):
  - BD22 `Revolver` reserve = `AmmoShell` (shotgun shells), cylinder = `RevolverAmmo` (max 6);
  - our `Revolver2` (slug revolver) reserve = `Clip2`, cylinder = `RevolverAmmo`.

  So the six-shooter needs its own reserve ammo, e.g. `RevolverRounds`, with a pickup. The owner prefers recolouring the Shotvolver's voxel ammo pickup to match the Moonlight mesh's colour; failing that, recolour another voxel or make one. Where it spawns (replacing what, how much) is the owner's call when built.
