#!/usr/bin/env python3
"""Pack RS_QuestHands into a loadable pk3.

The lane had no build step, so there was never anything to load. This is it.

A pk3 is a zip. What goes in is the data the engine reads; what stays out is our
own working material (tools, renders, notes, .bak files), because a lump the
engine does not understand in a folder pk3 is noise at best.

Checks before writing, since a pk3 that cannot load is worse than no pk3:
  - every #include in zscript.txt resolves to a real file
  - every MODELDEF Path/Model/Skin names a file that is actually present
Refuses to write if either fails, and says which.

    python tools/build.py              -> RS_QuestHands.pk3 beside the folder
    python tools/build.py -o <path>    -> somewhere else
"""
import argparse
import os
import re
import sys
import zipfile
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lumps and trees the engine reads.
# MODELDEF.vanilla.txt is DELIBERATELY NOT SHIPPED: it keys QHV_* classes
# that are not written yet, and an unknown class in a MODELDEF is fatal at
# startup, not a warning. Add it back with the V guns.
FILES = ["CVARINFO.txt", "KEYCONF.txt", "MENUDEF.txt", "MODELDEF.txt",
         "MODELDEF.bd.txt", "SURFACES.txt",
         "SNDINFO.txt", "zscript.txt"]
TREES = ["zscript", "models", "sprites", "sounds"]
SKIP_EXT = {".bak", ".md", ".py", ".ps1"}

INCLUDE_RE = re.compile(r'#include\s+"?([^"\s]+)"?', re.I)
PATH_RE = re.compile(r'^\s*Path\s+"?([^"\s]+)"?', re.I)
MODELFILE_RE = re.compile(r'^\s*(?:Model|Skin|SurfaceSkin)\s+\d*\s*"([^"]+)"', re.I)


def check_includes():
    bad = []
    p = os.path.join(ROOT, "zscript.txt")
    if not os.path.exists(p):
        return ["zscript.txt itself is missing"]
    for line in open(p, errors="replace"):
        m = INCLUDE_RE.search(line)
        if m and not os.path.exists(os.path.join(ROOT, m.group(1))):
            bad.append(m.group(1))
    return bad


def check_models():
    """Every file a modeldef block names must exist under its Path."""
    bad = []
    for d in ("MODELDEF.txt", "MODELDEF.bd.txt", "MODELDEF.vanilla.txt"):
        p = os.path.join(ROOT, d)
        if not os.path.exists(p):
            continue
        cur = None
        for line in open(p, errors="replace"):
            m = PATH_RE.match(line)
            if m:
                cur = m.group(1).replace("\\", "/").strip("/")
                continue
            m = MODELFILE_RE.match(line)
            if m and cur:
                fn = os.path.basename(m.group(1).replace("\\", "/"))
                if not os.path.exists(os.path.join(ROOT, cur, fn)):
                    bad.append("%s/%s  (%s)" % (cur, fn, d))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out",
                    default=os.path.join(os.path.dirname(ROOT), "RS_QuestHands.pk3"))
    ap.add_argument("--force", action="store_true",
                    help="write even if a check fails (for seeing a load error on purpose)")
    args = ap.parse_args()

    inc = check_includes()
    mdl = check_models()

    if inc:
        print("UNRESOLVED #include (%d) -- a pk3 with one of these REFUSES TO LOAD:" % len(inc))
        for x in inc:
            print("   ", x)
    if mdl:
        print("MODELDEF names a file that is not present (%d):" % len(mdl))
        for x in mdl[:40]:
            print("   ", x)
        if len(mdl) > 40:
            print("    ... and %d more" % (len(mdl) - 40))

    if (inc or mdl) and not args.force:
        print("\nREFUSED. Fix the above, or pass --force to pack anyway.")
        return 1

    n = 0
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                z.write(p, f)
                n += 1
        for t in TREES:
            base = os.path.join(ROOT, t)
            if not os.path.isdir(base):
                continue
            for dirpath, _dirs, files in os.walk(base):
                for fn in files:
                    if os.path.splitext(fn)[1].lower() in SKIP_EXT:
                        continue
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.relpath(full, ROOT).replace("\\", "/"))
                    n += 1

    print("\nwrote %s" % args.out)
    print("%d entries, %.1f MB" % (n, os.path.getsize(args.out) / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
