#!/usr/bin/env python3
"""원문과 결과를 비교해 사실이 보존됐는지 확인한다(읽기 전용).

실패(FAIL)로 보는 것:
  - 숫자 목록이 달라짐
  - URL, 마크다운 링크 주소, 이미지 경로가 달라짐
  - 코드 블록(펜스, 인라인) 내용이 달라짐
  - 결과에 숨은 문자가 남아 있음(clean_text가 지울 문자 기준)
  - --forbid로 지정한 금지 문자가 결과에 있음
  - 결과 기준 상대 경로의 이미지 파일이 없음
경고(WARN)로만 보는 것:
  - 분량 비율(공백 제외 글자 수)이 --min-ratio(기본 0.9) 미만

숫자, URL, 링크는 양쪽 모두 숨은 문자를 지운 뒤 비교한다(보이는 내용 기준).
exit code: 0 통과, 1 실패.

사용 예:
  python3 scripts/verify.py draft.md draft-blog.md --forbid U+00B7
"""

from __future__ import annotations

import os
import sys

import argparse
import re
from collections import Counter
from pathlib import Path

from clean_text import clean_markdown  # noqa: E402
from mdsegments import TEXT, code_spans, split_markdown  # noqa: E402

NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
URL = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
MD_LINK = re.compile(r"(!?)\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def _prose(text: str) -> str:
    return "".join(chunk for kind, chunk in split_markdown(text) if kind == TEXT)


def _url(u: str) -> str:
    return u.rstrip(".,;:!?")


def facts(text: str) -> dict[str, Counter[str]]:
    """숨은 문자를 지운 본문에서 숫자, URL, 링크, 이미지 경로를 모은다(코드 안은 코드 비교에서 따로 본다)."""
    visible, _ = clean_markdown(text)
    prose = _prose(visible)
    links, images = Counter(), Counter()
    for m in MD_LINK.finditer(prose):
        (images if m.group(1) else links)[m.group(2)] += 1
    return {
        "숫자": Counter(NUMBER.findall(prose)),
        "URL": Counter(_url(u) for u in URL.findall(prose)),
        "링크 주소": links,
        "이미지 경로": images,
    }


def _diff(a: Counter[str], b: Counter[str]) -> str:
    missing = a - b
    added = b - a
    parts = []
    if missing:
        parts.append("빠짐 " + ", ".join(f"{k}" + (f" x{n}" if n > 1 else "") for k, n in missing.items()))
    if added:
        parts.append("생김 " + ", ".join(f"{k}" + (f" x{n}" if n > 1 else "") for k, n in added.items()))
    return "; ".join(parts)


def parse_char(spec: str) -> str:
    """'U+00B7', '0xB7', 문자 하나 그대로 형태를 문자 하나로 바꾼다."""
    s = spec.strip()
    if re.fullmatch(r"(?i)(u\+|0x)[0-9a-f]{1,6}", s):
        return chr(int(s[2:], 16))
    if len(s) == 1:
        return s
    raise argparse.ArgumentTypeError(f"금지 문자 형식을 알 수 없습니다: {spec}")


def verify(original: str, result: str, *, result_dir: Path | None = None,
           forbid: list[str] | None = None, min_ratio: float = 0.9) -> tuple[list[tuple[str, str, str]], bool]:
    """[(상태, 항목, 설명)] 목록과 통과 여부를 돌려준다. 상태는 PASS, FAIL, WARN."""
    rows: list[tuple[str, str, str]] = []
    fa, fb = facts(original), facts(result)
    for key in fa:
        d = _diff(fa[key], fb[key])
        rows.append(("FAIL", key, d) if d else ("PASS", key, f"{sum(fa[key].values())}개 동일"))

    ca, cb = code_spans(original), code_spans(result)
    if ca == cb:
        rows.append(("PASS", "코드 블록", f"{len(ca)}개 동일"))
    else:
        changed = sum(1 for x, y in zip(ca, cb) if x != y) + abs(len(ca) - len(cb))
        rows.append(("FAIL", "코드 블록", f"원문 {len(ca)}개, 결과 {len(cb)}개, 다른 곳 {changed}곳"))

    def size(t: str) -> int:
        return len(re.sub(r"\s", "", t))

    ratio = size(result) / size(original) if size(original) else 1.0
    rows.append(("WARN" if ratio < min_ratio else "PASS", "분량", f"{ratio:.1%} (기준 {min_ratio:.0%})"))

    _, st = clean_markdown(result)
    if st["removed_count"]:
        rows.append(("FAIL", "숨은 문자", f"{st['removed_count']}개 남음: {', '.join(st['removed'])}"))
    else:
        rows.append(("PASS", "숨은 문자", "0개"))

    for ch in forbid or []:
        n = result.count(ch)
        label = f"금지 문자 U+{ord(ch):04X}"
        rows.append(("FAIL", label, f"{n}개") if n else ("PASS", label, "0개"))

    if result_dir is not None:
        missing = [p for p in fb["이미지 경로"]
                   if not re.match(r"(?i)^(https?:|data:)", p) and not (result_dir / p).is_file()]
        if missing:
            rows.append(("FAIL", "이미지 파일", "없음: " + ", ".join(missing)))
        else:
            rows.append(("PASS", "이미지 파일", f"{len(fb['이미지 경로'])}개 확인"))

    return rows, all(s != "FAIL" for s, _, _ in rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="원문과 결과의 사실 보존 확인")
    ap.add_argument("original", type=Path)
    ap.add_argument("result", type=Path)
    ap.add_argument("--forbid", action="append", type=parse_char, default=[],
                    help="결과에 있으면 안 되는 문자(U+00B7 형식 또는 문자 그대로). 여러 번 쓸 수 있음")
    ap.add_argument("--min-ratio", type=float, default=0.9, help="분량 경고 기준(기본 0.9)")
    args = ap.parse_args(argv)

    a = args.original.read_text(encoding="utf-8")
    b = args.result.read_text(encoding="utf-8")
    rows, ok = verify(a, b, result_dir=args.result.parent, forbid=args.forbid, min_ratio=args.min_ratio)
    for status, item, desc in rows:
        print(f"[{status}] {item}: {desc}")
    print("결과: 통과" if ok else "결과: 실패")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
