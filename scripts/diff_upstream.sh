#!/bin/sh
# vendor 원본과 styles 수정본의 차이를 보여 준다.
# styles/<묶음>/ 아래 각 파일과 이름이 같은 파일을 vendor/ 아래에서 찾아 diff -u로 비교한다.
# 사용: scripts/diff_upstream.sh            (전체)
#       scripts/diff_upstream.sh ko-ai-signals.md   (파일 하나)
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT" || exit 2

status=0
for mod in styles/*/*.md; do
  name=$(basename "$mod")
  [ "$name" = "CHANGES.md" ] && continue
  if [ $# -gt 0 ] && [ "$1" != "$name" ]; then
    continue
  fi
  orig=$(find vendor -type f -name "$name" | head -n 1)
  if [ -z "$orig" ]; then
    echo "== $mod: vendor에 같은 이름의 원본이 없습니다(k-maltu에서 새로 쓴 파일)"
    continue
  fi
  echo "== $orig -> $mod"
  diff -u "$orig" "$mod" || status=1
done
# 차이가 있으면 1을 돌려준다(diff와 같은 규칙).
exit $status
