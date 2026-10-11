#!/usr/bin/env python3
"""Print a weapon's reload chain as a numbered list of tic-bearing states.

WHY THIS EXISTS
---------------
Carding a gun means naming the exact states where the animation should pause.
Reading that off a .dec by eye is slow and I get it wrong: a 0-tic action state
is invisible plumbing that must not shift the count, a `GHIJKLMNNO` run is ten
states on one line, duplicated letters are easy to miscount, and a `Goto` can
jump somewhere that never comes back.

So the chain gets enumerated mechanically, in exactly the terms the card uses:

    STEP  -- the Nth state that actually holds for a tic, counting from a label.
             This is what QH_ReloadCard.AddStepStop takes.
    RUN   -- which distinct sprite run the state is in, and the frame inside it.
             This is what QH_ReloadCard.AddStop takes.

Both are printed so a card can use whichever addressing suits the gun. Rifles
with clean two-sprite reloads read better as run/frame; BD22's, whose chain
loops through a 0-tic ammo block, needs steps.

USAGE
-----
    python dec_reload_map.py <file.dec> <ACTOR> [--label Reload]
    python dec_reload_map.py Rifle.dec Rifle --label Reload
    python dec_reload_map.py Rifle.dec Rifle --labels        # list labels only
"""

import argparse
import os
import re
import sys

# A state line: SPRT FRAMES TICS [action]
#   sprite is 4 chars or "####"; frames are a run of letters/symbols or "#"
STATE_RE = re.compile(
    r'^\s*(?P<spr>[A-Z0-9_]{4}|"#+"|#+)\s+'
    r'(?P<frames>"[^"]+"|[A-Za-z0-9\[\]\\_]+)\s+'
    r'(?P<tics>-?\d+)\s*(?P<rest>.*)$'
)
LABEL_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?://.*)?$')
GOTO_RE = re.compile(r'^\s*Goto\s+([A-Za-z_][A-Za-z0-9_.]*)', re.I)
STOPLIKE_RE = re.compile(r'^\s*(Stop|Loop|Wait|Fail)\s*$', re.I)


def frame_index(ch):
    """Doom frame letter -> index. A=0 .. Z=25, then [ \\ ] ^ _ ."""
    o = ord(ch.upper())
    if 65 <= o <= 90:
        return o - 65
    if 91 <= o <= 95:          # [ \ ] ^ _
        return o - 65
    return -1


def extract_actor(path, actor):
    """The States block of one ACTOR, as a list of raw lines."""
    with open(path, "r", errors="replace") as fh:
        lines = fh.read().splitlines()

    start = None
    pat = re.compile(r'^\s*ACTOR\s+' + re.escape(actor) + r'\s*(:|$|\s)', re.I)
    for i, ln in enumerate(lines):
        if pat.match(ln):
            start = i
            break
    if start is None:
        return None

    # the next ACTOR ends this one
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r'^\s*ACTOR\s+', lines[i], re.I):
            end = i
            break

    body = lines[start:end]
    for i, ln in enumerate(body):
        if re.match(r'^\s*States\s*$', ln, re.I):
            return body[i + 1:]
    return body


def walk(body, label):
    """Enumerate tic-bearing states from `label`, following one Goto."""
    # index the labels
    labels = {}
    for i, ln in enumerate(body):
        m = LABEL_RE.match(ln)
        if m:
            labels[m.group(1).lower()] = i

    if label.lower() not in labels:
        return None, sorted(labels)

    out = []
    runs = []          # distinct sprite runs, in order
    last_spr = None
    step = 0
    i = labels[label.lower()] + 1
    seen_goto = set()
    guard = 0

    while i < len(body) and guard < 4000:
        guard += 1
        ln = body[i]

        if LABEL_RE.match(ln):
            i += 1
            continue

        g = GOTO_RE.match(ln)
        if g:
            # DO NOT FOLLOW. A Goto near the top of a Reload label is almost
            # always a guard -- "can't reload, go back to Ready" -- and following
            # it enumerates the wrong chain entirely. Later ones leave for a
            # continuation label like FinishReloading, which is a separate card
            # entry anyway. Report where it goes and stop; the reader decides.
            # Note it and KEEP WALKING. A Goto ends that state's flow, but the
            # lines after it are still reachable: DECORATE's relative jumps
            # (A_JumpIfInventory(x, n, 3)) hop over it. Stopping here would miss
            # the entire real reload, which sits just past the "no ammo" exit.
            out.append(("GOTO", "Goto " + g.group(1),
                        "<- conditional exit; chain continues below"))
            i += 1
            continue

        if STOPLIKE_RE.match(ln):
            out.append(("END", ln.strip(), ""))
            break

        m = STATE_RE.match(ln)
        if not m:
            i += 1
            continue

        spr = m.group("spr").strip('"')
        frames = m.group("frames").strip('"')
        tics = int(m.group("tics"))
        rest = m.group("rest").strip()

        if tics <= 0:
            out.append(("zero", "%s %s" % (spr, frames), rest))
            i += 1
            continue

        if spr not in ("#", "####") and spr != last_spr:
            if spr not in runs:
                runs.append(spr)
            last_spr = spr

        run = runs.index(last_spr) if last_spr in runs else -1

        for ch in frames:
            fi = frame_index(ch)
            out.append(("tic", step, run, ch, fi, spr, tics, rest))
            step += 1
            rest = ""       # the action is on the first frame of the run only

        i += 1

    return (out, runs), sorted(labels)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Map a weapon's reload chain.")
    ap.add_argument("file")
    ap.add_argument("actor")
    ap.add_argument("--label", default="Reload")
    ap.add_argument("--labels", action="store_true", help="just list state labels")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.file):
        sys.stderr.write("no such file: %s\n" % args.file)
        return 2

    body = extract_actor(args.file, args.actor)
    if body is None:
        sys.stderr.write("no ACTOR %s in %s\n" % (args.actor, args.file))
        return 1

    res, labels = walk(body, args.label)
    if res is None:
        print("no label %r. labels present:" % args.label)
        for l in labels:
            print("   ", l)
        return 1

    out, runs = res
    print("%s :: %s    label %s" % (os.path.basename(args.file), args.actor, args.label))
    print("sprite runs, in order: %s" % (", ".join("%d=%s" % (i, r) for i, r in enumerate(runs)) or "none"))
    print()
    print("  %-5s %-4s %-6s %-5s %-5s %s" % ("STEP", "RUN", "SPRITE", "FRAME", "TICS", "action / note"))
    for row in out:
        if row[0] == "zero":
            print("  %-5s %-4s %-6s %-5s %-5s %s" % ("", "", "", "", "0", "%s   %s" % (row[1], row[2])))
        elif row[0] in ("GOTO", "END"):
            print("  %-5s %-4s %-6s %-5s %-5s %s %s" % ("", "", "", "", "", row[1], row[2]))
        else:
            _, step, run, ch, fi, spr, tics, rest = row
            print("  %-5d %-4d %-6s %-5s %-5d %s" % (step, run, spr, "%s=%d" % (ch, fi), tics, rest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
