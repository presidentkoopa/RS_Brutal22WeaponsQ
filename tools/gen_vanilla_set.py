#!/usr/bin/env python3
"""Generate the Vanilla set: sprite lumps, MODELDEF and weapon classes.

WHY GENERATED
-------------
Nine weapons, each needing a sprite run long enough to key its reload (the
pistol alone is 22 model frames), is ~120 FrameIndex lines and ~120 sprite
lumps. Hand-writing that is how off-by-one errors get in, and I have already
made three counting mistakes in this set tonight. The table below is the only
thing anyone edits.

WHERE THE NUMBERS COME FROM
---------------------------
Not measured by me -- read out of the BD21 VR set, which already keyed these
meshes frame by frame:

    E:/DOOMWork/VR_WeaponSetRebuild/WeaponSets/br_vr/PK3_pbr/Modeldef.*.def

Its sprite naming gives the game away: a run ending in R is the reload. The
pistol's PISR maps sprite frames to model frames 8-29, the shotgun's SSHR to
23-31, and so on. Those ranges ARE the reload animation; BD21 found them years
ago and the meshes have carried them ever since.

The vanilla roster's own Classic* modeldefs in that set bind only ~6 frames per
gun, because vanilla Doom's sprite sets are that small -- which is exactly why
the reload animation has been sitting in the meshes unreachable. Our classes
exist to declare enough sprite frames to reach it. They inherit the vanilla
weapon so damage and rate of fire stay vanilla's.

WHAT IT DOES NOT DO
-------------------
It does not copy BD21's weapon code, states or balance. It reads frame numbers
out of a MODELDEF -- the measurement of which mesh frame is which animation
beat -- and nothing else.

USAGE
-----
    python gen_vanilla_set.py --out-root ..
"""

import argparse
import os
import struct
import sys
import zlib


# ---------------------------------------------------------------------------
# THE TABLE. Everything else is derived.
#
#   cls      our class name
#   parent   the vanilla Doom weapon it inherits (damage and ROF come from here)
#   sprite   our 4-char sprite base. 'QV' + two letters, to collide with nothing.
#   mesh     model file, relative to the BD21 set's Models/Weapons/Hud
#   skin     its skin
#   idle     (first, last) model frames for the ready/fire pose
#   reload   (first, last) model frames of the reload, or None if it has none
#   mag      magazine capacity, from the owner
# ---------------------------------------------------------------------------

WEAPONS = [
    # cls, parent, our sprite base, mesh (under the BD21 set's Models/Weapons/Hud),
    # skin, idle frames as MEASURED BY BD21 (model frame per pose, NOT a range),
    # reload model-frame range from BD21's own *R run, magazine.
    #
    # The idle lists are BD21's Classic* mappings read verbatim. They are NOT
    # sequential -- the pistol's is 2,4,4,5,6,3 -- because they record which model
    # frame matches which pose, which is exactly the measurement we cannot infer.
    # An earlier version of this table invented a sequential range and was wrong.
    ("QHV_Pistol",         "Pistol",         "QVPI",
     "BrutalPistol/BrutalPistol.md3", "BrutalPistol.png",
     [2, 4, 4, 5, 6, 3],                                   (8, 29),  15),

    ("QHV_Shotgun",        "Shotgun",        "QVSG",
     "Shotgun/Shotgun.md3", "WPN-GUNS-k1.png",
     [4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18],      (23, 31), 8),

    ("QHV_SSG",            "SuperShotgun",   "QVSS",
     "SSG/SSG.md3", "WPN-GUNS-k1.png",
     [1, 2, 5, 6, 8, 10, 13, 14, 15, 16, 17, 18, 19, 20,
      21, 22, 23, 25, 24, 26, 27, 28, 29, 30, 31, 32],     (33, 45), 2),

    # NOTE: ClassicChaingun maps to Minigun.md3, not Machinegun.md3. An earlier
    # version of this table had the wrong mesh.
    ("QHV_Chaingun",       "Chaingun",       "QVCG",
     "Minigun/Minigun.md3", "Minigun.png",
     [4, 5, 6, 7, 8, 9, 10, 11],                           None,     100),

    ("QHV_RocketLauncher", "RocketLauncher", "QVRL",
     "RPG/RPG.md3", "RPG.png",
     [5, 9, 11, 12, 13, 14, 15, 6, 7, 8],                  (17, 34), 8),

    ("QHV_Plasma",         "PlasmaRifle",    "QVPL",
     "Plasma/Plasma.md3", "Plasma.png",
     [4, 5, 6, 7, 8, 17, 16, 15, 9, 10, 11, 12],           (18, 29), 50),

    ("QHV_BFG",            "BFG9000",        "QVBF",
     "BFG/BFG.md3", "BFG.png",
     [0, 1, 2, 3, 4, 5, 6],                                None,     4),

    ("QHV_Chainsaw",       "Chainsaw",       "QVCS",
     "Chain_saw/Chain_saw.md3", "Chain_saw.png",
     [18, 19, 13, 14, 13, 14],                             None,     0),

    ("QHV_Fist",           "Fist",           "QVFI",
     "FIST/fistclosed.md3", "fist.png",
     [48, 0, 1, 2, 3, 4, 5, 6, 7, 8, 45, 46],              None,     0),
]

# The kick. Bound into every weapon in the BD21 set under its own sprite, which
# is how the quick kick draws a boot whatever you are holding.
BOOT = ("QVBT", "Boot/Boot.md3", "Boot.png", (0, 57))

# A-Z ONLY, 26 frames per sprite name.
#
# Doom frames continue past Z into [ \ ] ^ _ , but a folder-based pk3 stores one
# lump per FILE, and a backslash is not a filename -- it is a path separator.
# The first run of this silently tried to write sprites/QVPI\0.png and failed
# there. So a run longer than 26 frames is split across consecutive sprite
# NAMES instead: QVPI, QVPJ, QVPK. The pistol needs 28 frames, so it uses two.
FRAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PER_SPRITE = len(FRAME_CHARS)


def alloc(spr, n):
    """[(sprite_name, frame_char)] for n consecutive frames starting at spr."""
    out = []
    base, first = spr[:3], spr[3]
    for i in range(n):
        name = base + chr(ord(first) + i // PER_SPRITE)
        out.append((name, FRAME_CHARS[i % PER_SPRITE]))
    return out


# ---------------------------------------------------------------------------
# 1x1 transparent PNG, built rather than pasted so the bytes are provably valid.
# ---------------------------------------------------------------------------

def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def transparent_png():
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    raw = b"\x00" + b"\x00\x00\x00\x00"
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(raw, 9))
            + _chunk(b"IEND", b""))


def span(rng):
    """Frame count. A (first,last) tuple is a range; a list is already the frames."""
    if rng is None:
        return 0
    if isinstance(rng, (list,)):
        return len(rng)
    return rng[1] - rng[0] + 1


def frames_of(rng):
    """The model frames themselves, in order."""
    if rng is None:
        return []
    if isinstance(rng, (list,)):
        return list(rng)
    return list(range(rng[0], rng[1] + 1))


def emit_sprites(out_root):
    """One lump per sprite frame every weapon uses."""
    d = os.path.join(out_root, "sprites")
    os.makedirs(d, exist_ok=True)
    blob = transparent_png()
    names = []

    for cls, parent, spr, mesh, skin, idle, reload_rng, mag in WEAPONS:
        total = span(idle) + span(reload_rng)
        for nm, ch in alloc(spr, total):
            names.append("%s%s0" % (nm, ch))

    for nm, ch in alloc(BOOT[0], span(BOOT[3])):
        names.append("%s%s0" % (nm, ch))

    for n in names:
        with open(os.path.join(d, n + ".png"), "wb") as fh:
            fh.write(blob)
    return names


def emit_modeldef(out_root, model_path):
    """One block per weapon, plus the boot."""
    L = []
    L.append("// " + "=" * 74)
    L.append("// RS_QuestHands -- Vanilla set models")
    L.append("//")
    L.append("// GENERATED by tools/gen_vanilla_set.py. Edit the table there, not this.")
    L.append("//")
    L.append("// Frame numbers are read out of the BD21 VR set's own modeldefs, which")
    L.append("// keyed these meshes years ago -- a sprite run ending in R is its reload.")
    L.append("// The vanilla roster's Classic* blocks there bind only ~6 frames each,")
    L.append("// because vanilla Doom's sprite sets are that small, which is why the")
    L.append("// reload animation has been in the meshes and unreachable. These blocks")
    L.append("// declare enough frames to reach it.")
    L.append("//")
    L.append("// NOINTERPOLATION is kept on the gun bodies exactly as BD21 had it. Those")
    L.append("// animations have frames far enough apart that blending makes the gun look")
    L.append("// like it is melting, and that set has been in use for years. A reload stop")
    L.append("// does not need blending: holding a frame works either way.")
    L.append("// " + "=" * 74)
    L.append("")

    for cls, parent, spr, mesh, skin, idle, reload_rng, mag in WEAPONS:
        L.append("// ---- %s : %s  (magazine %s) ----" % (cls, parent, mag if mag else "none"))
        L.append("Model %s" % cls)
        L.append("{")
        L.append('\tPath "%s/%s"' % (model_path, os.path.dirname(mesh)))
        L.append('\tModel 0 "%s"' % os.path.basename(mesh))
        L.append('\tSkin 0 "%s"' % skin)
        L.append("\tScale -1.0 1.0 1.0")
        L.append("\tNoInterpolation")
        total = span(idle) + span(reload_rng)
        slots = alloc(spr, total)
        i = 0
        # frames_of, NOT range(). `idle` is a LIST of measured model frames and
        # is deliberately not sequential -- the pistol's is 2,4,4,5,6,3. Treating
        # it as a (first,last) range silently emitted 3 frames instead of 6, and
        # the fist's [48,0,...] became range(48,1), i.e. nothing at all.
        L.append("\t// idle / fire -- BD21's measured pose mapping, verbatim")
        for f in frames_of(idle):
            nm, ch = slots[i]
            L.append("\tFrameIndex %s %s 0 %d" % (nm, ch, f))
            i += 1
        if reload_rng:
            L.append("\t// reload -- model frames %d-%d, from BD21's *R run" % reload_rng)
            for f in frames_of(reload_rng):
                nm, ch = slots[i]
                L.append("\tFrameIndex %s %s 0 %d" % (nm, ch, f))
                i += 1
        L.append("}")
        L.append("")

    spr, mesh, skin, rng = BOOT
    L.append("// ---- the boot: Brutal Doom's quick kick ----")
    L.append("// BD21 binds this into every weapon's own modeldef so the kick draws a")
    L.append("// boot whatever is in your hands. One block here, keyed to its own class.")
    L.append("Model QHV_Boot")
    L.append("{")
    L.append('\tPath "%s/%s"' % (model_path, os.path.dirname(mesh)))
    L.append('\tModel 0 "%s"' % os.path.basename(mesh))
    L.append('\tSkin 0 "%s"' % skin)
    L.append("\tScale -1.0 1.0 1.0")
    slots = alloc(spr, span(rng))
    for i, f in enumerate(range(rng[0], rng[1] + 1)):
        nm, ch = slots[i]
        L.append("\tFrameIndex %s %s 0 %d" % (nm, ch, f))
    L.append("}")
    L.append("")

    p = os.path.join(out_root, "MODELDEF.vanilla.txt")
    with open(p, "w", newline="\n") as fh:
        fh.write("\n".join(L))
    return p, sum(1 for l in L if "FrameIndex" in l)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default="..")
    ap.add_argument("--model-path", default="models/vanilla",
                    help="where the meshes sit inside the pk3")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.out_root)
    names = emit_sprites(root)
    path, n = emit_modeldef(root, args.model_path)

    print("sprite lumps : %d" % len(names))
    print("modeldef     : %s  (%d FrameIndex lines)" % (os.path.relpath(path, root), n))
    print()
    for cls, parent, spr, mesh, skin, idle, rl, mag in WEAPONS:
        print("  %-22s : %-14s %s  idle %2d  reload %-8s mag %s"
              % (cls, parent, spr,
                 span(idle),
                 ("%d" % span(rl)) if rl else "none",
                 mag if mag else "-"))
    print("  %-22s   %-14s %s  %d frames" % ("QHV_Boot", "(kick)", BOOT[0], span(BOOT[3])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
