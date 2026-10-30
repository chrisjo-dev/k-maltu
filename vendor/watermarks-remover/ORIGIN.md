# 출처: watermarks-remover

| 항목 | 값 |
|---|---|
| 원작 | watermarks-remover (Guillaume Meyer and contributors) |
| 저장소 | https://github.com/guillaumemeyer/watermarks-remover |
| 커밋 | 5c180932a00c793261177f79aee21db8929f3fe2 |
| 원본 경로 | `service/scripts/text_unicode.py` (730줄), `LICENSE` |
| 복사일 | 2026-10-30 |
| 라이선스 | MIT, Copyright (c) 2026 Guillaume Meyer and contributors (같은 폴더 `LICENSE`) |

## 규칙

- `text_unicode.py`는 원본 그대로 둔다. 동작을 바꿀 일이 있으면 이 파일이 아니라 `scripts/clean_text.py`에서 호출 옵션을 바꾼다.
- 가져온 것은 숨은 문자 판정(A층) 하나뿐이다. HTTP 서버, Docker, 통계적 워터마크 대응 재작성(B층, mlm/roberta), humanize_pass, stylometry, 자동 훅은 가져오지 않았다.

## 복사 전 점검(2026-10-30)

파일 전체를 읽고 확인했다.

- import: `unicodedata`, `collections.Counter`, `dataclasses`, `difflib.SequenceMatcher`, `__future__` 뿐. 표준 라이브러리만 쓴다.
- 네트워크(socket, urllib, http, requests) 없음.
- 파일 열기, 쓰기, 삭제(open, pathlib, os, shutil) 없음.
- 외부 실행(subprocess, os.system, eval, exec, compile, `__import__`) 없음.
- 모듈을 불러올 때 실행되는 코드는 상수 정의뿐이다.

## ko-maltu에서 쓰는 방식

- `clean_text(text, nfkc=False, aggressive_homoglyphs=False, normalize_spaces=False, strip_emoji_glue=False, strip_bidi=False)`
  원본 함수의 기본값은 `normalize_spaces=True`라서 공백 동형 문자(U+00A0, U+3000 등)를 U+0020으로 바꾼다. ko-maltu는 이 값을 끄고 보고만 한다.
- `inspect_text(text)`: 점검 보고에 쓴다. 이 함수는 공백 동형 문자와 방향 제어 문자를 항상 보고하므로, 보고에 나와도 정리 때 지워지지 않는 문자가 있다(LRM, RLM, 격리 문자 등).
- 원본은 마크다운 코드 블록을 구분하지 않는다. 코드 보호는 `scripts/mdsegments.py`가 맡는다.
