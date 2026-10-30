# 출처: korean-humanizer

| 항목 | 값 |
|---|---|
| 원작 | korean-humanizer (dotoricode) |
| 저장소 | https://github.com/dotoricode/korean-humanizer |
| 버전 | 1.0.1 (CHANGELOG 기준 2026-06-02) |
| 복사한 위치 | https://github.com/dotoricode/korean-humanizer 의 v1.0.1 설치본 |
| 복사일 | 2026-10-30 |
| 라이선스 | MIT, Copyright (c) 2026 dotoricode (같은 폴더 `LICENSE`) |

## 규칙

- 이 폴더의 파일은 원본 그대로 둔다. 고칠 일이 있으면 `styles/` 아래 수정본을 고치고 `styles/<묶음>/CHANGES.md`에 적는다.
- 원본과 수정본 차이는 `scripts/diff_upstream.sh`로 본다.
- 새 버전으로 올릴 때는 이 폴더를 통째로 바꾸고 위 표의 버전, 복사일, 원본 커밋을 고친 뒤 `diff_upstream.sh`로 수정본에 옮길 변경을 확인한다.

## 가져온 파일

`SKILL.md`, `PROMPT.md`, `PROMPT.short.md`, `CHEATSHEET.md`, `CHANGELOG.md`, `LICENSE`, `README.md`, `references/`, `examples/`, `eval/`, `scripts/eval-harness.py`, `scripts/eval-harness.sh`

## 뺀 파일

- `docs/` (출시, 베타, 마이그레이션 문서), `roadmap/`, `ROADMAP.md`
- `.github/` (이슈 템플릿, lint 워크플로), `.markdownlint.yml`, `.gitignore`
- `AGENTS.md`, `CONTEXT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `README.ko.md`, `README.zh-CN.md`
- `assets/` (소개 카드 이미지)
- `scripts/` 중 eval 외 스크립트: `check-codex-skill.sh`, `install-codex-skill.sh`, `lint-cross-file.sh`, `lint-examples.sh`, `lint-patterns.sh`

뺀 파일은 k-maltu 동작에 쓰이지 않는다. 필요하면 원작 저장소에서 본다.

## 참고

원본 문서에는 가운뎃점(U+00B7)이 들어 있다. 원본 보존 원칙에 따라 이 폴더에서는 고치지 않았고, `styles/base/` 수정본에서는 슬래시로 바꿨다.
