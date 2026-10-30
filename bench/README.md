# bench: 규칙 실측용 시험지와 채점 도구

규칙을 바꾸거나 `personal.md`의 규칙을 승격할 때, 기존보다 나빠지지 않았는지 확인하는 데 쓴다. 방법과 지난 결과는 `docs/EVALUATION.md`에 있다.

## 들어 있는 것

- `items/`: 말투 4개 x 6문항 = 24문항(정리형 2, 변환형 3, 통제형 1). 모두 가상의 글이다.
  - 각 파일: frontmatter(보존해야 할 사실 `preserve` 등) + `## 원문` + `## 좋은 답이 갖출 점`(채점용)
- `items.json`: 문항 목록
- `tools/score.py`: 자동 채점(보존 사실, 통제형 변경 문장 수, 분량, 가운뎃점, 숨은 문자)
- `tools/blind.py`: 답안 출처를 가리고 섞어 채점자용 묶음을 만든다
- `tools/aggregate.py`: 채점 결과를 말투별로 모으고 기준선과 비교한다

## 돌리는 순서

1. **답안 만들기**: 비교할 규칙 판마다(예: `baseline`, `new-rule`) 독립된 에이전트가 문항 원문과 `register`, `instruction`만 보고 변환한다. **"좋은 답이 갖출 점"은 보여 주지 않는다.** 결과는 `bench/outputs/<판 이름>/<문항 id>.md`에 본문만 저장한다.
2. **자동 채점**:
   ```bash
   python3 bench/tools/score.py bench/outputs/*
   ```
3. **이름 가리기**: 말투를 좁혀서 비교할 수 있다.
   ```bash
   python3 bench/tools/blind.py judging gongmun=baseline,new-rule
   ```
   `bench/judging/packets/`가 채점자용, `bench/judging/.key/`는 대응표다(채점자에게 보여 주지 않는다).
4. **독립 채점**: 서로 다른 채점자 2명이 묶음만 보고 답안마다 ai, register, meaning, publish를 1~5점으로 채점해 JSON으로 낸다. 형식은 `aggregate.py` 머리 주석 참고. 결과를 `bench/judging/raw/<채점자>.json`으로 저장한다.
5. **집계**:
   ```bash
   python3 bench/tools/aggregate.py judging
   ```

## 채택 기준

- 기준선 대비 평균 차이가 **+1점 이상**이고 패보다 승이 많을 때 채택한다. 1점 안팎은 실행마다 바뀌는 잡음일 수 있다.
- 자동 채점에서 보존 사실이 빠지거나 통제형을 3문장 이상 고치면 채택하지 않는다.
- 규칙 예시에 시험지 문장을 그대로 쓰지 않는다(과적합 방지).

`bench/outputs/`, `bench/judging/`은 git에 올리지 않는다.
