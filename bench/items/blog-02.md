---
id: blog-02
register: blog
type: 정리형
source_style: "블로그 ~합니다체(AI 티 많음)"
topic: "IT: 집 NAS 사진 백업 자동화"
target: "블로그(~다체 글말, 한 사람이 쓰는 글)"
instruction: "이 블로그 글의 AI 티를 걷어내 주세요. 블로그 말투는 그대로 둡니다."
planted_patterns: ["5_openers_closers", "3_translationese", "4_geotida_ireohan_haedang", "6_passive", "7_connectives", "8_parallelism", "1_intensifiers", "11_hedging", "12_llm_vocab", "10_emoji"]
preserve:
  - {"value": "3월", "kind": "date", "exact": true}
  - {"value": "두 달", "kind": "number", "exact": true}
  - {"value": "하늘NAS H2", "kind": "name", "exact": true}
  - {"value": "4TB", "kind": "number", "exact": true}
  - {"value": "새벽 2시 30분", "kind": "time", "exact": true}
  - {"value": "30 2 * * * rsync -av --delete /photos/ /backup/photos/", "kind": "code", "exact": true}
  - {"value": "--delete", "kind": "code", "exact": true}
  - {"value": "주 1회", "kind": "number", "exact": true}
  - {"value": "3시간 40분", "kind": "time", "exact": true}
  - {"value": "6분", "kind": "time", "exact": true}
  - {"value": "2,800원", "kind": "money", "exact": true}
length: 731  # 원문 글자 수(공백 포함, 줄바꿈 제외). 목표 범위 600~1000
---
# blog-02 (정리형): IT: 집 NAS 사진 백업 자동화

요청 문구: 이 블로그 글의 AI 티를 걷어내 주세요. 블로그 말투는 그대로 둡니다.

## 원문

안녕하세요! 오늘은 제가 집에서 사용하는 NAS의 사진 백업을 자동화한 과정에 대해 살펴보도록 하겠습니다.

저는 그동안 사진 백업을 수동으로 진행해 왔습니다. 한 달에 한 번 외장하드를 연결해 복사하는 방식이었는데, 지난 3월에는 이를 깜빡해서 무려 두 달 치 사진을 잃을 뻔했습니다. 이러한 문제를 극복하기 위해 자동화 방법을 모색하게 되었습니다.

사용한 장비는 하늘NAS H2이고, 4TB 디스크 두 개를 넣었습니다. 백업 도구로는 rsync를 활용했으며, 매일 새벽 2시 30분에 실행되도록 cron을 설정했습니다. 실제 설정은 다음과 같습니다.

`30 2 * * * rsync -av --delete /photos/ /backup/photos/`

여기서 주의해야 할 점은 --delete 옵션입니다. 해당 옵션은 원본에서 지워진 파일을 백업에서도 지우기 때문에, 실수로 원본을 지우면 백업도 함께 사라질 수 있습니다. 따라서 저는 주 1회 별도 스냅숏을 추가로 남기도록 구성했습니다.

결과는 매우 만족스러웠습니다. 첫 백업에는 약 3시간 40분이 소요되었지만, 이후에는 변경된 파일만 복사되기 때문에 평균 6분 정도면 완료됩니다. 전기 요금도 한 달에 약 2,800원 수준이라 부담이 크지 않은 것 같습니다.

자동화를 통해 얻은 가장 큰 가치는 시간 절약, 안정성 향상, 그리고 마음의 평화라고 할 수 있습니다. 여러분도 한번 시도해 보시는 건 어떨까요? 궁금한 점이 있으시면 언제든지 댓글로 남겨 주세요! 😊

## 좋은 답이 갖출 점

- 코드 줄과 `--delete`, 시간, 용량, 금액은 한 글자도 바꾸지 않는다.
- 어미는 ~다체로 바꾸는 것이 기본값이다. ~합니다체로 일관되게 유지했다면 어미만으로 감점하지 않는다(검수 질문 참고).
- "다음과 같습니다" 뒤 코드 블록 구조와 "주의할 점" 경고는 남긴다(정보 손실 금지).
- 마지막 3항 나열과 장식성 마무리, 이모지를 줄이되 원문에 없는 결론 문단을 만들지 않는다.
