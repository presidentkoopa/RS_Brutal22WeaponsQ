#!/usr/bin/env python3
"""Re-key an authored MODELDEF onto our own classes, preserving every line.

WHY
---
The BD21 VR set carries 5,145 hand-authored FrameIndex lines across 37
modeldefs -- Chainsaw 312, Pistol 255, SMG 254, Rifle 253, ClassicSSG 118,
ClassicPistol 90. Vanilla VR Plus carries 852 more. That is the mapping of which
model frame is which pose, for every gun, done by hand over years.

It does not need redoing, inferring or measuring. It needs the class name on the
`Model <X>` line changed and nothing else touched.

An earlier pass of mine built a nine-row table by reading the FIRST BLOCK of
each Classic modeldef and treating it as the file. That threw away roughly 90%
of the authored data and got the rest wrong. This tool exists so that cannot
happen again: it is a rename, not a reconstruction.

WHAT IT PRESERVES
-----------------
Every FrameIndex, Scale, Offset, ZOffset, Skin, SurfaceSkin, Path, rotation and
flag line, verbatim, in order, including NOINTERPOLATION -- which is on the gun
bodies deliberately and is not ours to second-guess.

WHAT IT CHANGES
---------------
Only `Model <OldClass>` -> `Model <NewClass>`, and only for classes named in the
map. Any block whose class is not mapped is passed through untouched, so a file
that also defines shared props (the boot, fists, grenade) keeps them.

It also reports every sprite the file keys, so the matching lumps can be made --
a FrameIndex pointing at a sprite with no lump is a frame that silently never
draws.

USAGE
-----
    python rekey_modeldef.py --src <dir> --pattern "Modeldef.Classic*.def" \\
        --map ClassicPistol=QHV_Pistol,ClassicShotgun=QHV_Shotgun \\
        --out ../MODELDEF.vanilla.txt --path-prefix models/vanilla
"""

import argparse
import glob
import os
import re
import sys

MODEL_RE = re.compile(r'^(\s*)Model\s+([A-Za-z0-9_]+)\s*$', re.I)
PATH_RE = re.compile(r'^(\s*)Path\s+"([^"]*)"\s*$', re.I)
FRAME_RE = re.compile(r'^\s*FrameIndex\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', re.I)


def rekey(src_files, mapping, path_prefix=None, drop=None):
    """drop: classes whose blocks are removed entirely.

    An unknown class name in a MODELDEF is FATAL at startup -- models.cpp:750
    does PClass::FindClass and sc.ScriptError's on a miss, so one stale block
    stops the whole pack loading. BD21 names three classes BD22 no longer has
    (HitlersBuzzsaw, Machinegun, Revolver2), and they have to come out.
    """
    drop = set(d.lower() for d in (drop or []))
    out = []
    sprites = {}
    counts = {}
    current = None
    kept_unmapped = set()
    dropping = False
    dropped = {}
    depth = 0

    for path in src_files:
        out.append("")
        out.append("// " + "-" * 72)
        out.append("// from %s" % os.path.basename(path))
        out.append("// " + "-" * 72)

        with open(path, "r", errors="replace") as fh:
            for line in fh.read().splitlines():
                # While dropping a block, swallow lines until its braces close.
                if dropping:
                    depth += line.count("{") - line.count("}")
                    if depth <= 0:
                        dropping = False
                        depth = 0
                    continue

                m = MODEL_RE.match(line)
                if m:
                    indent, cls = m.group(1), m.group(2)
                    if cls.lower() in drop:
                        dropping = True
                        depth = 0
                        dropped[cls] = dropped.get(cls, 0) + 1
                        current = None
                        continue
                    if cls in mapping:
                        current = mapping[cls]
                        out.append("%sModel %s" % (indent, current))
                    else:
                        current = cls
                        kept_unmapped.add(cls)
                        out.append(line)
                    continue

                # Model files move into our pk3, so Path is rebased if asked.
                p = PATH_RE.match(line)
                if p and path_prefix:
                    indent, old = p.group(1), p.group(2)
                    tail = old.replace("\\", "/")
                    low = tail.lower()
                    for marker in ("models/weapons/hud/", "models/weapons/", "models/"):
                        i = low.find(marker)
                        if i >= 0:
                            tail = tail[i + len(marker):]
                            break
                    out.append('%sPath "%s/%s"' % (indent, path_prefix.rstrip("/"), tail))
                    continue

                f = FRAME_RE.match(line)
                if f:
                    spr, frm = f.group(1), f.group(2)
                    sprites.setdefault(spr.upper(), set()).add(frm.upper().strip('"'))
                    counts[current] = counts.get(current, 0) + 1

                out.append(line)

    return out, sprites, counts, kept_unmapped, dropped


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--pattern", default="Modeldef.*.def")
    ap.add_argument("--map", default="", help="Old=New,Old=New")
    ap.add_argument("--out", required=True)
    ap.add_argument("--path-prefix", default=None)
    ap.add_argument("--drop", default="",
                    help="classes to remove entirely, comma separated. An unknown "
                         "class in a MODELDEF is fatal at startup.")
    ap.add_argument("--sprite-dir", default=None,
                    help="write placeholder lumps for every sprite keyed")
    args = ap.parse_args(argv)

    mapping = {}
    for pair in args.map.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            sys.stderr.write("bad --map entry %r\n" % pair)
            return 2
        a, b = pair.split("=", 1)
        mapping[a.strip()] = b.strip()

    files = sorted(glob.glob(os.path.join(args.src, args.pattern)))
    if not files:
        sys.stderr.write("no files matched %s in %s\n" % (args.pattern, args.src))
        return 1

    drop = [d.strip() for d in args.drop.split(",") if d.strip()]
    out, sprites, counts, unmapped, dropped = rekey(
        files, mapping, args.path_prefix, drop)

    header = [
        "// " + "=" * 72,
        "// RS_QuestHands -- re-keyed from authored modeldefs. NOT reconstructed.",
        "//",
        "// Every FrameIndex, Scale, Offset, Skin and flag below is the original",
        "// author's, verbatim and in order. The only change is the class name on",
        "// the `Model` line, plus Path rebased into this pk3.",
        "//",
        "// Source: %s" % args.src,
        "// Files : %d" % len(files),
        "// " + "=" * 72,
    ]

    with open(args.out, "w", newline="\n") as fh:
        fh.write("\n".join(header + out) + "\n")

    total = sum(counts.values())
    print("wrote %s" % args.out)
    print("  source files   : %d" % len(files))
    print("  FrameIndex     : %d" % total)
    print()
    print("  per class:")
    for k in sorted(counts, key=lambda k: -counts[k]):
        tag = "" if k in mapping.values() else "   (passed through unmapped)"
        print("    %-26s %4d%s" % (k, counts[k], tag))

    if dropped:
        print()
        print("  dropped (class absent in the target mod -- would be fatal):")
        for k in sorted(dropped):
            print("    %-26s %d block(s)" % (k, dropped[k]))

    print()
    print("  sprites keyed: %d" % len(sprites))
    need = []
    for spr in sorted(sprites):
        for frm in sorted(sprites[spr]):
            if len(frm) == 1:
                need.append("%s%s0" % (spr, frm))
    print("  sprite lumps needed: %d" % len(need))

    if args.sprite_dir:
        import struct
        import zlib

        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data
                    + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

        blob = (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(b"\x00" + b"\x00\x00\x00\x00", 9))
                + chunk(b"IEND", b""))
        os.makedirs(args.sprite_dir, exist_ok=True)
        made = 0
        for n in need:
            p = os.path.join(args.sprite_dir, n + ".png")
            if not os.path.exists(p):
                with open(p, "wb") as fh:
                    fh.write(blob)
                made += 1
        print("  sprite lumps written: %d (%d already present)" % (made, len(need) - made))

    return 0


if __name__ == "__main__":
    sys.exit(main())
