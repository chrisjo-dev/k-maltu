---
id: gongmun-04
register: gongmun
type: 변환형
source_style: "블로그식 홍보글"
topic: "공공 안내: 구립도서관 저녁 독서 모임 참가자 모집"
target: "공문서(개조식, 항목 기호, 2026. 10. 30. 날짜, 붙임, 끝.)"
instruction: "이 홍보글을 공문서 형식으로 바꿔 주세요."
planted_patterns: ["5_openers_closers", "1_intensifiers", "9_honorific", "10_emoji", "11_hedging"]
preserve:
  - {"value": "달빛구립도서관", "kind": "name", "exact": true}
  - {"value": "퇴근길 한 권", "kind": "name", "exact": true}
  - {"value": "2026년 11월 10일부터 12월 15일까지", "kind": "date", "exact": false, "note": "2026. 11. 10.~2026. 12. 15. 표기 허용"}
  - {"value": "매주 화요일 저녁 7시 30분", "kind": "time", "exact": false, "note": "19:30 표기 허용"}
  - {"value": "2층 세미나실", "kind": "name", "exact": true}
  - {"value": "6회", "kind": "number", "exact": true}
  - {"value": "15명", "kind": "number", "exact": true}
  - {"value": "무료", "kind": "money", "exact": true}
  - {"value": "세 권", "kind": "number", "exact": true}
  - {"value": "10월 26일부터 11월 3일까지", "kind": "date", "exact": false, "note": "연도 미기재. 표기 변경 허용"}
  - {"value": "https://example.com/dalbit-library/apply", "kind": "url", "exact": true}
  - {"value": "02-000-0000", "kind": "number", "exact": true}
  - {"value": "끝까지 못 읽어도 괜찮으니 일단 오시라", "kind": "quote", "exact": true, "optional": true, "note": "공문에서는 인용 생략 허용(검수 결정 4). 남긴다면 그대로"}
length: 474  # 원문 글자 수(공백 포함, 줄바꿈 제외). 목표 범위 300~700
---
# gongmun-04 (변환형): 공공 안내: 구립도서관 저녁 독서 모임 참가자 모집

요청 문구: 이 홍보글을 공문서 형식으로 바꿔 주세요.

## 원문

책 좋아하는 분들 주목해 주세요! 달빛구립도서관에서 아주 특별한 프로그램을 준비했다고 해서 소개해 드리려고 합니다.

프로그램 이름은 '퇴근길 한 권'이에요. 직장인을 위한 저녁 독서 모임으로, 2026년 11월 10일부터 12월 15일까지 매주 화요일 저녁 7시 30분에 도서관 2층 세미나실에서 열린다고 해요. 총 6회 과정이고, 정원은 15명이에요.

무엇보다 좋은 점은 참가비가 완전 무료라는 거예요! 게다가 교재로 쓰는 책 세 권도 도서관에서 빌려준대요. 담당 사서 선생님은 "끝까지 못 읽어도 괜찮으니 일단 오시라"고 하셨어요.

신청은 10월 26일부터 11월 3일까지 도서관 누리집(https://example.com/dalbit-library/apply)에서 선착순으로 받는다고 하니 서두르세요. 문의는 02-000-0000으로 하면 된다고 합니다.

혼자 읽기 어려웠던 책, 이번 기회에 함께 읽어 보는 건 어떨까요? 정말 강력 추천합니다! 📚

## 좋은 답이 갖출 점

- 도서관이 관내 기관에 보내는 모집 안내/홍보 협조 공문이 된다(제목 한 줄, 1. 가. 항목).
- 기간, 요일, 시각(19:30), 장소, 횟수, 정원, 참가비, 신청 기간과 방법, 문의처가 빠짐없이 항목으로 들어간다.
- "~라고 해요" 같은 전언체와 추천, 감탄, 이모지가 사라진다. 원문에 없는 담당자 이름이나 문서번호를 만들지 않는다.
- 날짜 표기가 한 가지로 통일되고 마지막에 "끝."이 있다.
