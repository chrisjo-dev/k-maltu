#!/usr/bin/env python3
"""이미지 메타데이터를 지운다. 표준 라이브러리만 쓰고, 픽셀 데이터는 다시 인코딩하지 않는다.

- PNG: tEXt, zTXt, iTXt, eXIf, caBX, c2로 시작하는 청크를 뺀다. IHDR, PLTE, IDAT, IEND와
  iCCP, gAMA, cHRM, sRGB, pHYs 같은 표시용 청크는 원래 바이트(CRC 포함) 그대로 둔다.
- JPEG: APP1(EXIF/XMP), APP11(C2PA/JUMBF), APP13(IPTC/Photoshop), COM을 뺀다.
  APP0(JFIF), APP2(ICC 등), APP14(Adobe)와 나머지 세그먼트, 첫 SOS 이후 데이터는 그대로 복사한다.
- 그 밖의 형식은 건너뛰고 경고한다.

입력 파일은 덮어쓰지 않는다.
사용 예:
  python3 scripts/clean_images.py images/*.png -d out/images
  python3 scripts/clean_images.py photo.jpg            # photo.cleaned.jpg 생성
"""

from __future__ import annotations

import os
import sys

import argparse
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_DROP = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"caBX"}

JPEG_DROP = {0xE1: "APP1", 0xEB: "APP11", 0xED: "APP13", 0xFE: "COM"}
# 길이 필드가 없는 단독 마커
_JPEG_STANDALONE = {0x01, *range(0xD0, 0xD8)}


class FormatError(ValueError):
    pass


@dataclass
class Chunk:
    """PNG 청크 하나 또는 JPEG 세그먼트 하나. raw는 파일에 있던 바이트 그대로."""

    name: str
    raw: bytes
    payload: bytes
    drop: bool
    crc_ok: bool = True


def is_png_drop(ctype: bytes) -> bool:
    return ctype in PNG_DROP or ctype.startswith(b"c2")


def parse_png(data: bytes) -> list[Chunk]:
    if not data.startswith(PNG_SIG):
        raise FormatError("PNG 시그니처가 아닙니다")
    pos = len(PNG_SIG)
    chunks: list[Chunk] = []
    while pos < len(data):
        if pos + 12 > len(data):
            raise FormatError("PNG 청크가 중간에 잘렸습니다")
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            raise FormatError(f"{ctype!r} 청크 길이가 파일보다 깁니다")
        payload = data[pos + 8:pos + 8 + length]
        (crc,) = struct.unpack(">I", data[end - 4:end])
        crc_ok = zlib.crc32(ctype + payload) & 0xFFFFFFFF == crc
        chunks.append(Chunk(ctype.decode("latin-1"), data[pos:end], payload, is_png_drop(ctype), crc_ok))
        pos = end
        if ctype == b"IEND":
            break
    if not chunks or chunks[-1].name != "IEND":
        raise FormatError("IEND 청크가 없습니다")
    return chunks


def parse_jpeg(data: bytes) -> tuple[list[Chunk], bytes]:
    """첫 SOS 전까지의 세그먼트 목록과, SOS부터 파일 끝까지의 나머지 바이트를 돌려준다."""
    if not data.startswith(b"\xff\xd8"):
        raise FormatError("JPEG SOI가 아닙니다")
    segs = [Chunk("SOI", data[:2], b"", False)]
    pos = 2
    while pos < len(data):
        if data[pos] != 0xFF:
            raise FormatError(f"JPEG 마커 위치가 어긋났습니다(offset {pos})")
        m = pos
        while m < len(data) and data[m] == 0xFF:  # 채움 바이트 0xFF 건너뛰기
            m += 1
        if m >= len(data):
            raise FormatError("JPEG가 마커 중간에 끝났습니다")
        marker = data[m]
        if marker == 0xDA:  # SOS: 여기부터 끝까지 그대로 복사
            return segs, data[pos:]
        if marker in _JPEG_STANDALONE:
            segs.append(Chunk(f"FF{marker:02X}", data[pos:m + 1], b"", False))
            pos = m + 1
            continue
        if marker == 0xD9:
            raise FormatError("SOS 전에 EOI가 나왔습니다")
        if m + 3 > len(data):
            raise FormatError("JPEG 세그먼트 길이가 잘렸습니다")
        (length,) = struct.unpack(">H", data[m + 1:m + 3])
        end = m + 1 + length
        if length < 2 or end > len(data):
            raise FormatError(f"FF{marker:02X} 세그먼트 길이가 잘못됐습니다")
        if 0xE0 <= marker <= 0xEF:
            name = f"APP{marker - 0xE0}"
        else:
            name = JPEG_DROP.get(marker, f"FF{marker:02X}")
        segs.append(Chunk(name, data[pos:end], data[m + 3:end], marker in JPEG_DROP))
        pos = end
    raise FormatError("SOS 세그먼트가 없습니다")


def exif_orientation(app1_payload: bytes) -> int | None:
    """APP1 EXIF의 IFD0에서 Orientation(0x0112) 값을 읽는다. 없으면 None."""
    if not app1_payload.startswith(b"Exif\x00\x00"):
        return None
    tiff = app1_payload[6:]
    if len(tiff) < 8:
        return None
    bo = {b"II": "<", b"MM": ">"}.get(tiff[:2])
    if bo is None:
        return None
    try:
        (ifd,) = struct.unpack(bo + "I", tiff[4:8])
        (count,) = struct.unpack(bo + "H", tiff[ifd:ifd + 2])
        for i in range(count):
            e = ifd + 2 + 12 * i
            tag, typ, _n = struct.unpack(bo + "HHI", tiff[e:e + 8])
            if tag == 0x0112 and typ == 3:
                return struct.unpack(bo + "H", tiff[e + 8:e + 10])[0]
    except struct.error:
        return None
    return None


def detect(data: bytes) -> str | None:
    if data.startswith(PNG_SIG):
        return "png"
    if data.startswith(b"\xff\xd8"):
        return "jpeg"
    return None


def clean_bytes(data: bytes) -> tuple[bytes, list[str], list[str]]:
    """(정리된 바이트, 지운 항목 이름 목록, 경고 목록)."""
    kind = detect(data)
    warnings: list[str] = []
    if kind == "png":
        chunks = parse_png(data)
        bad = [c.name for c in chunks if not c.crc_ok and not c.drop]
        if bad:
            warnings.append(f"CRC가 맞지 않는 청크가 원본에 있습니다(그대로 둠): {', '.join(bad)}")
        kept = b"".join(c.raw for c in chunks if not c.drop)
        dropped = [c.name for c in chunks if c.drop]
        tail = len(data) - len(PNG_SIG) - sum(len(c.raw) for c in chunks)
        if tail:
            dropped.append(f"IEND 뒤 {tail}바이트")
        return PNG_SIG + kept, dropped, warnings
    if kind == "jpeg":
        segs, rest = parse_jpeg(data)
        for s in segs:
            if s.name == "APP1":
                o = exif_orientation(s.payload)
                if o not in (None, 1):
                    warnings.append(f"EXIF 회전 값 {o}이(가) 사라져 이미지가 돌아가 보일 수 있습니다")
        if not rest.endswith(b"\xff\xd9"):
            warnings.append("EOI 뒤에 데이터가 있거나 EOI가 없습니다(그대로 둠, 직접 확인 필요)")
        kept = b"".join(s.raw for s in segs if not s.drop)
        return kept + rest, [s.name for s in segs if s.drop], warnings
    raise FormatError("지원하지 않는 형식(PNG, JPEG만 처리)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="이미지 메타데이터 정리(원본 유지)")
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("-d", "--out-dir", type=Path, help="같은 파일 이름으로 이 폴더에 저장(원본 폴더는 안 됨)")
    ap.add_argument("--force", action="store_true", help="출력 파일이 이미 있으면 덮어쓴다")
    args = ap.parse_args(argv)

    status = 0
    for src in args.inputs:
        if args.out_dir:
            dst = args.out_dir / src.name
        else:
            dst = src.with_name(f"{src.stem}.cleaned{src.suffix}")
        data = src.read_bytes()
        try:
            out, dropped, warnings = clean_bytes(data)
        except FormatError as e:
            print(f"[건너뜀] {src}: {e}")
            continue
        if dst.resolve() == src.resolve():
            print(f"[오류] {src}: 입력을 덮어쓸 수 없습니다", file=sys.stderr)
            status = 2
            continue
        if dst.exists() and not args.force:
            print(f"[오류] {dst} 이(가) 이미 있습니다. 덮어쓰려면 --force", file=sys.stderr)
            status = 2
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(out)
        removed = ", ".join(dropped) if dropped else "없음"
        print(f"[정리] {src} -> {dst}  지움: {removed}  ({len(data)} -> {len(out)} bytes)")
        for w in warnings:
            print(f"  경고: {w}")
    return status


if __name__ == "__main__":
    sys.exit(main())
