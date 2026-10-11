#!/usr/bin/env python3
"""Survey an MD3's frames: real-world size, and which frames are distinct poses.

TWO QUESTIONS THIS ANSWERS WITHOUT A HEADSET
--------------------------------------------

1. WHAT MODELDEF SCALE MAKES THE MESH LIFE-SIZED.

   The hook's frame is 1 model unit = 1 cm times the MODELDEF Scale
   (models.cpp:225 scale 0.01, hw_openxrdevice.cpp:442 vr_vunits_per_meter 34:
   0.01 * 34 = 0.34 map units per model unit, and 34 units = 1 m, so one model
   unit is 1 cm at Scale 1.0).

   So a hand mesh whose longest axis spans N model units is N cm long at
   Scale 1.0. An adult hand is about 18.5 cm wrist crease to middle fingertip.
   That gives the scale outright instead of guessing 1.0 and sliding.

2. WHICH FRAMES ARE ACTUALLY DISTINCT POSES.

   Vertex-animated hands store a pose per frame, but consecutive frames inside a
   held pose are identical. Reporting the frames where the mesh actually CHANGES
   gives the pose list -- and the frame index to put in a MODELDEF FrameIndex
   line -- rather than eyeballing 211 frames.

   It also prices the trim the plan mentions: frames no MODELDEF line plays can
   be dropped with nothing visible changing.

USAGE
-----
    python md3_pose_survey.py <file.md3> --bbox
    python md3_pose_survey.py <file.md3> --bbox --hand-cm 18.5
    python md3_pose_survey.py <file.md3> --poses
    python md3_pose_survey.py <file.md3> --poses --tol 0.05
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md3_part_track import read_md3  # noqa: E402


def all_verts(md3, frame):
    """Every vertex of every surface in one frame, renderer axis order."""
    out = []
    for s in md3["surfaces"]:
        f = frame if frame < s.num_frames else s.num_frames - 1
        for x, y, z in s.verts[f]:
            out.append((x, z, y))  # models_md3.cpp:282 Set(x, z, y)
    return out


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def rms_change(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    tot = 0.0
    for i in range(n):
        dx = a[i][0] - b[i][0]
        dy = a[i][1] - b[i][1]
        dz = a[i][2] - b[i][2]
        tot += dx * dx + dy * dy + dz * dz
    return (tot / n) ** 0.5


def do_bbox(md3, hand_cm):
    print("size, measured at every frame (model units = cm at MODELDEF Scale 1.0)")
    print()
    widest = 0.0
    widest_frame = 0
    for f in range(md3["num_frames"]):
        pts = all_verts(md3, f)
        if not pts:
            continue
        lo, hi = bbox(pts)
        span = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        longest = max(span)
        if longest > widest:
            widest = longest
            widest_frame = f

    pts = all_verts(md3, widest_frame)
    lo, hi = bbox(pts)
    span = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])

    print("  longest extent is at frame %d" % widest_frame)
    print("    X %8.3f .. %8.3f   span %7.3f" % (lo[0], hi[0], span[0]))
    print("    Y %8.3f .. %8.3f   span %7.3f" % (lo[1], hi[1], span[1]))
    print("    Z %8.3f .. %8.3f   span %7.3f" % (lo[2], hi[2], span[2]))
    print("    longest axis: %.3f model units = %.3f cm at Scale 1.0" % (widest, widest))
    print()
    if hand_cm > 0:
        print("  for a %.1f cm hand, MODELDEF Scale = %.4f" % (hand_cm, hand_cm / widest))
        print("  (a starting number derived from the mesh, not a guess;")
        print("   the long axis may not be the one you want to match)")


def do_poses(md3, tol):
    n = md3["num_frames"]
    print("distinct poses at tolerance %.4f model units RMS" % tol)
    print()

    prev = all_verts(md3, 0)
    reps = [0]
    runs = [[0, 0]]  # [first, last]

    for f in range(1, n):
        cur = all_verts(md3, f)
        if rms_change(prev, cur) <= tol:
            runs[-1][1] = f
        else:
            reps.append(f)
            runs.append([f, f])
        prev = cur

    print("  %d frames -> %d distinct poses" % (n, len(reps)))
    print()
    print("  %-8s %-14s %s" % ("pose", "frames", "held"))
    for i, (a, b) in enumerate(runs):
        held = b - a + 1
        rng = "%d" % a if a == b else "%d-%d" % (a, b)
        print("  %-8d %-14s %d" % (i, rng, held))
    print()
    print("  FrameIndex frame numbers to use: %s"
          % ", ".join(str(r[0]) for r in runs))
    print()
    kept = len(reps)
    print("  trimming to one frame per pose: %d of %d frames, about %.0f%% saved"
          % (kept, n, 100.0 * (n - kept) / n if n else 0.0))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Survey MD3 size and distinct poses.")
    ap.add_argument("model")
    ap.add_argument("--bbox", action="store_true", help="real-world size and the scale it implies")
    ap.add_argument("--poses", action="store_true", help="which frames are distinct poses")
    ap.add_argument("--hand-cm", type=float, default=18.5,
                    help="reference length for the scale, default 18.5 (adult hand)")
    ap.add_argument("--tol", type=float, default=0.02,
                    help="RMS model units below which two frames are the same pose")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.model):
        sys.stderr.write("no such file: %s\n" % args.model)
        return 2

    md3 = read_md3(args.model)
    print("%s" % os.path.basename(args.model))
    print("  internal name : %s" % md3["name"])
    print("  frames        : %d" % md3["num_frames"])
    print("  surfaces      : %d" % len(md3["surfaces"]))
    print("  verts/frame   : %d" % sum(s.num_verts for s in md3["surfaces"]))
    print()

    if not args.bbox and not args.poses:
        args.bbox = args.poses = True

    if args.bbox:
        do_bbox(md3, args.hand_cm)
        print()
    if args.poses:
        do_poses(md3, args.tol)

    return 0


if __name__ == "__main__":
    sys.exit(main())
