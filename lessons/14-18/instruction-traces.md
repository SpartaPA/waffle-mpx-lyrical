# 강의별 지시문과 코드 추적

## 14강 · 오래된 관측이면 왜 팔이 출발하지 않을까요?

“파란 블록을 초록 칸으로 옮겨” · 01-파란 사례, 관측 나이 1.2초

[통합 교안 23쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_trace_14_flow)

1. **대상 선택** run_case()가 “파란”을 찾아 color=blue로 정합니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L96-L103)
2. **요청 생성** ground()의 월드 좌표에 unit=m, age_s=1.2를 붙입니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L103-L106)
3. **계약 검사** contract()에서 0 ≤ 1.2 ≤ 0.4가 거짓이므로 Reject를 냅니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L23-L31)
4. **종료 사유** benchmark()가 contract.stale을 받아 기대값과 대조합니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L117-L130)

같은 입력에서 기준선은 completed, 검증 경로는 contract.stale을 반환했습니다. 이 사례는 저장 기록을 쓰는 계약 검사입니다. [실행 기록](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/lesson-18.json)

시간 검사가 결과를 바꾸는 한 줄

```text
if not 0 <= goal["age_s"] <= .4:
    raise Reject("contract.stale")
```

0.4초 경계는 포함합니다. 이번 입력은 1.2초여서 좌표가 유효해도 요청을 거부합니다. 기대한 거부 사유가 일치해 correct=true입니다. [코드](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L23-L31)

## 15강 · “파란 블록”은 영상의 어느 점일까요?

“파란 블록을 초록 칸으로 옮겨” · 00-파란 사례에서 대상 위치를 복원합니다.

[통합 교안 39쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_trace_15_flow)

1. **지시 → 색** run_case()가 “파란”을 blue로 바꾸고 ground()에 넘깁니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L96-L104)
2. **색 → 픽셀** blue는 RGB의 2번 축입니다. 색·밝기·깊이 검사 후 16,850개가 남습니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L34-L46)
3. **픽셀 → 점** (288,284)의 Z는 0.07257 m입니다. fx와 fy는 약 457.6 px입니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L44-L49)
4. **점 → 월드** 모든 점을 월드로 변환한 뒤 축별 중앙값 (0.199, 0.044, 0.051) m를 얻습니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L47-L50)

계산은 records/blue/start.png와 rgbd.npz에 저장한 동일 프레임을 사용합니다. 파란 마스크 안의 한 픽셀과 전체 대표점을 구분합니다. [실행 기록](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/lesson-15.json)

한 픽셀의 깊이를 미터 좌표로 바꿉니다

```text
u, v = 288, 284
cx, cy = 320, 240
X = (288 - 320) * 0.07257 / 457.6
Y = (284 - 240) * 0.07257 / 457.6
```

X ≈ −0.00507 m, Y ≈ +0.00698 m입니다. 이 점은 주점보다 왼쪽·아래에 있습니다. 전체 표면의 월드 대표점은 모든 유효 점으로 계산합니다. [코드](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L41-L50)

## 16강 · 파란 블록 지시에서 첫 관절 목표까지

실제 정책 입력 · “Pick up the blue cube and place it on the green square.”

[통합 교안 58쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_trace_16_flow)

1. **관측 결합** 시작 영상·영어 지시·로봇 상태를 ColorPolicy.plan()에서 특징으로 만듭니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/learning/color_imitation.py#L39-L58)
2. **궤적 생성** 회귀 헤드가 92×7 배열을 냅니다. 첫 행의 joint1 후보는 0.17624 rad입니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/sim/evaluate_pick_place.py#L296-L305)
3. **이동 제한** 시작각 0.30706 rad에서 한 번에 최대 0.0875 rad만 이동합니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/sim/evaluate_pick_place.py#L305-L314)
4. **물리 결과** 첫 적용 목표는 0.21956 rad입니다. 운반 뒤 파란 블록이 1.95초간 안정됐습니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/blue/result.json)

실행 로그에서 목표 물체 최대 상승은 약 59.1 mm, wrong_pick=false, success=true입니다. [실행 기록](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/blue/result.json)

후보와 적용값이 다른 이유를 계산합니다

```text
q = 0.30706
candidate = 0.17624
change = candidate - q  # -0.13082
applied = q - 0.0875    #  0.21956
```

원래 후보의 변화량이 한 스텝 제한을 넘습니다. 실행기는 팔 네 축과 그리퍼에 각각 제한을 적용하고 다음 관절 목표를 물리 엔진에 전달합니다. [코드](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/sim/evaluate_pick_place.py#L305-L316)

## 17강 · 안착 조건을 물었을 때 원문까지 따라갑니다

실제 질의 · “블록 운반 후 안착 조건은 무엇인가요?” · 매뉴얼 버전 2

[통합 교안 73쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_trace_17_flow)

1. **검색 입력** answer()가 질문과 버전 “2”를 retrieve()에 보냅니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L62-L76)
2. **문서 선택** 버전 1을 제외합니다. 버전 2 안착 문서와 질문은 검색어 5개가 겹칩니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/manual.json)
3. **모델 응답** Qwen2.5 7B에 질문과 근거를 전달해 원문 인용과 조각 ID를 받습니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L77-L81)
4. **인용 확인** ID는 table-v2-settle입니다. 같은 조각 안에서 인용문을 찾아 cited를 냅니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L81-L82)

실제 응답은 “블록 운반 후 목표 칸 안에서 약 0.5초 이상 안정된 상태를 확인합니다.”입니다. [실행 기록](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/lesson-17.json)

검색 점수와 인용 검사를 분리해서 읽습니다

```text
words = {블록, 운반, 후, 안착, 조건은, 무엇인가요}
일치 = {블록, 운반, 후, 안착, 조건은}
score = 5
retrieved = ["table-v2-settle"]
```

검색 점수 5는 겹치는 단어 개수입니다. cited는 ID와 인용문 대조 결과입니다. 블록이 지금 안착했는지는 센서 기록에서 판정합니다. [코드](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/lab.py#L62-L82)

## 18강 · 전후 사진을 요구하면 어떤 순서로 실행할까요?

“작업 전과 후의 사진을 한 장씩 남겨. 그 사이에 파란 큐브를 초록 칸에 옮겨 줘.”

[통합 교안 89쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_trace_18_flow)

1. **계획 생성** Qwen이 [photo, place_blue, photo]를 생성합니다. 최초 계획을 저장합니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/sim/instruction_loop.py#L118-L141)
2. **의존성 부여** next()가 첫 턴은 [], 다음 턴은 [0], 그다음은 [1]로 연결합니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/sim/instruction_loop.py#L165-L180)
3. **물리 실행** 0번에서 촬영, 1번에서 파랑을 운반, 2번에서 결과를 촬영합니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/missions/budget6/turns.jsonl)
4. **독립 채점** score()가 순서·사진·물체 위치를 확인합니다. 최종 오차 4.9 mm, 성공입니다. [해당 단계](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/13-react/evaluation/score.py#L26-L118)

같은 지시와 배치의 2턴 시험은 운반 뒤 멈춰 사진 1장이 부족했습니다. 6턴 시험은 요구한 사진 2장을 남겼습니다. [실행 기록](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/lessons/14-18/records/missions/budget6/score.json)

계획의 색상 토큰이 실제 행동으로 바뀝니다

```text
place_blue → action="place", color="blue"
turn 0 → photo-00.png
turn 1 → center_error_m ≈ 0.00486
turn 2 → photo-02.png
turn 3 → finish
```

운반 턴 직후의 오차는 4.86 mm입니다. 독립 채점기는 종료 상태의 좌표로 4.9 mm를 계산합니다. 종료 선언과 지시 충족 여부를 나눠 확인합니다. [코드](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/e96ce170cd9eabf5e44fb0eceb016af132c1d4ad/sim/instruction_loop.py#L302-L329)

