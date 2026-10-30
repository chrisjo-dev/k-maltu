#!/usr/bin/env python3
"""채점 결과 집계.

입력: judging/raw/*.json (채점자 응답 JSON, {"judge":"J1","items":{id:{"scores":{코드:{ai,register,meaning,publish}},"rank":[...]}}})
      judging/.key/mapping.json (문항별 코드 -> 변형본)
출력: 말투별, 변형본별 평균 점수와 기준선 대비 승/무/패, 채점자 간 큰 불일치 목록.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

LAB = Path(__file__).resolve().parent.parent
import sys
J = LAB / (sys.argv[1] if len(sys.argv) > 1 else "judging")
CRIT = ("ai", "register", "meaning", "publish")


def load():
    mapping = json.loads((J / ".key" / "mapping.json").read_text(encoding="utf-8"))
    rows = []  # (judge, item, variant, scores dict, total)
    for f in sorted((J / "raw").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for item, v in data["items"].items():
            for code, sc in v["scores"].items():
                variant = mapping[item].get(code)
                if variant is None:
                    continue
                total = sum(int(sc[c]) for c in CRIT)
                rows.append((data["judge"], item, variant, sc, total))
    return rows


def main() -> None:
    rows = load()
    reg = lambda item: item.rsplit("-", 1)[0]
    # 말투별 평균 총점(4~20)
    table = defaultdict(list)
    crit_table = defaultdict(lambda: defaultdict(list))
    for judge, item, var, sc, total in rows:
        table[(reg(item), var)].append(total)
        for c in CRIT:
            crit_table[(reg(item), var)][c].append(int(sc[c]))
    print("## 말투별 평균 총점 (4~20, 채점자 2명 평균)\n")
    print("| 말투 | 변형본 | n | 총점 | ai | register | meaning | publish |")
    print("|---|---|---|---|---|---|---|---|")
    for (r, var) in sorted(table, key=lambda k: (k[0], -mean(table[k]))):
        ct = crit_table[(r, var)]
        print(f"| {r} | {var} | {len(table[(r, var)])} | {mean(table[(r, var)]):.2f} | " + " | ".join(f"{mean(ct[c]):.2f}" for c in CRIT) + " |")
    # 기준선 대비 승/무/패 (같은 채점자, 같은 문항)
    base = {(j, i): t for j, i, v, s, t in rows if v == "baseline"}
    wdl = defaultdict(lambda: [0, 0, 0])
    diff = defaultdict(list)
    for j, i, v, s, t in rows:
        if v == "baseline" or (j, i) not in base:
            continue
        d = t - base[(j, i)]
        diff[(reg(i), v)].append(d)
        wdl[(reg(i), v)][0 if d > 0 else 1 if d == 0 else 2] += 1
    print("\n## 기준선 대비 (같은 채점자, 같은 문항 총점 비교)\n")
    print("| 말투 | 변형본 | 승 | 무 | 패 | 평균 차이 |")
    print("|---|---|---|---|---|---|")
    for k in sorted(wdl, key=lambda k: (k[0], -mean(diff[k]))):
        w, d_, l = wdl[k]
        print(f"| {k[0]} | {k[1]} | {w} | {d_} | {l} | {mean(diff[k]):+.2f} |")
    # 채점자 간 불일치 (같은 문항, 같은 변형본 총점 차이 4 이상)
    by = defaultdict(dict)
    for j, i, v, s, t in rows:
        by[(i, v)][j] = t
    dis = [(i, v, js) for (i, v), js in by.items() if len(js) == 2 and abs(list(js.values())[0] - list(js.values())[1]) >= 4]
    print(f"\n## 채점자 간 큰 불일치 (총점 차 4 이상): {len(dis)}건\n")
    for i, v, js in sorted(dis):
        print(f"- {i} {v}: {js}")
    # 채점자별 전체 평균(엄격도 차이 확인)
    jm = defaultdict(list)
    for j, i, v, s, t in rows:
        jm[j].append(t)
    print("\n채점자별 평균 총점:", {j: round(mean(ts), 2) for j, ts in jm.items()})


if __name__ == "__main__":
    main()
