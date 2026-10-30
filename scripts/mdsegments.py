"""마크다운을 본문, 펜스 코드 블록, 인라인 코드로 나눈다.

clean_text, inspect, verify가 같은 기준으로 코드 영역을 구분하도록 한곳에 둔다.
나눈 조각을 그대로 이어 붙이면 원문과 바이트 단위로 같다.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VENDOR_WMR = Path(__file__).resolve().parent.parent / "vendor" / "watermarks-remover"
if str(VENDOR_WMR) not in sys.path:
    sys.path.insert(0, str(VENDOR_WMR))

import text_unicode  # noqa: E402  (vendor/watermarks-remover, 원본 그대로)

TEXT = "text"
FENCE = "fence"
INLINE = "inline"

_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _split_fences(text: str) -> list[tuple[str, str]]:
    """펜스 코드 블록(``` 또는 ~~~)을 떼어 낸다. 닫히지 않은 펜스는 문서 끝까지 코드로 본다."""
    parts: list[tuple[str, str]] = []
    buf: list[str] = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        m = _FENCE_OPEN.match(lines[i])
        if not m:
            buf.append(lines[i])
            i += 1
            continue
        fence = m.group(1)
        # 백틱 펜스는 정보 문자열에 백틱이 있으면 펜스가 아니다(CommonMark).
        if fence[0] == "`" and "`" in lines[i][m.end():]:
            buf.append(lines[i])
            i += 1
            continue
        if buf:
            parts.append((TEXT, "".join(buf)))
            buf = []
        close = re.compile(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*\r?\n?$")
        block = [lines[i]]
        i += 1
        while i < len(lines):
            block.append(lines[i])
            i += 1
            if close.match(block[-1]):
                break
        parts.append((FENCE, "".join(block)))
    if buf:
        parts.append((TEXT, "".join(buf)))
    return parts


def _split_inline(text: str) -> list[tuple[str, str]]:
    """같은 길이의 백틱 묶음으로 닫힌 인라인 코드를 떼어 낸다. 짝이 없으면 일반 글자로 둔다."""
    parts: list[tuple[str, str]] = []
    pos = 0
    start_text = 0
    while True:
        m = re.compile(r"`+").search(text, pos)
        if not m:
            break
        ticks = m.group(0)
        closer = re.compile(r"(?<!`)" + re.escape(ticks) + r"(?!`)")
        c = closer.search(text, m.end())
        if not c:
            pos = m.end()
            continue
        if m.start() > start_text:
            parts.append((TEXT, text[start_text:m.start()]))
        parts.append((INLINE, text[m.start():c.end()]))
        pos = start_text = c.end()
    if start_text < len(text):
        parts.append((TEXT, text[start_text:]))
    return parts


def split_markdown(text: str) -> list[tuple[str, str]]:
    """(종류, 조각) 목록을 돌려준다. 종류는 text, fence, inline 중 하나."""
    out: list[tuple[str, str]] = []
    for kind, chunk in _split_fences(text):
        if kind == FENCE:
            out.append((kind, chunk))
        else:
            out.extend(_split_inline(chunk))
    return out


def code_spans(text: str) -> list[str]:
    return [chunk for kind, chunk in split_markdown(text) if kind != TEXT]


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1
