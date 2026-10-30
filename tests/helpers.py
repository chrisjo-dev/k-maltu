"""테스트 공용 도우미. scripts/를 sys.path 맨 뒤에 붙인다(scripts/inspect.py가 표준 inspect를 가리지 않게)."""

import importlib.util
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
if str(SCRIPTS) not in sys.path:
    sys.path.append(str(SCRIPTS))


def load_inspect():
    """scripts/inspect.py를 표준 inspect와 다른 이름으로 불러온다."""
    spec = importlib.util.spec_from_file_location("maltu_inspect", SCRIPTS / "inspect.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def png_chunk(ctype: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + ctype + data + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)


def read_png_chunks(data: bytes):
    """테스트용 독립 파서. (type, data, crc_ok) 목록. clean_images의 파서를 쓰지 않는다."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "PNG 시그니처 아님"
    pos, out = 8, []
    while pos < len(data):
        (n,) = struct.unpack(">I", data[pos:pos + 4])
        t = data[pos + 4:pos + 8]
        d = data[pos + 8:pos + 8 + n]
        (crc,) = struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])
        out.append((t, d, zlib.crc32(t + d) & 0xFFFFFFFF == crc))
        pos += 12 + n
    return out


def jpeg_segment(marker: int, payload: bytes) -> bytes:
    return bytes([0xFF, marker]) + struct.pack(">H", len(payload) + 2) + payload


def exif_with_orientation(value: int) -> bytes:
    """IFD0에 Orientation 태그 하나만 있는 빅엔디언 EXIF APP1 페이로드."""
    tiff = b"MM\x00\x2a" + struct.pack(">I", 8) + struct.pack(">H", 1)
    tiff += struct.pack(">HHIHH", 0x0112, 3, 1, value, 0) + struct.pack(">I", 0)
    return b"Exif\x00\x00" + tiff
