#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261117.

Copies the pre-built entry image (entry.png, made in-session) to the
output directory. Standard library only, no network, deterministic:
the same bytes are written on every run.

Before copying, the source image is validated: it must exist, be at
most 1 MiB, and be a PNG no larger than 1024x1024, its dimensions
read from the PNG IHDR header with struct (no imaging library, so
the program stays standard-library-only). Any failure is a clear
error on stderr with a non-zero exit code, and nothing is copied.
"""
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def png_dimensions(data):
    """(width, height) from the PNG IHDR chunk, or None if not a PNG."""
    if len(data) < 33 or data[:8] != PNG_SIGNATURE:
        return None
    length, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or length != 13:
        return None
    return struct.unpack(">II", data[16:24])


def main():
    if not SRC.is_file():
        return fail(f"entry image not found: {SRC}")
    try:
        data = SRC.read_bytes()
    except OSError as exc:
        return fail(f"cannot read entry image {SRC}: {exc}")
    if len(data) > MAX_BYTES:
        return fail(
            f"entry image is {len(data)} bytes, over the {MAX_BYTES}-byte limit"
        )
    dims = png_dimensions(data)
    if dims is None:
        return fail(f"entry image {SRC} is not a valid PNG file")
    width, height = dims
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        return fail(
            f"entry image is {width}x{height}, "
            f"over the {MAX_WIDTH}x{MAX_HEIGHT} limit"
        )
    try:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SRC, OUT_DIR / "entry.png")
    except OSError as exc:
        return fail(f"cannot write output image: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
