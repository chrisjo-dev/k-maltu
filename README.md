# k-maltu

한국어 글을 원하는 말투로 바꾸면서 AI 문체를 걷어내고, 숨은 문자와 이미지 메타데이터를 지우는 Claude Code skill.

말투는 네 가지다: **blog**(블로그), **threads**(스레드, X), **dc**(디씨 같은 커뮤니티), **gongmun**(공문서).

## 무엇을 하나

| 층 | 하는 일 | 누가 |
|---|---|---|
| 1. AI 문체 빼기 | 강조어 남발, 번역체, "것이다/이러한/해당" 과다, 판에 박힌 인사 같은 AI 티를 고친다 | 모델(korean-humanizer 카탈로그) |
| 2. 말투 맞추기 | 말투별 어미, 길이, 형식 규칙을 적용한다. 말투마다 1층 카테고리를 켜고 끈다 | 모델(`registers/*.md`) |
| 3. 숨은 문자와 메타데이터 정리 | 제로폭 문자, 태그 문자 같은 숨은 문자와 PNG/JPEG 메타데이터(EXIF, XMP, IPTC, C2PA)를 지운다 | 스크립트(`scripts/`) |

처리 순서는 점검(읽기 전용) → 개인정보 후보 확인(사용자 승인) → 말투 선택 → 1, 2층 → 3층(항상 마지막) → 사실 보존 검증 → 새 파일로 저장과 변경 보고다. 원본 파일은 덮어쓰지 않는다. 자세한 흐름은 [SKILL.md](SKILL.md).

### 말투별 차이

| 말투 | 어미 | 분량 | 수정량 상한 | humanizer에서 끄는 것 |
|---|---|---|---|---|
| blog | ~다체 | 원문 90% 이상 | 지킴(문단당 3곳 미만, 문장 20% 이하) | 없음 |
| threads | 반말 또는 ~요체 | 한 덩어리 500자 안팎, 길면 연결 글 | 대신 의미, 숫자, 고유명사, 링크 보존만 강제 | 없음(더 세게) |
| dc | 음슴체 또는 반말 | 짧게 | 대신 의미, 숫자, 고유명사, 링크 보존만 강제 | 없음(정돈된 느낌 제거를 더 세게) |
| gongmun | ~함, ~바람 | 원문 90% 이상 | 지킴 | "것이다/이러한/해당", 번역체 일부("~에 따라"), 격식 연결어 |

dc 말투 규칙에는 혐오, 비하, 지역 비하 어미, 욕설을 만드는 규칙이 없다. 원문에 그런 표현이 있으면 알리고 묻는다.

## 설치

```sh
git clone https://github.com/chrisjo-dev/k-maltu.git ~/.claude/skills/k-maltu
```

> **korean-humanizer를 이미 쓰고 있다면** 둘 중 하나만 켜 두는 것을 권한다. k-maltu는 korean-humanizer의 규칙을 복사해 품고 있고, "AI 티 빼줘" 같은 트리거 문구도 겹친다. 둘 다 켜 두면 어느 skill이 실행될지 예측하기 어렵다. 예: `rm ~/.claude/skills/korean-humanizer` (링크로 설치한 경우)

또는 이미 받은 폴더를 링크로 건다.

```sh
ln -s /path/to/k-maltu ~/.claude/skills/k-maltu
```

스크립트는 파이썬 3.10 이상, 표준 라이브러리만 쓴다. 따로 설치할 패키지는 없다.

개인 규칙을 쓰려면 템플릿을 복사해서 채운다. `styles/personal.md`는 git에 올라가지 않는다.

```sh
cp styles/personal.example.md styles/personal.md
```

## 사용 예

Claude Code에서:

```
이 글 블로그 말투로 다듬고 AI 티 빼 줘. 숨은 문자랑 이미지 메타데이터도 지워 줘. drafts/post.md
```

스크립트만 따로 쓸 수도 있다.

```sh
# 점검(아무것도 바꾸지 않음)
python3 scripts/inspect_report.py drafts/post.md drafts/images/*.png

# 숨은 문자 정리 -> drafts/post.cleaned.md (원본 유지, 코드 블록은 건드리지 않음)
python3 scripts/clean_text.py drafts/post.md
python3 scripts/clean_text.py drafts/post.md --check     # 확인만, 지울 문자가 있으면 exit 1

# 이미지 메타데이터 정리 -> out/images/ (원본 유지, 픽셀 재인코딩 없음)
python3 scripts/clean_images.py drafts/images/*.png -d out/images

# 원문과 결과 비교: 숫자, URL, 링크, 코드, 숨은 문자, 금지 문자, 이미지 경로
python3 scripts/verify.py drafts/post.md drafts/post.cleaned.md --forbid U+00B7

# vendor 원본과 styles 수정본의 차이
scripts/diff_upstream.sh
```

테스트:

```sh
python3 -m unittest discover -s tests -v
```

## 한계

- 지우는 것은 **숨은 문자와 메타데이터뿐**이다. 단어 선택 확률에 심는 통계적 워터마크와 이미지 픽셀 워터마크는 지우지 않는다.
- **AI 탐지기 통과를 보장하지 않는다.** 목표는 자연스러운 글과 깨끗한 파일이다.
- **본인이 쓰거나 권리를 가진 콘텐츠에만** 쓴다. 남의 글에서 출처나 저작권 정보를 지우는 용도가 아니다.
- 공백 동형 문자(U+00A0, U+3000 등)는 기본으로 보고만 한다. 일부러 넣은 줄바꿈 없는 공백일 수 있어서다.
- 마크다운 펜스 코드 블록과 인라인 코드는 정리하지 않는다(보고만). 들여쓰기 코드 블록은 코드로 보지 않는다.
- 개인정보 후보는 정규식으로 찾는다. 이미지 속 글자는 스크립트가 보지 못하므로 모델이 이미지를 보고 후보를 알리고, 사용자가 승인한 곳만 가린다.
- JPEG EXIF를 지우면 회전 정보도 사라진다. 회전 값이 있으면 경고한다.
- 공문서 규칙은 행정안전부 행정업무운영편람의 작성 원칙을 바탕으로 했지만 세부 조항을 옮겨 적지는 않았다. 기관 지침이 있으면 그것이 우선이다.

## 저장소 구조

```
SKILL.md              skill 진입점(워크플로우)
registers/            말투 규칙 4개
styles/base/          humanizer 카탈로그 고친 판 + CHANGES.md
styles/personal.example.md   개인 규칙 템플릿
scripts/              inspect, clean_text, clean_images, verify, diff_upstream.sh
vendor/               가져온 원본 그대로 + ORIGIN.md
examples/             말투별 전후 예시(가상의 글)
tests/                unittest
```

원본(vendor)과 수정본(styles)을 나눠 둔 것은 다른 한국어 문체 스킬을 더 가져와 고쳐 쓰기 위해서다. 새로 가져올 때는 `vendor/<이름>/`에 원본과 `ORIGIN.md`를, 고친 판은 `styles/<묶음>/`에 `CHANGES.md`와 함께 둔다.

## 출처와 라이선스

k-maltu는 MIT 라이선스다([LICENSE](LICENSE)). 다음 두 MIT 프로젝트를 포함한다. 고지 전문은 [NOTICE](NOTICE).

- [korean-humanizer](https://github.com/dotoricode/korean-humanizer) v1.0.1, Copyright (c) 2026 dotoricode. AI 문체 카탈로그와 과교정 방지 원칙. `vendor/korean-humanizer/`에 원본, `styles/base/`에 고친 판.
- [watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) (commit 5c18093), Copyright (c) 2026 Guillaume Meyer and contributors. 숨은 문자 판정 `text_unicode.py` 한 파일만 원본 그대로 가져왔다. 서버, Docker, 통계적 워터마크 대응 재작성은 포함하지 않는다.

---

## English summary

k-maltu is a Claude Code skill for Korean text. It (1) removes "AI-sounding" Korean phrasing using the korean-humanizer catalog, (2) rewrites text into one of four registers (blog, threads, dc community style, gongmun official documents), each with its own rules and per-category humanizer switches, and (3) strips invisible Unicode characters and PNG/JPEG metadata (EXIF, XMP, IPTC, C2PA) with standard-library Python scripts, preserving Markdown code, emoji sequences, flag tags, and Hangul fillers after jamo. A verify step checks that numbers, URLs, links, image paths, and code blocks are unchanged. Original files are never overwritten. It does not remove statistical (token-sampling) or pixel watermarks and does not promise to evade AI detectors. Use it only on content you own. MIT licensed; includes MIT-licensed code from korean-humanizer and watermarks-remover (see NOTICE).
