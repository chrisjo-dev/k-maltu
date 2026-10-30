#!/usr/bin/env python3
"""점검 보고(읽기 전용). 파일을 바꾸거나 새로 쓰지 않는다.

텍스트(.md, .txt 등):
  - 숨은 문자 종류와 개수, 코드포인트, 줄 번호(종류마다 앞 10곳), 코드 블록 안인지 여부
  - 공백 동형 문자(U+00A0, U+3000 등)
  - 개인정보 후보: IPv4, 이메일, 한국 휴대폰 번호, 주민등록번호 형식(값은 일부 가려서 표시)
이미지(PNG, JPEG):
  - 메타데이터 청크/세그먼트 이름, 크기, 정리 때 지울지 여부, 텍스트 청크의 키워드

사용 예:
  python3 scripts/inspect_report.py draft.md images/*.png
"""

from __future__ import annotations

import os
import sys

import argparse
import re
from pathlib import Path

from clean_images import FormatError, detect, parse_jpeg, parse_png  # noqa: E402
from mdsegments import TEXT, line_of, split_markdown, text_unicode  # noqa: E402

_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "IPv4": re.compile(rf"(?<![\d.]){_OCTET}(?:\.{_OCTET}){{3}}(?![\d.]|\.\d)"),
    "이메일": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    "휴대폰 번호": re.compile(r"(?<!\d)01[016789][- .]?\d{3,4}[- .]?\d{4}(?!\d)"),
    "주민등록번호 형식": re.compile(r"(?<!\d)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])-?[1-8]\d{6}(?!\d)"),
}

_IMAGE_INFO_ONLY = {"tIME"}  # 지우지는 않지만 알려 둘 만한 PNG 청크


def mask(value: str) -> str:
    """앞뒤 일부만 남기고 가린다. 보고서가 그대로 공유돼도 원값이 다 드러나지 않게."""
    if len(value) <= 4:
        return "*" * len(value)
    keep = max(2, len(value) // 4)
    return value[:keep] + "*" * (len(value) - 2 * keep) + value[-keep:]


def _code_ranges(text: str) -> list[tuple[int, int]]:
    ranges, pos = [], 0
    for kind, chunk in split_markdown(text):
        if kind != TEXT:
            ranges.append((pos, pos + len(chunk)))
        pos += len(chunk)
    return ranges


def inspect_text(text: str) -> str:
    code = _code_ranges(text)

    def in_code(off: int) -> bool:
        return any(a <= off < b for a, b in code)

    rep = text_unicode.inspect_text(text)
    hidden = [h for h in rep.hits if h.kind != "space"]
    spaces = [h for h in rep.hits if h.kind == "space"]
    lines = [f"글자 수: {len(text)}"]
    lines.append(f"숨은 문자: {sum(h.count for h in hidden)}개")
    for h in hidden:
        where = ", ".join(f"{line_of(text, o)}줄" + ("(코드)" if in_code(o) else "") for o in h.samples)
        lines.append(f"  - [{h.kind}] {h.label} x{h.count}  위치: {where}")
    if any(h.kind == "bidi" for h in hidden):
        lines.append("  참고: 방향 표시(LRM, RLM, 격리 문자)와 짝이 맞는 LRE/RLE는 정리 때 보존됩니다.")
    lines.append(f"공백 동형 문자: {sum(h.count for h in spaces)}개(기본 정리에서는 바꾸지 않음)")
    for h in spaces:
        where = ", ".join(f"{line_of(text, o)}줄" for o in h.samples)
        lines.append(f"  - {h.label} x{h.count}  위치: {where}")
    pii = []
    for name, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            pii.append(f"  - {name}: {mask(m.group(0))}  {line_of(text, m.start())}줄")
    lines.append(f"개인정보 후보: {len(pii)}곳(자동으로 가리지 않음, 확인 후 결정)")
    lines.extend(pii)
    return "\n".join(lines)


def inspect_image(data: bytes) -> str:
    kind = detect(data)
    if kind is None:
        return "지원하지 않는 형식(PNG, JPEG만 점검)"
    lines = [f"형식: {kind.upper()}"]
    if kind == "png":
        chunks = parse_png(data)
        tail = len(data) - 8 - sum(len(c.raw) for c in chunks)
    else:
        chunks, rest = parse_jpeg(data)
        tail = 0
    meta = [c for c in chunks if c.drop]
    lines.append(f"지울 메타데이터: {len(meta)}개")
    for c in meta:
        extra = ""
        if c.name in ("tEXt", "zTXt", "iTXt"):
            keyword = c.payload.split(b"\x00", 1)[0].decode("latin-1", "replace")
            extra = f"  키워드: {keyword}"
        elif c.name == "APP1":
            extra = "  EXIF" if c.payload.startswith(b"Exif\x00") else "  XMP 등"
        lines.append(f"  - {c.name} {len(c.payload)} bytes{extra}")
    info = [c.name for c in chunks if c.name in _IMAGE_INFO_ONLY]
    if info:
        lines.append(f"참고(유지됨): {', '.join(info)}")
    bad = [c.name for c in chunks if not c.crc_ok]
    if bad:
        lines.append(f"CRC 불일치: {', '.join(bad)}")
    if tail:
        lines.append(f"IEND 뒤 덧붙은 데이터: {tail} bytes(정리 때 지움)")
    if kind == "jpeg" and not rest.endswith(b"\xff\xd9"):
        lines.append("EOI 뒤 데이터 있음 또는 EOI 없음(직접 확인 필요)")
    lines.append("이미지 속 글자(IP, 사용자 이름 등)는 이 도구가 보지 못합니다. 이미지를 직접 확인하세요.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="숨은 문자, 메타데이터, 개인정보 후보 점검(읽기 전용)")
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args(argv)
    for p in args.paths:
        print(f"== {p}")
        data = p.read_bytes()
        if detect(data):
            try:
                print(inspect_image(data))
            except FormatError as e:
                print(f"이미지 해석 실패: {e}")
        else:
            try:
                print(inspect_text(data.decode("utf-8")))
            except UnicodeDecodeError:
                print("UTF-8 텍스트도 PNG/JPEG도 아니라서 건너뜁니다")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
