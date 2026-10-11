#!/usr/bin/env python3
"""Emit the placeholder sprite lumps RS_QuestHands needs.

MODELDEF keys a model on (caller class, sprite, frame) -- models.cpp:1165. Every
layer therefore needs a state whose sprite and frame exist as a real lump, even
though the sprite itself is never seen: the model replaces it. These are 1x1
fully transparent PNGs.

Written with zlib and struct rather than pasted as base64, so the bytes are
provably a valid PNG instead of probably one.

Run from the pack root:  python tools/make_placeholder_sprites.py
"""

import os
import struct
import zlib

# sprite + frame -> one lump each. Frames must match the States blocks in
# zscript/qh_hands.zs.
LUMPS = [
    "QHNDA0",   # QH_Hands  Ready / Select / Deselect  (no model bound)
    "QHNDB0",   # QH_Hands  FreeHand   -> off controller
    "QHNDC0",   # QH_Hands  Carry      -> off controller
    "QHNDD0",   # QH_Hands  closed on the magazine (step 4 blend target)
    "QHNDE0",   # QH_Hands  carried rifle magazine
    "QHNDF0",   # QH_Hands  carried shotgun shell
    "QHGSA0",   # QH_GunSide GunHand   -> main controller
    "QHGSB0",   # QH_GunSide Support   -> main controller
    "QTSTA0",   # QH_TestGun Ready     -> main controller
] + [
    # QH_Debris: one frame per chunk mesh.
    #   A-D concrete   E-H brick   I-L dirt
    "QDBR%s0" % c for c in "ABCDEFGHIJKL"
]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites")


def chunk(tag: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def transparent_png_1x1() -> bytes:
    # bit depth 8, colour type 6 (RGBA), no interlace
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    # one scanline: filter byte 0, then RGBA = 0,0,0,0
    raw = b"\x00" + b"\x00\x00\x00\x00"
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    blob = transparent_png_1x1()
    for name in LUMPS:
        path = os.path.join(OUT_DIR, name + ".png")
        with open(path, "wb") as fh:
            fh.write(blob)
        print("wrote %s (%d bytes)" % (os.path.normpath(path), len(blob)))


if __name__ == "__main__":
    main()
