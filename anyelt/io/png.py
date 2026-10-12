"""
Pure Python zero-dependency PNG encoder.
Produces valid PNG 1.2 bitstreams using zlib and struct from the standard library.
"""

import struct
import zlib


def encode_grayscale8(pixels: bytes, width: int, height: int) -> bytes:
    """Encode 8-bit grayscale raw bytes to standard PNG."""
    return _encode(pixels, width, height, color_type=0, bit_depth=8, bytes_per_pixel=1)


def encode_rgb24(pixels: bytes, width: int, height: int) -> bytes:
    """Encode 24-bit RGB raw bytes to standard PNG."""
    return _encode(pixels, width, height, color_type=2, bit_depth=8, bytes_per_pixel=3)


def _encode(pixels: bytes, width: int, height: int, color_type: int, bit_depth: int, bytes_per_pixel: int) -> bytes:
    png_sig = b"\x89PNG\r\n\x1a\n"
    stride = width * bytes_per_pixel

    # Build scanlines with filter type 0 (None)
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)
        src_offset = y * stride
        chunk = pixels[src_offset:src_offset + stride]
        if len(chunk) < stride:
            chunk = chunk + b"\x80" * (stride - len(chunk))
        scanlines.extend(chunk)

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    ihdr_chunk = _make_chunk(b"IHDR", ihdr_data)

    # IDAT
    compressed = zlib.compress(bytes(scanlines))
    idat_chunk = _make_chunk(b"IDAT", compressed)

    # IEND
    iend_chunk = _make_chunk(b"IEND", b"")

    return png_sig + ihdr_chunk + idat_chunk + iend_chunk


def _make_chunk(chunk_type: bytes, data: bytes) -> bytes:
    length = len(data)
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", length) + chunk_type + data + struct.pack(">I", crc)
