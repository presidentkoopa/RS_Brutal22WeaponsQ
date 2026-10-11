#!/usr/bin/env python3
"""Track where each surface of an MD3 sits, frame by frame.

WHY THIS EXISTS
---------------
Step 3 of the plan keeps a hand on a part the animation moves -- the magazine
going into the rifle. The hook cannot ask the engine where that part is: there
is no bone control from script of any kind on stock QZD, and one rigid
transform per layer. So the part's position is measured ONCE, offline, per
frame, and the hook replays it.

This prints that table.

WHAT IT MEASURES
----------------
MD3 is vertex-animated: every frame stores every vertex outright. A surface's
position in a frame is therefore just the centroid of its vertices in that
frame. That is what the hand follows.

Centroid, not bounding-box centre, on purpose: a magazine's bbox centre jumps
when a single stray vertex enters or leaves, while the centroid moves smoothly,
which is what a hand riding it needs.

UNITS
-----
MD3 stores int16 coordinates scaled by 1/64. Output is in those model units and
in the hook's own frame after the axis swap the engine does at
models_md3.cpp:282:

    bvert->Set(vert->x, vert->z, vert->y, ...)

so model (x, y, z) is handed to the renderer as (x, z, y). The columns below are
already swapped, i.e. they are what ModifyBobLayer3D's translation space sees:
X right, Y up, Z back toward the player.

Scale is NOT applied. Multiply by the MODELDEF Scale yourself -- VR_Rifle is
1.35 uniform.

USAGE
-----
    python md3_part_track.py <file.md3>
    python md3_part_track.py <file.md3> --frames 26-34
    python md3_part_track.py <file.md3> --frames 26-34 --surface mag
    python md3_part_track.py <file.md3> --frames 26-34 --surface mag --delta

This belongs in CardKit once it has earned its keep; it is here while step 3 is
being built.
"""

import argparse
import os
import struct
import sys

MD3_MAGIC = b"IDP3"
MD3_SCALE = 1.0 / 64.0


def _cstr(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("latin-1", "replace").strip()


class Surface:
    __slots__ = ("name", "num_frames", "num_verts", "verts", "tris")

    def __init__(self, name, num_frames, num_verts, verts, tris=None):
        self.name = name
        self.num_frames = num_frames
        self.num_verts = num_verts
        self.verts = verts  # [frame][vert] -> (x, y, z) in model units
        self.tris = tris or []  # [(a, b, c), ...] vertex indices, shared by all frames

    def centroid(self, frame):
        """Mean vertex position for one frame, in the renderer's axis order."""
        vs = self.verts[frame]
        n = len(vs)
        if n == 0:
            return (0.0, 0.0, 0.0)
        sx = sy = sz = 0.0
        for x, y, z in vs:
            sx += x
            sy += y
            sz += z
        # models_md3.cpp:282 -- Set(x, z, y): model Y and Z swap on upload.
        return (sx / n, sz / n, sy / n)


def read_md3(path):
    with open(path, "rb") as fh:
        blob = fh.read()

    if blob[:4] != MD3_MAGIC:
        raise ValueError("not an MD3 (magic is %r, expected %r)" % (blob[:4], MD3_MAGIC))

    # header: magic, version, name[64], flags, numFrames, numTags,
    #         numSurfaces, numSkins, ofsFrames, ofsTags, ofsSurfaces, ofsEnd
    (_magic, version, name, _flags, num_frames, _num_tags,
     num_surfaces, _num_skins, _ofs_frames, _ofs_tags,
     ofs_surfaces, _ofs_end) = struct.unpack_from("<4si64s9i", blob, 0)

    surfaces = []
    off = ofs_surfaces
    for _ in range(num_surfaces):
        (_ident, s_name, _s_flags, s_frames, _s_shaders, s_verts,
         s_tris, ofs_tris, _ofs_shaders, _ofs_st,
         ofs_xyz, s_ofs_end) = struct.unpack_from("<4s64s10i", blob, off)

        # Triangles are one list shared by every frame -- MD3 animates vertices,
        # never topology.
        tris = []
        if s_tris > 0:
            raw = struct.unpack_from("<%di" % (s_tris * 3), blob, off + ofs_tris)
            for t in range(s_tris):
                i = t * 3
                tris.append((raw[i], raw[i + 1], raw[i + 2]))

        frames = []
        for f in range(s_frames):
            base = off + ofs_xyz + f * s_verts * 8
            raw = struct.unpack_from("<%dh" % (s_verts * 4), blob, base)
            pts = []
            for v in range(s_verts):
                i = v * 4
                pts.append((raw[i] * MD3_SCALE,
                            raw[i + 1] * MD3_SCALE,
                            raw[i + 2] * MD3_SCALE))
            frames.append(pts)

        surfaces.append(Surface(_cstr(s_name), s_frames, s_verts, frames, tris))
        off += s_ofs_end

    return {
        "name": _cstr(name),
        "version": version,
        "num_frames": num_frames,
        "surfaces": surfaces,
    }


def parse_frames(spec, limit):
    if not spec:
        return list(range(limit))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    bad = [f for f in out if f < 0 or f >= limit]
    if bad:
        raise ValueError("frame(s) out of range 0..%d: %s" % (limit - 1, bad))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Track MD3 surface positions per frame.")
    ap.add_argument("model")
    ap.add_argument("--frames", help="e.g. 26-34 or 0,5,9. Default: all")
    ap.add_argument("--surface", action="append", default=None,
                    help="case-insensitive substring; repeatable. Default: all")
    ap.add_argument("--delta", action="store_true",
                    help="also show movement from the first listed frame")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.model):
        sys.stderr.write("no such file: %s\n" % args.model)
        return 2

    md3 = read_md3(args.model)

    print("%s" % os.path.basename(args.model))
    print("  internal name : %s" % md3["name"])
    print("  frames        : %d" % md3["num_frames"])
    print("  surfaces      : %d" % len(md3["surfaces"]))
    print()

    picked = md3["surfaces"]
    if args.surface:
        needles = [s.lower() for s in args.surface]
        picked = [s for s in picked
                  if any(n in s.name.lower() for n in needles)]
        if not picked:
            print("no surface matched %s. present:" % args.surface)
            for s in md3["surfaces"]:
                print("    %-28s %5d verts  %4d frames" % (s.name, s.num_verts, s.num_frames))
            return 1

    for s in picked:
        frames = parse_frames(args.frames, s.num_frames)
        print("surface %r  -- %d verts, %d frames" % (s.name, s.num_verts, s.num_frames))
        print("  (columns are the hook's frame: X right, Y up, Z back. Model units,")
        print("   MODELDEF Scale NOT applied.)")
        if args.delta:
            print("  %-7s %9s %9s %9s   %9s %9s %9s %9s"
                  % ("frame", "X", "Y", "Z", "dX", "dY", "dZ", "|d|"))
        else:
            print("  %-7s %9s %9s %9s" % ("frame", "X", "Y", "Z"))

        ref = s.centroid(frames[0]) if frames else (0.0, 0.0, 0.0)
        for f in frames:
            c = s.centroid(f)
            if args.delta:
                d = (c[0] - ref[0], c[1] - ref[1], c[2] - ref[2])
                mag = (d[0] ** 2 + d[1] ** 2 + d[2] ** 2) ** 0.5
                print("  %-7d %9.3f %9.3f %9.3f   %9.3f %9.3f %9.3f %9.3f"
                      % (f, c[0], c[1], c[2], d[0], d[1], d[2], mag))
            else:
                print("  %-7d %9.3f %9.3f %9.3f" % (f, c[0], c[1], c[2]))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
