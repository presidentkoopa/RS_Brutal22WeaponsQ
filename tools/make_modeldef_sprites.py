#!/usr/bin/env python3
"""Emit placeholder lumps for every sprite the modeldefs key but nobody ships.

WHY THIS IS NEEDED
------------------
MODELDEF keys a model on (caller class, sprite, frame). The sprite is never
seen -- the model replaces it -- but the LUMP MUST EXIST, and an absent one is
fatal at startup, not a warning:

    Script error, "RS_QuestHands.pk3:modeldef.bd.txt" line 27:
    Unknown sprite A12S in model definition for AssaultShotgun

Our BD modeldefs were re-keyed from BD21's authored originals. BD21 ships no
sprites of its own, and only part of what it keys also exists in BD22 -- so the
rest have to be created or the pack cannot load at all.

WHY IT ONLY FILLS THE GAPS
--------------------------
A placeholder is a 1x1 transparent PNG, and a lump in our pk3 SHADOWS the same
name in an earlier one. Blanketing every keyed name would therefore blank out
BD22's real sprites wherever they are used for something a model does not
replace -- a pickup lying on the floor, for instance. So this reads what BD22,
the IWAD and we already provide, and writes only the genuine absences.

    python tools/make_modeldef_sprites.py            # report only
    python tools/make_modeldef_sprites.py --write     # create them
"""

import argparse
import os
import re
import struct
import sys
import zipfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "sprites")
DEFS = ["MODELDEF.bd.txt", "MODELDEF.vanilla.txt", "MODELDEF.txt"]

# Everything already loaded ahead of us at runtime. Order does not matter here;
# we only care whether a name exists anywhere.
SOURCES = [
    r"D:/SteamLibrary/steamapps/Common/DooM VR/BD22 ModelDefs/brutal22test6/brutal22test6.pk3",
    r"D:/SteamLibrary/steamapps/Common/DooM VR/___Sourceport/doom2.wad",
]

FRAMEINDEX_RE = re.compile(r'^\s*FrameIndex\s+(\S+)\s+(\S+)\s+', re.I)


# ---------------------------------------------------------------- PNG
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def transparent_png():
    """1x1 fully transparent RGBA. Built, not pasted, so it is provably valid."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
    idat = _chunk(b"IDAT", zlib.compress(b"\x00" + b"\x00\x00\x00\x00"))
    return sig + ihdr + idat + _chunk(b"IEND", b"")


# ---------------------------------------------------------------- what is keyed
def wanted_lumps():
    """{lumpname: (sprite, frame)} for every FrameIndex in our modeldefs."""
    out = {}
    for d in DEFS:
        p = os.path.join(ROOT, d)
        if not os.path.exists(p):
            continue
        for line in open(p, errors="replace"):
            m = FRAMEINDEX_RE.match(line)
            if not m:
                continue
            spr, frame = m.group(1).upper(), m.group(2).upper()
            if len(spr) != 4 or len(frame) != 1 or frame == '#':
                continue
            if frame == chr(92):
                # A frame beyond Z runs [ \ ] and a backslash cannot be a
                # filename, so this lump cannot be shipped in a zip at all.
                # Noted rather than silently skipped.
                continue
            # Rotation 0 = "same picture from every angle", which is what a
            # model-backed sprite always is.
            out["%s%s0" % (spr, frame)] = (spr, frame)
    return out


# ---------------------------------------------------------------- what exists
def wad_lumps(path):
    """Lump names from an IWAD/PWAD directory."""
    names = set()
    with open(path, "rb") as fh:
        head = fh.read(12)
        if head[:4] not in (b"IWAD", b"PWAD"):
            return names
        count, offset = struct.unpack("<ii", head[4:12])
        fh.seek(offset)
        for _ in range(count):
            e = fh.read(16)
            if len(e) < 16:
                break
            names.add(e[8:16].rstrip(b"\x00").decode("latin-1").upper())
    return names


def existing_lumps():
    names = set()

    for src in SOURCES:
        if not os.path.exists(src):
            print("  (missing, not counted: %s)" % src)
            continue
        if src.lower().endswith(".wad"):
            names |= wad_lumps(src)
        else:
            with zipfile.ZipFile(src) as z:
                for n in z.namelist():
                    base = os.path.splitext(os.path.basename(n))[0]
                    if base:
                        names.add(base.upper())

    # Our own pack, so re-running is idempotent.
    if os.path.isdir(SPRITES):
        for fn in os.listdir(SPRITES):
            names.add(os.path.splitext(fn)[0].upper())

    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    want = wanted_lumps()
    have = existing_lumps()
    missing = sorted(n for n in want if n not in have)

    print("keyed by our modeldefs : %d lumps" % len(want))
    print("already provided       : %d" % (len(want) - len(missing)))
    print("MISSING                : %d" % len(missing))

    if missing:
        shown = ", ".join(missing[:14])
        print("  e.g. %s%s" % (shown, " ..." if len(missing) > 14 else ""))

    if not args.write:
        print("\nreport only -- pass --write to create them")
        return 0

    os.makedirs(SPRITES, exist_ok=True)
    blob = transparent_png()
    for n in missing:
        with open(os.path.join(SPRITES, n + ".png"), "wb") as fh:
            fh.write(blob)

    print("\nwrote %d placeholder lumps into sprites/" % len(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
