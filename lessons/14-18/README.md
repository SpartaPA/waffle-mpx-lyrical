# 14~18강 · 로봇 명령에서 작업 평가까지

[통합 Google Slides](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit) · [통합 PowerPoint](lessons-14-18.pptx) · [YouTube 시연](https://youtu.be/1vrGTaNn2sw) · [같은 영상의 MP4](media/waffle-labs-14-18.mp4)

이 실습은 Waffle MPX의 실제 Isaac Sim 기록으로 명령, 관측, 행동 후보, 작업 지식과 결과를 연결합니다. 수업 자료는 이 GitHub 브랜치에서 받습니다. 14~17강은 각 4시간, 18강은 6시간이며 발표자 노트에 수업 활동과 원문 링크가 있습니다.

## 준비

```bash
git clone --branch feature/open-instruction-vla https://github.com/SpartaPA/waffle-mpx-lyrical.git
cd waffle-mpx-lyrical/lessons/14-18
python3 -m venv /tmp/waffle-course-venv
source /tmp/waffle-course-venv/bin/activate
python -m pip install numpy Pillow
python lab.py 14
python lab.py 15 --color blue
python lab.py 16 --color blue
python lab.py 18
```

기록 재생에는 GPU가 필요하지 않습니다. 17강은 별도 Ollama 서버, 물리 재실행은 [Isaac Sim 6.1 설치](../../docs/install.md)와 [학습 환경](../../learning/README.md), Action 실습은 ROS 2 Lyrical 워크스페이스를 사용합니다. ROS와 Isaac에 설치된 환경을 사용할 때에는 별도 터미널을 엽니다.

## 14강 · 명령 계약과 ROS 2 Action

`lab.py 14`는 world 좌표의 유효 거리·단위·시각 계약을 검사합니다. 별도 ROS 실습에서는 팔 관절 이름 4개와 절대각(rad), 실행 시간 3초를 지정해 FollowJointTrajectory 액션을 보냅니다. 아래 두 터미널은 같은 호스트와 도메인을 사용합니다. 설치 경로는 [ROS 설치](../../docs/install.md)의 워크스페이스 기준입니다.

```bash
# 터미널 A
source ~/waffle_mpx/src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=184 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ros2 launch turtlebot3_manipulation_bringup robot.launch.py mode:=mock
```

```bash
# 터미널 B
source ~/waffle_mpx/src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=184 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
cd ~/waffle_mpx/src/lessons/14-18
python3 action_client.py
python3 action_client.py --cancel
```

검증 기록은 [정상 완료](records/action-complete.json)와 [취소](records/action-cancel.json)입니다. 취소 요청의 수락, 최종 CANCELED, 실제 모터가 정지한 시각은 별개입니다. 이 실습은 앞의 두 상태를 검증합니다. 모의 제어기 기록에는 실물 정지 지연이 포함되지 않습니다.

## 15강 · 멀티모달 임베딩과 Grounding

`python lab.py 15 --color blue`는 [실제 시작 RGB](records/blue/start.png)에서 파랑 단위 벡터와 픽셀 RGB의 코사인 유사도를 계산합니다. 유사도 0.92 초과, 해당 채널 45 초과, 유효 깊이라는 조건을 통과한 픽셀을 역투영합니다. [깊이와 보정](records/blue/rgbd.npz)의 단위는 m입니다. 같은 광학 영상면에 정렬된 깊이와 내부 파라미터를 사용하고 USD 카메라 축을 광학 축에 맞춘 뒤 월드 좌표로 변환합니다. 대표점은 가시 표면 점들의 축별 중앙값입니다.

`--color red`로 바꿔 위치를 비교합니다. 동일한 색상의 물체가 둘이면 마스크가 합쳐질 수 있습니다. 실제 용도에서는 개체 분리와 관측 시각에 맞는 TF가 필요합니다. 이 실습의 색상 벡터는 해석 가능한 공동 특징 공간을 사용하며, 물리 운반의 학습형 인코더는 16강에서 다룹니다.

## 16강 · VLA 행동 후보와 어댑터

`python lab.py 16 --color red` 또는 `--color blue`로 92개의 원래 후보와 적용값을 확인합니다. `learning/actions.py`가 정의하는 축은 차체 선속도(m/s), 각속도(rad/s), 팔 관절 4개(rad), 그리퍼(m)입니다. `adapt`는 축 순서·차원·유한값·범위·차체 정지를 검사합니다. 기록 재생에서 `rejected_raw`는 이 검사로 거부되는 원래 후보 수입니다. Isaac 실행기의 적용 기록에는 0.25초 단위 이동 제한도 반영됩니다.

모델은 SmolVLM2-500M 기반 부모 VLA와 `waffle-color-pose-111.npz` 회귀 헤드를 사용합니다. 이 체크포인트의 학습 시연, 시드와 해시는 [학습 보고서](../../learning/pose-evaluation/README.md)에 있습니다. LoRA는 교안의 비교 계산이며 이 체크포인트의 학습법은 궤적 회귀입니다.

## 17강 · 근거 검색과 생성

```bash
# Ollama 서버가 실행 중인 제어 PC
ollama pull qwen2.5:7b
python lab.py 17 --version 2 --query '블록 운반 후 안착 조건은 무엇인가요?'
python lab.py 17 --version 1 --query '블록 운반 후 안착 조건은 무엇인가요?'
python lab.py 17 --version 99
```

[수업용 매뉴얼](manual.json)의 버전을 필터링하고 질의 토큰과 일치하는 조각을 최대 두 개 찾습니다. Qwen2.5 7B가 반환한 ID와 인용문이 해당 조각에 있는지 확인합니다. 근거가 없으면 `no_evidence`, 인용을 검증할 수 없으면 `unsupported`입니다. 생성된 인용이 질문에 답하는지도 별도로 판독합니다. [실제 응답](records/lesson-17.json)

## 18강 · 통합 평가

```bash
python lab.py 18 > /tmp/waffle-planner-results.json
python -c 'import json; r=json.load(open("/tmp/waffle-planner-results.json")); print({k:(v["correct"],v["total"]) for k,v in r.items()})'
```

[고정 사례 20개](cases.json)는 요청과 기대 종료 사유를 함께 보관합니다. 평가기는 기대값을 채점에만 사용합니다. 한국어의 빨강·파랑 표현을 읽는 규칙 기반 기준선과 검증 경로를 동일한 기록에 적용합니다. 검증 경로에는 작업 그래프의 위상 정렬, 버전별 검색, RGB-D 후보, 좌표·단위·신선도 계약, 적용 관절값 검사가 있습니다. 도구 실패와 시간 초과를 주입한 사례도 포함합니다. 시간 초과는 결과 미확정으로 처리합니다. 이번 실행에서는 기준선 8/20, 검증 경로 20/20이 기대 종료 사유와 일치했습니다. [사례별 최초 종료 사유와 처리 시간](records/lesson-18.json)을 비교합니다. 20개는 오프라인 기록 재생이며 동일한 장면에서 실제로 실행한 물리 운반은 빨강과 파랑 각각 한 건입니다.

## Isaac Sim에서 영상 재현하기

워크스페이스에 생성한 scene.usda와 학습 의존성이 필요합니다. 새 출력 디렉터리를 지정합니다. `--record-frames`로 4 Hz의 실제 D435 프레임을 저장하고, `--capture-rgbd`로 각 시험의 첫 영상에 정렬한 깊이와 보정을 저장합니다.

```bash
cd ~/waffle_mpx/src
export WAFFLE_LEARNING_DEPS="$HOME/waffle_mpx/.learning-deps"
OUT="$HOME/waffle_mpx/lesson14-18-run-01"
"$HOME/isaacsim6_venv/bin/python" sim/evaluate_pick_place.py \
  "$HOME/waffle_mpx/simulation/scene.usda" learning/checkpoints/waffle-color-pose-111.npz "$OUT" \
  --controller color --parent-vla learning/checkpoints/waffle-hf-vla.pt \
  --seed 1927 --varied-poses --layouts 1 --decisions 92 --record-frames --capture-rgbd
python3 lessons/14-18/lab.py 15 --rgbd "$OUT/00-blue" --color blue
python3 lessons/14-18/record_demo.py "$OUT" "$OUT/demo.mp4"
```

영상 합성에는 ffmpeg와 Noto Sans CJK 폰트가 필요합니다. 출력 디렉터리의 result.json에서 지정 블록 파지, 다른 블록 파지 여부, 안정 시간과 성공 판정을 확인합니다. GitHub의 파랑 기록은 같은 시드의 별도 RGB-D 재실행에서 가져왔으므로 영상 녹화 실행과의 세부 물리 수치는 조금 달라질 수 있습니다.

## 강의별 코드 읽기와 심화 미션

[강의별 코드 해설·공식 시연·관련 연구](code-and-papers.md)에서 함수와 해당 줄을 바로 열 수 있습니다. [여섯 미션의 실측 기록](records/missions)에는 최초 계획, 턴별 상태, 작업 종료 상태와 독립 채점 결과가 있습니다. 두 조건부 확장 과제는 교안에 실험 설계로 수록했습니다.

| 실행 | 지시의 핵심 | 시드·배치 | 예산 | 채점 결과 |
|---|---|---|---:|---|
| budget2 | 전후 촬영 사이에 파란 큐브 운반 | 9201 A | 2 | 실패 · 마지막 사진 누락 |
| budget6 | 같은 지시를 다시 실행 | 9201 A | 6 | 성공 · 사진 2장 |
| leftA | 로봇 기준 왼쪽만 운반, 촬영 금지 | 9201 A | 6 | 성공 · 파랑 |
| leftB | 같은 지시, 좌우 반전 | 9302 B | 6 | 성공 · 빨강 |
| afterB | 안착 뒤에만 촬영 | 9302 B | 6 | 성공 · 운반 후 1장 |
| beforeB | 먼저 촬영한 뒤 운반 | 9302 B | 6 | 성공 · 운반 전 1장 |

시뮬레이터 환경에서 저장소 루트로 이동하고 아래 명령을 실행합니다. 실행마다 새 출력 경로를 지정합니다. 프롬프트에는 각 기록의 outcome.json에 있는 instruction을 입력합니다. B 배치는 --seed 9302 --mirror-layout, 예산 보정 실험은 --turns 2 또는 --turns 6을 사용합니다.

```bash
export WAFFLE_LEARNING_DEPS="$HOME/waffle_mpx/.learning-deps"
python3 lessons/13-react/free_command.py --scene "$HOME/waffle_mpx/simulation/scene.usda" --output /tmp/waffle-new-mission --seed 9201 --turns 6
```

각 조건은 한 번씩 실행했습니다. 배치 일반화나 반복 성공률 추정에는 추가 시드가 필요합니다. 운반의 수평 허용 오차는 16 mm이며 선택한 물체의 상승, 다른 물체 상승 여부, 사진의 시점·개수도 채점합니다.
