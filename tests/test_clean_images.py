import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

from helpers import FIXTURES, SCRIPTS, exif_with_orientation, jpeg_segment, png_chunk, read_png_chunks

from clean_images import FormatError, clean_bytes

W = H = 4
RAW = b"".join(b"\x00" + bytes([x * 60, y * 60, 200]) * 1 + bytes(3 * (W - 1)) for x, y in [(0, 0), (1, 1), (2, 2), (3, 3)])
COMPRESSED = zlib.compress(RAW)


def build_png(trailing: bytes = b"") -> bytes:
    half = len(COMPRESSED) // 2
    chunks = [
        png_chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)),
        png_chunk(b"iCCP", b"icc\x00\x00" + zlib.compress(b"fake profile")),
        png_chunk(b"gAMA", struct.pack(">I", 45455)),
        png_chunk(b"cHRM", bytes(32)),
        png_chunk(b"pHYs", struct.pack(">IIB", 2835, 2835, 1)),
        png_chunk(b"tEXt", b"Author\x00someone"),
        png_chunk(b"zTXt", b"Comment\x00\x00" + zlib.compress(b"secret")),
        png_chunk(b"iTXt", b"XML:com.adobe.xmp\x00\x00\x00\x00\x00<x:xmpmeta/>"),
        png_chunk(b"eXIf", b"MM\x00\x2a\x00\x00\x00\x08\x00\x00"),
        png_chunk(b"caBX", b"jumbf-c2pa"),
        png_chunk(b"c2pa", b"future c2 chunk"),
        png_chunk(b"tIME", bytes(7)),
        png_chunk(b"IDAT", COMPRESSED[:half]),
        png_chunk(b"IDAT", COMPRESSED[half:]),
        png_chunk(b"IEND", b""),
    ]
    return b"\x89PNG\r\n\x1a\n" + b"".join(chunks) + trailing


class PngTest(unittest.TestCase):
    def setUp(self):
        self.src = build_png(trailing=b"appended-payload")
        self.out, self.dropped, self.warnings = clean_bytes(self.src)
        self.src_chunks = read_png_chunks(self.src[: len(self.src) - len(b"appended-payload")])
        self.out_chunks = read_png_chunks(self.out)

    def test_metadata_chunks_removed(self):
        types = [t for t, _, _ in self.out_chunks]
        self.assertEqual(types, [b"IHDR", b"iCCP", b"gAMA", b"cHRM", b"pHYs", b"tIME", b"IDAT", b"IDAT", b"IEND"])
        self.assertEqual(self.dropped[:6], ["tEXt", "zTXt", "iTXt", "eXIf", "caBX", "c2pa"])
        self.assertIn("IEND 뒤 16바이트", self.dropped)
        for secret in (b"someone", b"xmpmeta", b"jumbf", b"appended-payload"):
            self.assertNotIn(secret, self.out)

    def test_valid_png_signature_and_crc(self):
        self.assertTrue(self.out.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertTrue(all(ok for _, _, ok in self.out_chunks))
        self.assertEqual(self.out_chunks[0][0], b"IHDR")
        self.assertEqual(self.out_chunks[-1][0], b"IEND")

    def test_idat_and_kept_chunks_byte_identical(self):
        idat = lambda cs: b"".join(d for t, d, _ in cs if t == b"IDAT")  # noqa: E731
        self.assertEqual(idat(self.out_chunks), idat(self.src_chunks))
        self.assertEqual(zlib.decompress(idat(self.out_chunks)), RAW)
        src_kept = [(t, d) for t, d, _ in self.src_chunks if t in {b"IHDR", b"iCCP", b"gAMA", b"cHRM", b"pHYs", b"tIME"}]
        out_kept = [(t, d) for t, d, _ in self.out_chunks if t not in {b"IDAT", b"IEND"}]
        self.assertEqual(out_kept, src_kept)

    def test_clean_png_unchanged(self):
        once = clean_bytes(build_png())[0]
        self.assertEqual(clean_bytes(once), (once, [], []))

    def test_truncated_png_rejected(self):
        with self.assertRaises(FormatError):
            clean_bytes(build_png()[:-6])


class JpegTest(unittest.TestCase):
    def setUp(self):
        self.base = (FIXTURES / "tiny_base.jpg").read_bytes()
        # tiny_base.jpg = SOI, APP0(JFIF), DQT/SOF/DHT/DRI ..., SOS, 스캔 데이터, EOI
        self.assertEqual(self.base[2:4], b"\xff\xe0")
        app0_end = 4 + struct.unpack(">H", self.base[4:6])[0]
        self.app2 = jpeg_segment(0xE2, b"ICC_PROFILE\x00\x01\x01fake-icc")
        injected = (
            jpeg_segment(0xE1, exif_with_orientation(6))
            + self.app2
            + jpeg_segment(0xE1, b"http://ns.adobe.com/xap/1.0/\x00<x:xmpmeta/>")
            + jpeg_segment(0xED, b"Photoshop 3.0\x008BIM iptc")
            + jpeg_segment(0xEB, b"JP\x00\x00c2pa-jumbf")
            + jpeg_segment(0xFE, b"comment by someone")
        )
        self.src = self.base[:app0_end] + injected + self.base[app0_end:]
        self.expected = self.base[:app0_end] + self.app2 + self.base[app0_end:]
        self.out, self.dropped, self.warnings = clean_bytes(self.src)

    def test_exact_bytes_after_removal(self):
        # APP0과 APP2는 남고, 나머지 세그먼트와 스캔 데이터는 바이트 그대로여야 한다.
        self.assertEqual(self.out, self.expected)
        self.assertEqual(self.dropped, ["APP1", "APP1", "APP13", "APP11", "COM"])

    def test_scan_data_identical(self):
        sos = self.src.index(b"\xff\xda")
        self.assertEqual(self.out[self.out.index(b"\xff\xda"):], self.src[sos:])
        self.assertTrue(self.out.endswith(b"\xff\xd9"))

    def test_app0_and_app2_kept(self):
        self.assertIn(b"JFIF\x00", self.out)
        self.assertIn(self.app2, self.out)
        for secret in (b"Exif", b"xmpmeta", b"8BIM", b"c2pa", b"someone"):
            self.assertNotIn(secret, self.out)

    def test_orientation_warning(self):
        self.assertTrue(any("회전" in w for w in self.warnings))

    def test_fill_bytes_before_marker(self):
        app0_end = 4 + struct.unpack(">H", self.base[4:6])[0]
        padded = self.base[:app0_end] + b"\xff" + jpeg_segment(0xFE, b"x") + self.base[app0_end:]
        out, dropped, _ = clean_bytes(padded)
        self.assertEqual(out, self.base)
        self.assertEqual(dropped, ["COM"])


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "clean_images.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_unsupported_format_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            gif = Path(d) / "a.gif"
            gif.write_bytes(b"GIF89a....")
            r = self.run_cli(gif)
            self.assertEqual(r.returncode, 0)
            self.assertIn("건너뜀", r.stdout)
            self.assertFalse((Path(d) / "a.cleaned.gif").exists())

    def test_out_dir_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.png"
            data = build_png()
            src.write_bytes(data)
            self.assertEqual(self.run_cli(src, "-d", d).returncode, 2)
            self.assertEqual(src.read_bytes(), data)
            r = self.run_cli(src, "-d", Path(d) / "out")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((Path(d) / "out" / "a.png").read_bytes(), clean_bytes(data)[0])
            self.assertEqual(src.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
