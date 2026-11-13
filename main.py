#!/usr/bin/env python3
"""make.fun news-image-01 entry: "13 November 2026 — The Day in Five Stories".

Copies the pre-rendered front-page collage (art.png, in this repo) to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png) and self-checks the
output: valid PNG magic bytes, file size <= 1 MiB, dimensions <= 1024x1024.

Stdlib only, no network, deterministic: the output is byte-identical to
art.png on every run.
"""

import hashlib
import os
import shutil
import struct
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art.png")
MAX_BYTES = 1 * 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data: bytes) -> tuple:
    """Return (width, height) from the PNG IHDR chunk."""
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file (bad magic bytes)")
    # IHDR: length (4 bytes) + type "IHDR" (4 bytes) + width (4) + height (4)
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    ihdr_type = data[12:16]
    if ihdr_type != b"IHDR" or ihdr_len != 13:
        raise ValueError("not a PNG file (bad IHDR chunk)")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main() -> int:
    if not os.path.isfile(SRC):
        print(f"FAIL: source image not found: {SRC}", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    shutil.copyfile(SRC, out_path)
    print(f"copied {SRC} -> {out_path}")

    with open(out_path, "rb") as f:
        data = f.read()

    if len(data) > MAX_BYTES:
        print(f"FAIL: entry.png is {len(data)} bytes (> {MAX_BYTES})", file=sys.stderr)
        return 1

    width, height = png_dimensions(data)
    if width > MAX_DIM or height > MAX_DIM:
        print(f"FAIL: entry.png is {width}x{height} (> {MAX_DIM}x{MAX_DIM})",
              file=sys.stderr)
        return 1

    digest = hashlib.sha256(data).hexdigest()
    print(f"entry.png: {len(data)} bytes, {width}x{height}, sha256={digest}")
    print("OK: entry.png is a valid PNG within size limits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
