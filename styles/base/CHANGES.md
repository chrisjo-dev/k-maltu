# styles/base 변경 기록

`styles/base/`는 korean-humanizer v1.0.1(vendor/korean-humanizer/)의 카탈로그를 k-maltu용으로 고친 판이다. 원본과의 차이는 `scripts/diff_upstream.sh`로 볼 수 있다.

## 2026-10-30, 첫 복사

대상: `ko-ai-signals.md` (원본 `vendor/korean-humanizer/references/ko-ai-signals.md`)

| 바꾼 점 | 이유 |
|---|---|
| 맨 위에 출처 안내 한 줄 추가 | 수정본이라는 것과 원본 위치를 바로 알 수 있게 |
| 가운뎃점(U+00B7) 10곳을 슬래시로 | 저장소 글쓰기 규칙(가운뎃점 금지) |
| "부록: 적용 순서" 1~3번을 k-maltu 우선순위로 | Brand voice 대신 `styles/personal.md`, 도메인 대신 `registers/`를 쓰므로 |
| 원작 저장소에만 있는 링크(`../korean-humanizer-research.md`, `../SKILL.md`, `../examples/...`)를 vendor 경로나 설명으로 | 이 저장소 안에서 깨진 링크가 되지 않게 |

카테고리 표(1~12번)의 내용은 바꾸지 않았다. 말투마다 카테고리를 끄고 켜는 일은 `registers/*.md`의 `humanizer` 항목이 맡는다.

## 앞으로 고칠 때

- 표에 패턴을 더하거나 빼면 여기에 날짜, 바꾼 점, 이유를 한 줄씩 남긴다.
- 다른 한국어 문체 스킬을 가져오면 원본은 `vendor/<이름>/`에 그대로 두고 `ORIGIN.md`를 쓴 뒤, 고친 판은 `styles/<묶음>/`에 두고 이 파일과 같은 형식의 `CHANGES.md`를 만든다.
