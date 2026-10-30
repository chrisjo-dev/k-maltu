#!/usr/bin/env python3
"""k-maltu 실측 자동 채점.

사용: python3 score.py <outputs/변형본 폴더> [...]
문항별로 보존 사실, 통제형 변경 문장 수, 분량 비율, 가운뎃점, 숨은 문자를 검사해 표로 낸다.
보존 사실 규칙(items.json):
  exact=true   원문 문자열이 결과에 그대로 있어야 함
  exact=false  표기 변경 허용. 문자열 안의 숫자들이 결과에 모두 있으면 통과
  optional     없어도 통과(있으면 표시만)
"""
from __future__ import annotations

import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

EXAM = Path(__file__).resolve().parent.parent  # bench/
ITEMS = json.loads((EXAM / "items.json").read_text(encoding="utf-8"))["items"]


def original_text(item: dict) -> str:
    s = (EXAM / item["path"]).read_text(encoding="utf-8")
    return s.split("## 원문", 1)[1].split("## 좋은 답이 갖출 점", 1)[0].strip()


def chars(s: str) -> int:
    return len(s.replace("\n", "").strip())


def numbers(s: str) -> list[str]:
    return [n.replace(",", "") for n in re.findall(r"\d[\d,]*", s)]


def preserve_check(item: dict, out: str) -> tuple[int, int, list[str]]:
    out_nums = numbers(out)
    ok, total, missing = 0, 0, []
    for p in item["preserve"]:
        if p.get("optional"):
            continue
        total += 1
        v = p["value"]
        if p.get("exact", True):
            hit = v in out
        else:
            need = numbers(v)
            pool = list(out_nums)
            hit = True
            for n in need:
                if n in pool:
                    pool.remove(n)
                elif n.lstrip("0") in [x.lstrip("0") for x in pool]:
                    pool.pop([x.lstrip("0") for x in pool].index(n.lstrip("0")))
                elif p.get("kind") == "time" and n.isdigit() and str(int(n) + 12) in pool:
                    pool.remove(str(int(n) + 12))  # 저녁 7시 -> 19:00 같은 24시각제 변환
                else:
                    hit = False
        if hit:
            ok += 1
        else:
            missing.append(v)
    return ok, total, missing


def sentences(s: str) -> list[str]:
    parts = re.split(r"(?<=[.!?。])\s+|\n+", s)
    return [p.strip() for p in parts if p.strip()]


def changed_sentences(orig: str, out: str) -> int:
    a, b = sentences(orig), sentences(out)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    changed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            changed += max(i2 - i1, j2 - j1)
    return changed


def hidden_count(s: str) -> int:
    return sum(1 for ch in s if unicodedata.category(ch) == "Cf" and ch not in "‍️")


def score_dir(d: Path) -> list[dict]:
    rows = []
    for item in ITEMS:
        f = d / f"{item['id']}.md"
        if not f.exists():
            continue
        out = f.read_text(encoding="utf-8").strip()
        orig = original_text(item)
        ok, total, missing = preserve_check(item, out)
        row = {
            "variant": d.name,
            "id": item["id"],
            "type": item["type"],
            "preserve": f"{ok}/{total}",
            "preserve_ok": ok == total,
            "missing": missing,
            "ratio": round(chars(out) / max(1, chars(orig)), 2),
            "middot": out.count("·"),
            "hidden": hidden_count(out),
        }
        if item["type"] == "통제형":
            row["changed"] = changed_sentences(orig, out)
        rows.append(row)
    return rows


def main(argv: list[str]) -> int:
    all_rows = []
    for a in argv:
        all_rows += score_dir(Path(a))
    print("| 변형본 | 문항 | 유형 | 보존 | 분량 | 가운뎃점 | 숨은문자 | 통제형 변경 | 빠진 사실 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in all_rows:
        print(f"| {r['variant']} | {r['id']} | {r['type']} | {r['preserve']} | {r['ratio']} | {r['middot']} | {r['hidden']} | {r.get('changed', '')} | {', '.join(r['missing'])} |")
    print()
    by = {}
    for r in all_rows:
        by.setdefault(r["variant"], []).append(r)
    print("| 변형본 | 문항 수 | 보존 완전 | 가운뎃점 | 숨은문자 | 통제형 과교정(변경 3개 이상) |")
    print("|---|---|---|---|---|---|")
    for v, rs in by.items():
        over = sum(1 for r in rs if r.get("changed", 0) >= 3)
        print(f"| {v} | {len(rs)} | {sum(r['preserve_ok'] for r in rs)}/{len(rs)} | {sum(r['middot'] for r in rs)} | {sum(r['hidden'] for r in rs)} | {over} |")
    json.dump(all_rows, open(Path(__file__).resolve().parent.parent / "outputs" / "auto-scores.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
