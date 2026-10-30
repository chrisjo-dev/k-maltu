---
id: blog-03
register: blog
type: 변환형
source_style: "보도자료체"
topic: "제품: 가계부 앱 2.0 업데이트"
target: "블로그(~다체 글말, 한 사람이 쓰는 글)"
instruction: "이 보도자료를 블로그 글로 바꿔 주세요."
planted_patterns: ["2_empty_adjectives", "1_intensifiers", "8_parallelism", "4_geotida_ireohan_haedang", "6_passive", "12_llm_vocab", "7_connectives", "3_translationese"]
preserve:
  - {"value": "가계부온", "kind": "name", "exact": true}
  - {"value": "온솔랩", "kind": "name", "exact": true}
  - {"value": "2.0", "kind": "number", "exact": true}
  - {"value": "2026년 10월 27일", "kind": "date", "exact": true}
  - {"value": "94.2%", "kind": "number", "exact": true}
  - {"value": "70%", "kind": "number", "exact": true}
  - {"value": "80%", "kind": "number", "exact": true}
  - {"value": "한서윤", "kind": "name", "exact": true}
  - {"value": "가계부는 꾸준히 쓰는 게 제일 어렵다. 그 귀찮음을 줄이는 데 집중했다", "kind": "quote", "exact": true}
  - {"value": "안드로이드 8.0", "kind": "number", "exact": true}
  - {"value": "iOS 16", "kind": "number", "exact": true}
  - {"value": "3,900원", "kind": "money", "exact": true}
  - {"value": "https://example.com/gagyebuon/2.0", "kind": "url", "exact": true}
length: 679  # 원문 글자 수(공백 포함, 줄바꿈 제외). 목표 범위 600~1000
---
# blog-03 (변환형): 제품: 가계부 앱 2.0 업데이트

요청 문구: 이 보도자료를 블로그 글로 바꿔 주세요.

## 원문

[보도자료] 가계부온, 2.0 업데이트로 사용자 경험 획기적 개선

2026년 10월 27일, 생활 금융 앱 가계부온(운영사 온솔랩)은 대규모 업데이트인 버전 2.0을 공식 출시했다고 밝혔다. 이번 업데이트는 사용자 편의성 극대화, 데이터 정확성 강화, 그리고 개인화 기능 확대라는 세 가지 핵심 가치를 중심으로 진행되었다.

가장 주목할 만한 변화는 영수증 자동 인식 기능의 도입이다. 해당 기능은 사용자가 촬영한 영수증 사진을 분석해 금액과 날짜, 가게 이름을 자동으로 입력해 주는 것으로, 내부 테스트 결과 인식 정확도는 94.2%로 측정되었다. 이는 기존 수동 입력 방식 대비 입력 시간을 평균 70% 단축시킬 수 있음을 시사한다.

또한 월별 예산 알림 기능이 새롭게 추가되었다. 사용자가 설정한 예산의 80%를 넘으면 푸시 알림이 발송되며, 이를 통해 사용자는 보다 체계적인 소비 관리를 도모할 수 있게 된다. 뿐만 아니라 다크 모드와 홈 화면 위젯 기능도 함께 제공된다.

온솔랩 한서윤 대표는 "가계부는 꾸준히 쓰는 게 제일 어렵다. 그 귀찮음을 줄이는 데 집중했다"고 전했다.

가계부온 2.0은 안드로이드 8.0 이상, iOS 16 이상에서 이용 가능하며, 기본 기능은 무료, 프리미엄 요금제는 월 3,900원이다. 자세한 내용은 https://example.com/gagyebuon/2.0 에서 확인할 수 있다.

## 좋은 답이 갖출 점

- 업데이트 소식을 정리하는 개인 블로그 글이 된다. 원문에 없는 사용 경험("써 봤더니")을 지어내지 않는다.
- "94.2%"는 내부 테스트 수치, "70% 단축"은 회사 주장이라는 출처 경계를 지운다면 감점한다.
- "획기적", "세 가지 핵심 가치", "극대화/강화/도모" 같은 홍보 문구를 구체적인 기능 설명으로 바꾼다.
- 대표 인용문, 지원 OS, 요금, URL이 모두 남아 있다.
