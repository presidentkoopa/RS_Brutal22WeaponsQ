#!/usr/bin/env python3
"""Rewrite MODELDEF.bd.txt's FrameIndex lines against BD22's OWN sprites.

THE PROBLEM THIS FIXES
----------------------
MODELDEF keys a model on (class, sprite, frame). The classes in MODELDEF.bd.txt
are BD22's, but the FrameIndex SPRITE NAMES were carried over from the BD21 set
the meshes came from -- e.g. AssaultShotgun keyed on A12S, a name that does not
occur anywhere in BD22. BD22's assault shotgun uses USAS and 2SAR. So every
block keys frames the weapon never enters, and no model can ever draw.

Nothing from BD21 is needed or used here. The meshes are BD21's; the keying is
read from BD22's own DECORATE.

WHAT IT EMITS
-------------
For each block, every (sprite, frame) pair that class's states actually use,
each pointing at model 0 frame 0 -- a STATIC model that is present in every
state. That is deliberately not an animation: BD21's frame mapping described
BD21's animation and is meaningless against BD22's state chains. A gun that is
visible in every frame is the correct first result; per-state frames are a
second pass, and they need the mesh's own frame list.

"####" in a state means "keep the previous sprite", so the walk carries the
last explicit one forward -- which is the only reason the grenade launcher and
the flamers resolve to anything at all.

    python tools/rekey_sprites_bd22.py              # report
    python tools/rekey_sprites_bd22.py --write      # rewrite MODELDEF.bd.txt
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELDEF = os.path.join(ROOT, "MODELDEF.bd.txt")
BD22 = r"D:/SteamLibrary/steamapps/common/DooM VR/BD22 ModelDefs/brutal22test6/brutaldoom22/actors/Weapons"

# A state line: SPRITE FRAMES TICS [action].  Sprite is 4 chars or "####".
STATE_RE = re.compile(
    r'^\s*(?P<spr>"####"|####|[A-Z0-9_]{4})\s+'
    r'(?P<frames>"[^"]+"|[A-Za-z0-9\[\]\\_]+)\s+'
    r'(?P<tics>-?\d+)', re.I)
ACTOR_RE = re.compile(r'^\s*ACTOR\s+(\S+)', re.I)
BLOCK_RE = re.compile(r'^\s*Model\s+(\S+)\s*$', re.I)
FRAMEINDEX_RE = re.compile(r'^\s*FrameIndex\s', re.I)


def frame_letters(tok):
    """'ABCDE' or '"[ \\ ]"' -> list of single frame characters."""
    t = tok.strip('"')
    return [c for c in t if c not in ' \t']


def sprites_for_actor(path, actor):
    """Every (SPRITE, FRAME) pair this actor's own states use, in order."""
    try:
        lines = open(path, errors="replace").read().splitlines()
    except OSError:
        return []

    start = None
    pat = re.compile(r'^\s*ACTOR\s+' + re.escape(actor) + r'\s*(:|\{|$|\s)', re.I)
    for i, ln in enumerate(lines):
        if pat.match(ln):
            start = i
            break
    if start is None:
        return []

    pairs, seen = [], set()
    carried = None
    for ln in lines[start + 1:]:
        m = ACTOR_RE.match(ln)
        if m and not pat.match(ln):
            break                      # into the next actor
        m = STATE_RE.match(ln)
        if not m:
            continue
        spr = m.group('spr').strip('"').upper()
        if spr == '####':
            if not carried:
                continue               # nothing to carry yet
            spr = carried
        else:
            carried = spr
        for f in frame_letters(m.group('frames')):
            key = (spr, f.upper())
            if key not in seen:
                seen.add(key)
                pairs.append(key)
    return pairs


def find_dec(actor):
    """Which .dec defines this actor."""
    if not os.path.isdir(BD22):
        return None
    pat = re.compile(r'^\s*ACTOR\s+' + re.escape(actor) + r'\s*(:|\{|$|\s)', re.I)
    for fn in sorted(os.listdir(BD22)):
        if not fn.lower().endswith(".dec"):
            continue
        p = os.path.join(BD22, fn)
        try:
            for ln in open(p, errors="replace"):
                if pat.match(ln):
                    return p
        except OSError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(MODELDEF):
        print("no MODELDEF.bd.txt"); return 1

    lines = open(MODELDEF, errors="replace").read().splitlines()

    out, cls, depth = [], None, 0
    stats, missing = [], []

    for ln in lines:
        m = BLOCK_RE.match(ln)
        if m:
            cls = m.group(1)
            out.append(ln)
            continue

        if cls and ln.strip().startswith("{"):
            depth += 1
            out.append(ln)
            continue

        if cls and ln.strip().startswith("}"):
            depth -= 1
            if depth <= 0:
                # Emit this class's keying just before the block closes.
                dec = find_dec(cls)
                pairs = sprites_for_actor(dec, cls) if dec else []
                if pairs:
                    out.append("")
                    out.append("\t// Keyed on BD22's OWN sprites, read from %s."
                               % os.path.basename(dec))
                    out.append("\t// Static: model 0 frame 0 in every state the class enters.")
                    for spr, f in pairs:
                        out.append("\tFrameIndex\t%s\t%s\t0\t0" % (spr, f))
                    stats.append((cls, len(pairs), os.path.basename(dec)))
                else:
                    missing.append(cls)
                cls, depth = None, 0
            out.append(ln)
            continue

        # Drop every inherited FrameIndex; everything else in the block stays.
        if cls and FRAMEINDEX_RE.match(ln):
            continue

        out.append(ln)

    print("classes re-keyed : %d" % len(stats))
    for c, n, d in stats[:40]:
        print("   %-22s %4d pairs   (%s)" % (c, n, d))
    if len(stats) > 40:
        print("   ... and %d more" % (len(stats) - 40))
    if missing:
        print("\nNO BD22 STATES FOUND (left with no FrameIndex, so no model): %d" % len(missing))
        print("   " + ", ".join(missing[:20]))

    if not args.write:
        print("\nreport only -- pass --write to rewrite MODELDEF.bd.txt")
        return 0

    open(MODELDEF, "w").write("\n".join(out) + "\n")
    print("\nrewrote %s" % MODELDEF)
    return 0


if __name__ == "__main__":
    sys.exit(main())
