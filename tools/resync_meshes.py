#!/usr/bin/env python3
"""Re-copy the meshes and skins MODELDEF.bd.txt names, from the authored tree.

WHY
---
An earlier pass collected meshes by matching FILENAME across several source
trees. That picked whichever copy it found first, and one of them was a ZERO
BYTE Unmaker.md3 -- which parses fine as a MODELDEF reference and then crashes
or silently fails when the renderer tries to load it. A -norun check cannot see
that, because -norun exits before anything is drawn.

So the source is no longer "wherever a file of that name lives". It is the
AUTHORED tree first -- br_vr/PK3_pbr/Models/Weapons/Hud, which is what the
authored Path lines point at -- and the others only as a fallback. Any candidate
of zero length is refused outright, and every .md3 that lands is checked for a
valid header.

    python tools/resync_meshes.py            # report
    python tools/resync_meshes.py --write    # copy
"""

import argparse
import os
import re
import shutil
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELDEF = os.path.join(ROOT, "MODELDEF.bd.txt")

# In priority order. The authored Hud tree is what the authored Path lines name,
# so it is the one the placement numbers were fitted against.
SOURCES = [
    r"E:/DOOMWork/VR_WeaponSetRebuild/WeaponSets/br_vr/PK3_pbr/Models/Weapons/Hud",
    r"E:/DOOMWork/VR_WeaponSetRebuild/WeaponSets/br_vr/PK3_pbr",
    r"E:/DOOMWork/RS_VR_Weapons/models/vanilla",
]

PATH_RE = re.compile(r'^\s*Path\s+"?([^"\n]*)"?', re.I)
FILE_RE = re.compile(r'^\s*(?:Model|Skin|SurfaceSkin)\s+\d+\s+"([^"]+)"', re.I)


def md3_problem(path):
    """Why this .md3 is unusable, or None."""
    sz = os.path.getsize(path)
    if sz == 0:
        return "zero bytes"
    with open(path, "rb") as fh:
        h = fh.read(108)
    if len(h) < 108:
        return "truncated (%d bytes)" % sz
    if h[0:4] != b"IDP3":
        return "bad magic %r" % h[0:4]
    if struct.unpack("<i", h[4:8])[0] != 15:
        return "bad version"
    nframe, _ntag, nsurf = struct.unpack("<i", h[76:80])[0], 0, struct.unpack("<i", h[84:88])[0]
    if not 0 < nframe < 4096:
        return "frame count %d" % nframe
    if not 0 < nsurf < 128:
        return "surface count %d" % nsurf
    if struct.unpack("<i", h[104:108])[0] != sz:
        return "eof offset does not match size"
    return None


def index_sources():
    """{lowercase basename: [full paths]} in source priority order."""
    idx = {}
    for root in SOURCES:
        if not os.path.isdir(root):
            print("  (source missing: %s)" % root)
            continue
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                full = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(full) == 0:
                        continue          # never a usable source
                except OSError:
                    continue
                idx.setdefault(fn.lower(), []).append(full)
    return idx


def wanted():
    """[(destdir, filename)] every file the modeldef names."""
    out, cur = [], None
    for line in open(MODELDEF, errors="replace"):
        m = PATH_RE.match(line)
        if m:
            cur = m.group(1).replace("\\", "/").strip("/")
            continue
        m = FILE_RE.match(line)
        if m and cur:
            out.append((cur, os.path.basename(m.group(1).replace("\\", "/"))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(MODELDEF):
        print("no MODELDEF.bd.txt"); return 1

    idx = index_sources()
    todo, fine, nosrc = [], 0, []

    for destdir, fn in wanted():
        target = os.path.join(ROOT, destdir, fn)
        bad = None
        if os.path.exists(target):
            if os.path.getsize(target) == 0:
                bad = "zero bytes"
            elif fn.lower().endswith(".md3"):
                bad = md3_problem(target)
        else:
            bad = "absent"

        if not bad:
            fine += 1
            continue

        cands = idx.get(fn.lower(), [])
        src = next((c for c in cands
                    if not (c.lower().endswith(".md3") and md3_problem(c))), None)
        if not src:
            nosrc.append("%s/%s  (%s, no good source)" % (destdir, fn, bad))
            continue
        todo.append((target, src, bad))

    print("files already good : %d" % fine)
    print("to replace         : %d" % len(todo))
    for t, s, why in todo:
        print("   %-44s  %s\n      from %s" % (os.path.relpath(t, ROOT), why, s))
    if nosrc:
        print("\nNO USABLE SOURCE: %d" % len(nosrc))
        for x in nosrc:
            print("   " + x)

    if not args.write:
        print("\nreport only -- pass --write")
        return 0

    for t, s, _why in todo:
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copy2(s, t)
    print("\ncopied %d" % len(todo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
