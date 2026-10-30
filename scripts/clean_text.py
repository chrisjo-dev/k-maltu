#!/usr/bin/env python3
"""본문의 숨은 문자를 지운다. 원본은 덮어쓰지 않고 새 파일에 쓴다.

실제 판정은 vendor/watermarks-remover/text_unicode.py(원본 그대로)의 clean_text가 한다.
ko-maltu는 그 위에 다음만 정한다.
- 공백 동형 문자(U+00A0, U+3000 등)는 기본으로 바꾸지 않고 보고만 한다.
- NFKC, 라틴 혼동 문자 치환, 이모지 결합 문자 제거, 양방향 제어 문자 강제 제거는 쓰지 않는다.
- 마크다운 펜스 코드 블록과 인라인 코드는 손대지 않는다(--no-markdown이면 전체를 본문으로 본다).

사용 예:
  python3 scripts/clean_text.py draft.md -o draft-clean.md
  python3 scripts/clean_text.py draft.md --check   # 바꾸지 않고 보고, 지울 것이 있으면 exit 1
"""

from __future__ import annotations

import os
import sys

import argparse
from collections import Counter
from pathlib import Path

from mdsegments import TEXT, split_markdown, text_unicode  # noqa: E402


def _space_hits(text: str) -> Counter[str]:
    hits: Counter[str] = Counter()
    for ch in text:
        if ord(ch) in text_unicode.SPACE_HOMOGLYPHS:
            hits[text_unicode._char_label(ch)] += 1
    return hits


def clean_markdown(text: str, *, markdown: bool = True, normalize_spaces: bool = False) -> tuple[str, dict]:
    """본문 조각만 정리하고 코드 조각은 그대로 둔다. (결과, 통계)를 돌려준다."""
    segments = split_markdown(text) if markdown else [(TEXT, text)]
    removed: Counter[str] = Counter()
    replaced: Counter[str] = Counter()
    code_hidden: Counter[str] = Counter()
    out: list[str] = []
    code_count = 0
    for kind, chunk in segments:
        if kind != TEXT:
            code_count += 1
            out.append(chunk)
            # 코드 안에서 지울 만한 문자는 지우지 않고 알리기만 한다.
            _, s = text_unicode.clean_text(chunk, normalize_spaces=False)
            code_hidden.update(s["removed"])
            continue
        cleaned, s = text_unicode.clean_text(
            chunk,
            nfkc=False,
            aggressive_homoglyphs=False,
            normalize_spaces=normalize_spaces,
            strip_emoji_glue=False,
            strip_bidi=False,
        )
        removed.update(s["removed"])
        replaced.update(s["replaced"])
        out.append(cleaned)
    result = "".join(out)
    stats = {
        "removed": dict(removed),
        "removed_count": sum(removed.values()),
        "replaced": dict(replaced),
        "replaced_count": sum(replaced.values()),
        "spaces_left": dict(_space_hits(result)),
        "code_segments": code_count,
        "code_hidden": dict(code_hidden),
    }
    return result, stats


def report(stats: dict) -> str:
    lines = [f"지운 숨은 문자: {stats['removed_count']}개"]
    for label, n in sorted(stats["removed"].items(), key=lambda x: -x[1]):
        lines.append(f"  - {label} x{n}")
    if stats["replaced_count"]:
        lines.append(f"공백으로 바꾼 문자: {stats['replaced_count']}개")
        for label, n in stats["replaced"].items():
            lines.append(f"  - {label} x{n}")
    if stats["spaces_left"]:
        total = sum(stats["spaces_left"].values())
        lines.append(f"공백 동형 문자(보고만, 바꾸려면 --normalize-spaces): {total}개")
        for label, n in stats["spaces_left"].items():
            lines.append(f"  - {label} x{n}")
    lines.append(f"보존한 코드 조각: {stats['code_segments']}개")
    if stats["code_hidden"]:
        lines.append("코드 안 숨은 문자(지우지 않음, 직접 확인 필요):")
        for label, n in stats["code_hidden"].items():
            lines.append(f"  - {label} x{n}")
    return "\n".join(lines)


def default_output(path: Path) -> Path:
    return path.with_name(f"{path.stem}.cleaned{path.suffix}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="숨은 문자 정리(원본 유지, 새 파일에 저장)")
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, help="출력 경로(기본: <이름>.cleaned<확장자>)")
    ap.add_argument("--check", action="store_true", help="쓰지 않고 보고만. 지울 문자가 있으면 exit 1")
    ap.add_argument("--normalize-spaces", action="store_true", help="공백 동형 문자를 U+0020으로 바꾼다")
    ap.add_argument("--no-markdown", action="store_true", help="코드 블록 구분 없이 전체를 정리")
    ap.add_argument("--force", action="store_true", help="출력 파일이 이미 있으면 덮어쓴다")
    args = ap.parse_args(argv)

    # newline=""로 읽고 써서 CRLF 같은 줄바꿈을 그대로 둔다.
    with open(args.input, encoding="utf-8", newline="") as f:
        text = f.read()
    result, stats = clean_markdown(text, markdown=not args.no_markdown, normalize_spaces=args.normalize_spaces)
    print(report(stats))

    if args.check:
        return 1 if stats["removed_count"] or stats["replaced_count"] else 0

    out = args.output or default_output(args.input)
    if out.resolve() == args.input.resolve():
        print("오류: 입력 파일을 덮어쓸 수 없습니다. 다른 출력 경로를 주세요.", file=sys.stderr)
        return 2
    if out.exists() and not args.force:
        print(f"오류: {out} 이(가) 이미 있습니다. 덮어쓰려면 --force", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(result)
    print(f"저장: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
