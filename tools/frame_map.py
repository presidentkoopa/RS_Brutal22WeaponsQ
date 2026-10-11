#!/usr/bin/env python3
"""Work out which MODEL FRAME each BD22 sprite frame should draw.

THE PROBLEM
-----------
These meshes are animations: Rifle.md3 has 32 frames, Revolver 33, Plasma 30.
A MODELDEF line is `FrameIndex <sprite> <frame> <model> <modelframe>`, and the
model frame is the POSE. Pinning every line to frame 0 draws the first frame of
the raise animation in every state -- a gun stuck half-raised and angled down,
in the ready state, while firing, while reloading.

The authored BD21 defs are exactly this mapping, hand-made:

    FrameIndex RIFS A 0 0     select, frame 0
    FrameIndex RIFG A 0 3     ready pose
    FrameIndex RIFF A 0 4     firing
    FrameIndex RIFR A 0 7     reload begins

HOW THE MAPPING IS RECOVERED
----------------------------
BD21 and BD22 share most sprite NAMES for the same gun -- the rifle uses RIFG,
RIFF and RIFR in both. So wherever BD22 shows a sprite frame the authored def
also keyed, its model frame is copied VERBATIM. That is not inference; it is the
author's own pose for that exact picture.

For a BD22 sprite frame the authored def never keyed, there is no honest pose to
derive, so it falls back to the READY frame -- the model frame the authored def
gave the gun's ready sprite. A gun sitting in its ready pose during some state
nobody mapped is wrong in a way you can live with; a gun pointing at the floor
is not.

ONLY THE GUN'S OWN BLOCK IS READ. Each authored .def holds several Model blocks
-- the gun, a dual variant, nade.md3, Boot.md3, fistclosed.md3 -- all using
`Model 0` inside their own block. Reading them together is what produced model
frame indices up to 74 for a 32-frame mesh.

    python tools/frame_map.py Rifle
"""

import os
import re
import struct
import sys

AUTHORED = r"E:/DOOMWork/VR_WeaponSetRebuild/WeaponSets/br_vr/PK3_pbr"

MODELBLOCK_RE = re.compile(r'^\s*Model\s+([A-Za-z0-9_]+)\s*$', re.I)
MODELFILE_RE = re.compile(r'^\s*Model\s+(\d+)\s+"([^"]+)"', re.I)
FRAMEINDEX_RE = re.compile(
    r'^\s*FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', re.I)

# Meshes that are not the gun.
# "p_flame" and not "flame": the latter also excluded FlameCannon.md3 and
# Flamethrower2.md3, which ARE the guns.
OTHER_MESH = ("nade", "boot", "fistclosed", "dual", "p_flame")


def md3_frames(path):
    try:
        h = open(path, "rb").read(80)
        return struct.unpack("<i", h[76:80])[0]
    except OSError:
        return 0


def gun_block(def_path):
    """The FrameIndex lines of the block whose mesh is the GUN.

    Returns (mesh_filename, {(sprite, frame): modelframe}).
    """
    lines = open(def_path, errors="replace").read().splitlines()
    best = (None, {})

    i = 0
    while i < len(lines):
        if not MODELBLOCK_RE.match(lines[i]):
            i += 1
            continue

        mesh, pairs = None, {}
        depth, j = 0, i + 1
        while j < len(lines):
            ln = lines[j]
            depth += ln.count("{")
            if ln.count("}") and depth - ln.count("}") <= 0:
                break
            depth -= ln.count("}")

            m = MODELFILE_RE.match(ln)
            if m and mesh is None:
                mesh = os.path.basename(m.group(2).replace("\\", "/"))
            m = FRAMEINDEX_RE.match(ln)
            if m:
                pairs[(m.group(1).upper(), m.group(2).upper())] = int(m.group(4))
            j += 1

        if mesh and not any(k in mesh.lower() for k in OTHER_MESH):
            if len(pairs) > len(best[1]):
                best = (mesh, pairs)
        i = j + 1

    return best


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    want = sys.argv[1]

    path = None
    for fn in os.listdir(AUTHORED):
        if fn.lower() == ("modeldef.%s.def" % want).lower():
            path = os.path.join(AUTHORED, fn)
            break
    if not path:
        cands = [f for f in os.listdir(AUTHORED)
                 if f.lower().startswith("modeldef.") and want.lower() in f.lower()]
        if not cands:
            print("no authored def for %s" % want)
            return 1
        path = os.path.join(AUTHORED, cands[0])

    mesh, pairs = gun_block(path)
    print("authored def : %s" % os.path.basename(path))
    print("gun mesh     : %s" % mesh)
    print("keyed pairs  : %d" % len(pairs))
    if pairs:
        frames = sorted(set(pairs.values()))
        print("model frames : %d..%d  (%d distinct)"
              % (frames[0], frames[-1], len(frames)))
        by_sprite = {}
        for (s, f), mf in pairs.items():
            by_sprite.setdefault(s, []).append(mf)
        print("\nper sprite run -> model frame range:")
        for s in sorted(by_sprite):
            v = sorted(by_sprite[s])
            print("   %-6s %3d frames   %d..%d" % (s, len(v), v[0], v[-1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
