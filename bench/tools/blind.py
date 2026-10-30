#!/usr/bin/env python3
"""채점용 이름 가리기 묶음 만들기.

outputs/<변형본>/<id>.md 를 문항별로 모아 순서를 섞고 A, B, C... 기호를 붙인다.
채점자용 묶음: judging/packets/<id>.md  (원문 + 기호 붙은 답안들)
대응표(채점자에게 보여 주지 않음): judging/.key/mapping.json
"""
from __future__ import annotations

import json
import random
import string
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
EXAM = LAB  # bench/
OUT = LAB / "outputs"
JUDGE = LAB / (sys.argv[1] if len(sys.argv) > 1 else "judging")
# 사용: blind.py [출력폴더] [register=변형본1,변형본2 ...]  (지정 없으면 전체)
PICK = {a.split("=")[0]: a.split("=")[1].split(",") for a in sys.argv[2:]}
NAMES = {"blog": "블로그(~다체 기본)", "threads": "스레드(Threads 같은 짧은 SNS 글)", "dc": "디씨(커뮤니티 음슴체, 반말)", "gongmun": "공문서(개조식, 항목 기호, 날짜 2026. 10. 30. 표기, 붙임, 끝.)"}


def main() -> None:
    rng = random.Random(20261030 + len(PICK))
    items = json.loads((EXAM / "items.json").read_text(encoding="utf-8"))["items"]
    variants = sorted(p.name for p in OUT.iterdir() if p.is_dir())
    (JUDGE / "packets").mkdir(parents=True, exist_ok=True)
    (JUDGE / ".key").mkdir(parents=True, exist_ok=True)
    mapping = {}
    for it in items:
        if PICK and it["register"] not in PICK:
            continue
        src = (EXAM / it["path"]).read_text(encoding="utf-8")
        fm = src.split("---")[1]
        instruction = next((l.split(":", 1)[1].strip().strip('"') for l in fm.splitlines() if l.startswith("instruction:")), "")
        orig, criteria = (x.strip() for x in src.split("## 원문", 1)[1].split("## 좋은 답이 갖출 점", 1))
        use = PICK.get(it["register"], variants)
        answers = [(v, (OUT / v / f"{it['id']}.md").read_text(encoding="utf-8").strip()) for v in variants if v in use and (OUT / v / f"{it['id']}.md").exists()]
        rng.shuffle(answers)
        codes = list(string.ascii_uppercase[: len(answers)])
        mapping[it["id"]] = {c: v for c, (v, _) in zip(codes, answers)}
        lines = [f"# {it['id']}", "", f"- 목표 말투: {NAMES[it['register']]}", f"- 문항 유형: {it['type']}" + (" (사람이 쓴 자연스러운 글. 거의 그대로 두는 답이 좋은 답)" if it["type"] == "통제형" else ""), f"- 사용자 요청: {instruction}", "", "## 원문", "", orig, "", "## 이 문항의 채점 기준 (좋은 답이 갖출 점)", "", criteria, ""]
        for c, (_, text) in zip(codes, answers):
            lines += [f"## 답안 {c}", "", text, ""]
        (JUDGE / "packets" / f"{it['id']}.md").write_text("\n".join(lines), encoding="utf-8")
    (JUDGE / ".key" / "mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    print("packets:", len(mapping), "pick:", PICK or variants)


if __name__ == "__main__":
    main()
