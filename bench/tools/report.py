#!/usr/bin/env python3
"""반영 전후 결과를 하이라이팅한 검수 보고서(HTML) 만들기.

사용:
  python3 bench/tools/report.py <문항 폴더> <전 결과 폴더> <후 결과 폴더> <출력.html> [--blind]

- 문항 폴더: items.json이 있는 폴더(예: bench). 문항 파일 경로는 items.json의 path 기준.
- 전/후 결과 폴더: <문항 id>.md 파일들. 두 폴더 모두에 있는 문항만 보고서에 넣는다.
- --blind: 전/후를 A/B로 가리고 순서를 섞는다. "정답 보기" 버튼으로 확인.
원문에서 지운 말은 취소선, 결과에 새로 쓴 말은 초록 배경으로 표시한다.
"""
from __future__ import annotations

import difflib
import html
import json
import random
import re
import sys
from pathlib import Path

TOKEN = re.compile(r"\s+|[\w가-힣]+|[^\w\s]", re.UNICODE)


def tokens(s: str) -> list[str]:
    return TOKEN.findall(s)


def diff(a: str, b: str) -> tuple[str, str, int, int]:
    """(지운 말과 새로 쓴 말을 함께 보인 HTML, 결과만 보인 HTML, 지운 수, 새로 쓴 수)"""
    ta, tb = tokens(a), tokens(b)
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    esc = lambda xs: html.escape("".join(xs))
    uni, clean, dels, ins = [], [], 0, 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            uni.append(esc(tb[j1:j2])); clean.append(esc(tb[j1:j2]))
            continue
        if i2 > i1:
            uni.append(f"<del>{esc(ta[i1:i2])}</del>"); dels += sum(1 for t in ta[i1:i2] if t.strip())
        if j2 > j1:
            seg = f"<ins>{esc(tb[j1:j2])}</ins>"
            uni.append(seg); clean.append(seg); ins += sum(1 for t in tb[j1:j2] if t.strip())
    return "".join(uni), "".join(clean), dels, ins


def section(src: str, name: str) -> str:
    if name == "원문":
        return src.split("## 원문", 1)[1].split("## 좋은 답이 갖출 점", 1)[0].strip()
    return src.split("## 좋은 답이 갖출 점", 1)[1].strip() if "## 좋은 답이 갖출 점" in src else ""


def preserve(item: dict, out: str) -> str:
    nums = lambda s: [n.replace(",", "") for n in re.findall(r"\d[\d,]*", s)]
    pool, miss, total = nums(out), [], 0
    for p in item.get("preserve", []):
        if p.get("optional"):
            continue
        total += 1
        v = p["value"]
        if p.get("exact", True):
            ok = v in out
        else:
            ok = all(n in pool or (p.get("kind") == "time" and n.isdigit() and str(int(n) + 12) in pool) for n in nums(v))
        if not ok:
            miss.append(v)
    return f"보존 사실 {total - len(miss)}/{total}" + (f" (빠짐: {html.escape(', '.join(miss))})" if miss else "")


CSS = """:root{--bg:#f7f5f0;--card:#fff;--ink:#1d1b18;--muted:#6b665d;--line:#e4dfd4;--del:#fde2df;--delink:#a8261b;--ins:#dcf3e2;--insink:#15603a;--accent:#b83219;--chip:#f1ede4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15140f;--card:#1f1d18;--ink:#ede8dc;--muted:#a49d8f;--line:#35322a;--del:#4a1f1b;--delink:#ffb4aa;--ins:#173a26;--insink:#9be3b3;--accent:#ff8a70;--chip:#2a2721}}
:root[data-theme="dark"]{--bg:#15140f;--card:#1f1d18;--ink:#ede8dc;--muted:#a49d8f;--line:#35322a;--del:#4a1f1b;--delink:#ffb4aa;--ins:#173a26;--insink:#9be3b3;--accent:#ff8a70;--chip:#2a2721}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 -apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;word-break:keep-all}
.wrap{max-width:1180px;margin:0 auto;padding:32px 16px 0}h1{font-size:26px;margin:0 0 6px}h3{font-size:17px;margin:0}.sub{color:var(--muted);margin:0 0 18px}
del{background:var(--del);color:var(--delink);text-decoration:line-through;border-radius:3px;padding:0 1px}ins{background:var(--ins);color:var(--insink);text-decoration:none;border-radius:3px;padding:0 1px;font-weight:600}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:16px 0}.meta{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 14px}.chip{background:var(--chip);border-radius:999px;padding:2px 10px;font-size:12.5px;color:var(--muted)}
.grid{display:grid;gap:12px;grid-template-columns:1fr}@media(min-width:900px){.grid{grid-template-columns:1fr 1fr 1fr}}
.pane{border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-width:0}.pane h4{margin:0 0 8px;font-size:13px;color:var(--muted);display:flex;justify-content:space-between;gap:8px}.txt{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14.5px}.stat{font-size:12px;color:var(--muted)}
details{margin-top:12px}summary{cursor:pointer;color:var(--muted);font-size:13.5px}.v-clean{display:none}.clean .v-clean{display:block}.clean .v-uni{display:none}
.pick{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px;padding-top:14px;border-top:1px dashed var(--line)}.pick label{display:flex;gap:6px;align-items:center;cursor:pointer;padding:6px 12px;border:1px solid var(--line);border-radius:8px}
.pick input[type=text]{flex:1;min-width:200px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font:inherit}
.reveal{display:none;color:var(--accent);font-weight:700}.revealed .reveal{display:inline}
button{font:inherit;cursor:pointer;border:0;border-radius:10px;padding:10px 16px;background:var(--ink);color:var(--bg);font-weight:600}button.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.bar{position:sticky;bottom:0;background:var(--bg);padding:12px 0;border-top:1px solid var(--line);display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap;margin-top:24px}"""


def main(argv: list[str]) -> int:
    blind = "--blind" in argv
    args = [a for a in argv if a != "--blind"]
    if len(args) != 4:
        print(__doc__)
        return 2
    root, before, after, out = Path(args[0]), Path(args[1]), Path(args[2]), Path(args[3])
    items = json.loads((root / "items.json").read_text(encoding="utf-8"))["items"]
    rng = random.Random(len(items))
    cards, key = [], {}
    for it in items:
        fb, fa = before / f"{it['id']}.md", after / f"{it['id']}.md"
        if not (fb.exists() and fa.exists()):
            continue
        src = (root / it["path"]).read_text(encoding="utf-8")
        orig = section(src, "원문")
        vers = [("전", fb.read_text(encoding="utf-8").strip()), ("후", fa.read_text(encoding="utf-8").strip())]
        if blind:
            rng.shuffle(vers)
        labels = ["A", "B"] if blind else ["반영 전", "반영 후"]
        key[it["id"]] = {labels[0]: vers[0][0], labels[1]: vers[1][0]}
        panes = [f'<div class="pane"><h4><span>원문</span><span class="stat">{len(orig.replace(chr(10), ""))}자</span></h4><div class="txt">{html.escape(orig)}</div></div>']
        for lab, (name, text) in zip(labels, vers):
            u, c, d, i = diff(orig, text)
            tag = f' <span class="reveal">= 반영 {name}</span>' if blind else ""
            panes.append(f'<div class="pane"><h4><span>{lab}{tag}</span><span class="stat">{len(text.replace(chr(10), ""))}자, 지움 {d} / 새로 씀 {i}</span></h4><div class="txt"><div class="v-uni">{u}</div><div class="v-clean">{c}</div></div><div class="stat" style="margin-top:8px">{preserve(it, text)}</div></div>')
        crit = section(src, "기준")
        crit_html = f'<details><summary>채점 기준</summary><div class="txt" style="margin-top:8px">{html.escape(crit)}</div></details>' if crit else ""
        opts = "".join(f'<label><input type="radio" name="p-{it["id"]}" value="{v}">{v}</label>' for v in labels + ["비슷"])
        cards.append(f'<div class="card" data-id="{it["id"]}"><h3>{it["id"]}</h3><div class="meta"><span class="chip">{html.escape(it.get("register", ""))}</span><span class="chip">{html.escape(it.get("type", ""))}</span></div><div class="grid">{"".join(panes)}</div>{crit_html}<div class="pick"><strong>더 나은 쪽</strong>{opts}<input type="text" placeholder="지적이나 메모 (선택)" data-memo="{it["id"]}"></div></div>')
    reveal_btn = '<button class="ghost" id="reveal">정답 보기</button>' if blind else ""
    store = f"kmaltu-review-{out.stem}"
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>k-maltu 검수 보고서</title><style>{CSS}</style></head><body><div class="wrap">
<h1>k-maltu 검수 보고서</h1><p class="sub">원문에서 지운 말은 <del>취소선</del>, 결과에 새로 쓴 말은 <ins>초록 배경</ins>입니다. {len(cards)}문항.</p>
{"".join(cards)}
<div class="bar"><button class="ghost" id="mode">결과만 보기</button>{reveal_btn}<button id="copy">검수 결과 복사</button></div></div>
<script>
const KEY={json.dumps(key, ensure_ascii=False)},S={json.dumps(store)};
function load(){{try{{return JSON.parse(localStorage.getItem(S)||"{{}}")}}catch(e){{return {{}}}}}}
function save(o){{try{{localStorage.setItem(S,JSON.stringify(o))}}catch(e){{}}}}
const st=load();
document.querySelectorAll('.card[data-id]').forEach(c=>{{const id=c.dataset.id,v=st[id]||{{}};
 c.querySelectorAll('input[type=radio]').forEach(r=>{{if(r.value===v.pick)r.checked=true;r.addEventListener('change',()=>{{const o=load();o[id]=Object.assign(o[id]||{{}},{{pick:r.value}});save(o)}})}});
 const m=c.querySelector('[data-memo]');m.value=v.memo||"";m.addEventListener('input',()=>{{const o=load();o[id]=Object.assign(o[id]||{{}},{{memo:m.value}});save(o)}});}});
document.getElementById('mode').addEventListener('click',e=>{{const on=document.body.classList.toggle('clean');e.target.textContent=on?'변경 표시':'결과만 보기'}});
const rb=document.getElementById('reveal');if(rb)rb.addEventListener('click',()=>document.body.classList.toggle('revealed'));
document.getElementById('copy').addEventListener('click',async()=>{{const o=load(),lines=["k-maltu 검수 결과"],n={{"전":0,"후":0,"비슷":0}};
 Object.keys(KEY).forEach(id=>{{const v=o[id]||{{}};const who=v.pick?(v.pick==="비슷"?"비슷":KEY[id][v.pick]):"";if(who)n[who]++;
  lines.push(`- ${{id}}: ${{v.pick||"미선택"}}${{who&&who!=="비슷"?" (반영 "+who+")":""}}${{v.memo?" / "+v.memo:""}}`)}});
 lines.push(`합계: 반영 후 ${{n["후"]}}, 반영 전 ${{n["전"]}}, 비슷 ${{n["비슷"]}}`);const t=lines.join("\\n");
 try{{await navigator.clipboard.writeText(t);alert("복사했습니다. 채팅에 붙여 넣어 주세요.")}}catch(e){{prompt("아래를 복사해 주세요",t)}}}});
</script></body></html>'''
    out.write_text(page, encoding="utf-8")
    print(f"보고서: {out} ({len(cards)}문항, {'이름 가림' if blind else '전후 표시'})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
