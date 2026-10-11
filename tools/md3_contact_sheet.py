#!/usr/bin/env python3
"""Render an MD3's frames as a labelled contact sheet, so poses can be PICKED.

WHY
---
Steps 3 and 4 need somebody to choose frames: which frame of hand2.md3 is the
grip, which of hand.md3's poses are open / relaxed / pinch / cup. Those are
look-at-it calls, and numbers are a terrible way to make them. A sheet of
labelled thumbnails is the right instrument.

See also md3_pose_survey.py --poses, which prints which frames are actually
distinct so this sheet does not waste 131 tiles on held duplicates.

HOW
---
Orthographic projection, painter's algorithm (triangles sorted back to front),
flat Lambert shading. No z-buffer: for a closed hand mesh the depth sort is
visually sufficient, and it keeps this fast enough for 200 frames.

Axis order is the renderer's, after the swap at models_md3.cpp:282
Set(x, z, y): X right, Y up, Z back toward the viewer.

USAGE
-----
    python md3_contact_sheet.py models/hand.md3 -o sheet.png
    python md3_contact_sheet.py models/hand.md3 -o sheet.png --distinct
    python md3_contact_sheet.py models/hand2.md3 -o gun.png --view iso --fit common
    python md3_contact_sheet.py models/hand.md3 -o s.png --frames 0,47,100 --tile 320

    --fit tile    (default) each frame centred and scaled to fill its tile.
                  Best for judging POSE.
    --fit common  one scale and origin for every tile. Best for judging MOTION
                  -- which is what hand2.md3 needs, since its frames carry
                  position as well as pose.
"""

import argparse
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md3_part_track import read_md3  # noqa: E402

BG = (24, 24, 28)
LABEL = (235, 235, 235)
LABEL_DIM = (130, 130, 140)
GRID = (52, 52, 60)
LIGHT = (-0.35, 0.62, 0.70)   # from upper-left-front


def norm(v):
    m = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if m == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / m, v[1] / m, v[2] / m)


def build_mesh(md3, frame):
    """All surfaces of one frame, merged. Renderer axis order."""
    verts = []
    tris = []
    for s in md3["surfaces"]:
        f = frame if frame < s.num_frames else s.num_frames - 1
        base = len(verts)
        for x, y, z in s.verts[f]:
            verts.append((x, z, y))   # models_md3.cpp:282
        for a, b, c in s.tris:
            tris.append((base + a, base + b, base + c))
    return verts, tris


def rotate(p, yaw_deg, pitch_deg):
    cy, sy = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    cp, sp = math.cos(math.radians(pitch_deg)), math.sin(math.radians(pitch_deg))
    x, y, z = p
    x, z = x * cy + z * sy, -x * sy + z * cy
    y, z = y * cp - z * sp, y * sp + z * cp
    return (x, y, z)


VIEWS = {
    "front": (0.0, 0.0),
    "side": (90.0, 0.0),
    "top": (0.0, 90.0),
    "iso": (35.0, 20.0),
}


def view_points(verts, view):
    yaw, pitch = VIEWS[view]
    return [rotate(v, yaw, pitch) for v in verts]


def bounds(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def draw_frame(md3, frame, view, tile, fit_box):
    verts, tris = build_mesh(md3, frame)
    return draw_verts(verts, tris, view, tile, fit_box)


def draw_verts(verts, tris, view, tile, fit_box):
    if not verts or not tris:
        return Image.new("RGB", (tile, tile), BG)

    pts = view_points(verts, view)

    if fit_box is None:
        x0, y0, x1, y1 = bounds(pts)
    else:
        x0, y0, x1, y1 = fit_box

    span = max(x1 - x0, y1 - y0, 1e-6)
    pad = tile * 0.08
    scale = (tile - 2 * pad) / span
    cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5

    def to_px(p):
        return (tile * 0.5 + (p[0] - cx) * scale,
                tile * 0.5 - (p[1] - cy) * scale)   # screen Y is down

    img = Image.new("RGB", (tile, tile), BG)
    dr = ImageDraw.Draw(img)

    # Painter's algorithm: furthest first. Depth is +Z toward the viewer, so
    # ascending Z draws back to front.
    order = []
    for t in tris:
        a, b, c = pts[t[0]], pts[t[1]], pts[t[2]]
        order.append(((a[2] + b[2] + c[2]) / 3.0, t))
    order.sort(key=lambda e: e[0])

    for _depth, t in order:
        a, b, c = pts[t[0]], pts[t[1]], pts[t[2]]
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        n = norm((u[1] * v[2] - u[2] * v[1],
                  u[2] * v[0] - u[0] * v[2],
                  u[0] * v[1] - u[1] * v[0]))
        lam = n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2]
        shade = 0.22 + 0.78 * max(0.0, abs(lam))
        g = int(max(0, min(255, shade * 232)))
        dr.polygon([to_px(a), to_px(b), to_px(c)],
                   fill=(g, int(g * 0.93), int(g * 0.86)))

    return img


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render MD3 frames as a contact sheet.")
    ap.add_argument("model")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--frames", help="e.g. 0,47,100 or 26-34. Default: all")
    ap.add_argument("--blend", metavar="A:B:N",
                    help="render N steps of the engine's vertex blend from frame "
                         "A to frame B. This is what models.cpp:367-405 actually "
                         "draws between two poses -- use it to check the path, "
                         "not just the endpoints.")
    ap.add_argument("--distinct", action="store_true",
                    help="only frames where the mesh actually changes")
    ap.add_argument("--tol", type=float, default=0.02, help="--distinct tolerance")
    ap.add_argument("--view", choices=sorted(VIEWS), default="iso")
    ap.add_argument("--fit", choices=("tile", "common"), default="tile")
    ap.add_argument("--tile", type=int, default=200)
    ap.add_argument("--cols", type=int, default=0, help="0 = auto")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.model):
        sys.stderr.write("no such file: %s\n" % args.model)
        return 2

    md3 = read_md3(args.model)
    n = md3["num_frames"]

    if args.blend:
        a_s, b_s, n_s = args.blend.split(":")
        fa, fb, steps = int(a_s), int(b_s), int(n_s)
        va, tris = build_mesh(md3, fa)
        vb, _ = build_mesh(md3, fb)

        tiles = []
        for i in range(steps):
            t = i / float(steps - 1) if steps > 1 else 0.0
            verts = [(va[k][0] + (vb[k][0] - va[k][0]) * t,
                      va[k][1] + (vb[k][1] - va[k][1]) * t,
                      va[k][2] + (vb[k][2] - va[k][2]) * t)
                     for k in range(min(len(va), len(vb)))]
            tiles.append((t, verts, tris))

        cols = args.cols or steps
        rows = int(math.ceil(len(tiles) / float(cols)))
        lab = 18
        cell = args.tile + lab
        sheet = Image.new("RGB", (cols * cell, rows * cell), BG)
        sd = ImageDraw.Draw(sheet)

        for i, (t, verts, tr) in enumerate(tiles):
            cx = (i % cols) * cell
            cy = (i // cols) * cell
            sheet.paste(draw_verts(verts, tr, args.view, args.tile, None), (cx, cy))
            sd.rectangle([cx, cy, cx + args.tile - 1, cy + args.tile - 1], outline=GRID)
            sd.text((cx + 4, cy + args.tile + 3), "inter %.2f" % t, fill=LABEL)

        sd.text((4, rows * cell - 14),
                "%s  |  engine blend  frame %d -> %d  |  %s view"
                % (os.path.basename(args.model), fa, fb, args.view), fill=LABEL_DIM)
        sheet.save(args.out)
        print("wrote %s  (blend %d->%d, %d steps)" % (args.out, fa, fb, steps))
        return 0

    if args.frames:
        frames = []
        for part in args.frames.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                frames.extend(range(int(a), int(b) + 1))
            else:
                frames.append(int(part))
        frames = [f for f in frames if 0 <= f < n]
    elif args.distinct:
        frames = [0]
        prev = build_mesh(md3, 0)[0]
        for f in range(1, n):
            cur = build_mesh(md3, f)[0]
            m = min(len(prev), len(cur))
            tot = 0.0
            for i in range(m):
                dx = prev[i][0] - cur[i][0]
                dy = prev[i][1] - cur[i][1]
                dz = prev[i][2] - cur[i][2]
                tot += dx * dx + dy * dy + dz * dz
            if m and (tot / m) ** 0.5 > args.tol:
                frames.append(f)
            prev = cur
    else:
        frames = list(range(n))

    if not frames:
        sys.stderr.write("no frames selected\n")
        return 1

    fit_box = None
    if args.fit == "common":
        xs0 = ys0 = 1e9
        xs1 = ys1 = -1e9
        for f in frames:
            pts = view_points(build_mesh(md3, f)[0], args.view)
            a, b, c, d = bounds(pts)
            xs0, ys0 = min(xs0, a), min(ys0, b)
            xs1, ys1 = max(xs1, c), max(ys1, d)
        fit_box = (xs0, ys0, xs1, ys1)

    cols = args.cols or max(1, int(math.ceil(math.sqrt(len(frames)))))
    rows = int(math.ceil(len(frames) / float(cols)))
    lab = 18
    cell = args.tile + lab

    sheet = Image.new("RGB", (cols * cell, rows * cell), BG)
    sd = ImageDraw.Draw(sheet)

    for i, f in enumerate(frames):
        cx = (i % cols) * cell
        cy = (i // cols) * cell
        sheet.paste(draw_frame(md3, f, args.view, args.tile, fit_box), (cx, cy))
        sd.rectangle([cx, cy, cx + args.tile - 1, cy + args.tile - 1], outline=GRID)
        sd.text((cx + 4, cy + args.tile + 3), "frame %d" % f, fill=LABEL)

    name = os.path.basename(args.model)
    sd.text((4, rows * cell - 14),
            "%s  |  %s view  |  fit %s  |  %d of %d frames"
            % (name, args.view, args.fit, len(frames), n),
            fill=LABEL_DIM)

    sheet.save(args.out)
    print("wrote %s  (%dx%d, %d tiles, %s view, fit %s)"
          % (args.out, sheet.width, sheet.height, len(frames), args.view, args.fit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
