---
id: threads-03
register: threads
type: 변환형
source_style: "보도자료체"
topic: "동네 행사: 주민 나눔장터 개최"
target: "스레드(첫 줄 훅, 짧은 줄바꿈, 한 덩어리 500자 안팎)"
instruction: "이 보도자료를 스레드 글로 바꿔 주세요."
planted_patterns: ["12_llm_vocab", "6_passive", "7_connectives", "8_parallelism", "2_empty_adjectives", "3_translationese"]
preserve:
  - {"value": "해오름동 주민자치회", "kind": "name", "exact": true}
  - {"value": "11월 14일(토)", "kind": "date", "exact": true}
  - {"value": "오전 10시", "kind": "time", "exact": true}
  - {"value": "오후 4시", "kind": "time", "exact": true}
  - {"value": "해오름근린공원 잔디광장", "kind": "name", "exact": true}
  - {"value": "제3회 해오름 나눔장터", "kind": "name", "exact": true}
  - {"value": "60개", "kind": "number", "exact": true}
  - {"value": "10,000원", "kind": "money", "exact": true}
  - {"value": "10%", "kind": "number", "exact": true}
  - {"value": "11월 6일", "kind": "date", "exact": true}
  - {"value": "https://example.com/haeoreum/market", "kind": "url", "exact": true}
  - {"value": "박도윤", "kind": "name", "exact": true}
  - {"value": "작년에는 비가 와서 절반만 열렸다. 올해는 제대로 해 보고 싶다", "kind": "quote", "exact": true}
  - {"value": "해오름동 주민센터 3층 강당", "kind": "name", "exact": true}
length: 459  # 원문 글자 수(공백 포함, 줄바꿈 제외). 목표 범위 300~700
---
# threads-03 (변환형): 동네 행사: 주민 나눔장터 개최

요청 문구: 이 보도자료를 스레드 글로 바꿔 주세요.

## 원문

해오름동 주민자치회는 오는 11월 14일(토) 오전 10시부터 오후 4시까지 해오름근린공원 잔디광장에서 '제3회 해오름 나눔장터'를 개최한다고 밝혔다.

이번 행사는 지역 주민 간의 교류 활성화와 자원 순환 문화 확산을 도모하기 위한 일환으로 마련되었으며, 총 60개의 판매 부스가 운영될 예정이다. 판매 부스 참가비는 1팀당 10,000원이며, 수익금의 10%는 지역 아동센터에 기부된다.

부스 신청은 11월 6일까지 온라인(https://example.com/haeoreum/market)으로 접수되며, 선착순으로 마감된다. 아울러 행사 당일에는 어린이 그림 그리기 대회, 중고 책 교환 코너, 그리고 먹거리 장터 등 다양한 부대 행사가 함께 진행될 예정이다.

주민자치회 박도윤 회장은 "작년에는 비가 와서 절반만 열렸다. 올해는 제대로 해 보고 싶다"고 말했다.

우천 시에는 해오름동 주민센터 3층 강당으로 장소가 변경된다.

## 좋은 답이 갖출 점

- 첫 줄에 날짜와 행사 이름 같은 핵심이 온다.
- 어미는 ~요체나 반말 중 하나로 통일한다(원문이 보도체라 선택은 자유).
- 신청 마감(11월 6일, 선착순), 참가비, 기부 비율, 우천 시 장소처럼 행동에 필요한 정보가 하나도 빠지지 않는다. 길면 1/2, 2/2로 나누고 링크는 마지막 덩어리에.
- "도모하기 위한 일환", "다양한 부대 행사" 같은 문구를 걷어낸다. 과장 훅("놓치면 손해")은 감점.
