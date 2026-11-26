# Waffle 학습 실습

이 예제는 Hugging Face 데이터 다운로드부터 RGB 영상과 언어 명령으로 학습한 정책이 Isaac Sim의 관절을 움직이는 데까지 재현합니다. 실행 결과는 기본적으로 `~/waffle_mpx/learning_runs`에 둡니다.

[팔 시작 자세를 바꾼 시연으로 추가 학습하기](pose-evaluation/README.md)에서 관절·그리퍼의 초기 자세와 물체 배치를 바꿔 두 정책을 비교합니다.

## Hugging Face 데이터로 VLA 학습 후 Isaac에서 검증

이 PC의 Isaac Lab 환경에는 CUDA PyTorch가 설치돼 있습니다. 추가 패키지는 워크스페이스의 `.learning-deps`에 놓았습니다. 새 환경에서는 Isaac Lab 3 환경의 Python으로 [requirements.txt](requirements.txt)를 설치합니다. 시뮬레이터용 Python과 학습용 Python은 각각 `ISAAC_SIM_PYTHON`, `ISAAC_LAB_PYTHON`으로 지정할 수 있습니다.

```bash
cd ~/waffle_mpx/src
export PYTHONPATH="$HOME/waffle_mpx/.learning-deps:${PYTHONPATH:-}"
LAB="$HOME/IsaacLab/.venv/bin/python"
RUN="$HOME/waffle_mpx/learning_runs"
"$LAB" learning/hf_examples.py "$RUN/hf-examples" --episodes 0 1 2 3 --stride 6 --captions 16
"$LAB" learning/policy.py "$RUN/hf-examples" "$RUN/waffle-hf-vla.pt" \
  --kind vla --web "$RUN/hf-examples/web" --epochs 50
learning/verify_hf_sim.sh "$RUN/waffle-hf-vla.pt" "$RUN/my-hf-simulation"
```

이미 학습한 이 PC에서는 마지막 명령만 실행해도 됩니다. 결과 디렉터리는 매번 새 이름을 씁니다. 검증 스크립트는 빈 로컬 ROS 도메인에 Isaac Sim과 컨트롤러를 기동하고, 실시간 `pick_and_place` 지시와 D435 RGB를 입력합니다. `trace.jsonl`에 관측, 예측, 실제로 보낸 명령과 추론 시간을 남기고 종료합니다. 다시 판독할 때는 `python3 learning/check_trace.py 결과경로/trace.jsonl`을 사용합니다.

### 학습 데이터와 용도

| 입력 | 고정한 소스 | 학습에서 맡는 역할 |
|---|---|---|
| OpenMANIPULATOR-X 영상·5축 위치·목표·언어 지시 | [1114개 시연 중 4개](https://huggingface.co/datasets/Hadolking/openmanipulator-pickplace-dataset-1114ep/tree/f840ca6171f19987d6e4248ecbb1219231a4287a) | 30 Hz 원본에서 6프레임마다 한 장을 읽고, 0.2초 뒤의 관절 목표를 지도 신호로 사용합니다. 기록에 없는 차체 전진·회전 명령은 0으로 둡니다. |
| 웹 이미지와 자연어 캡션 | [Flickr8k 학습 분할](https://huggingface.co/datasets/jxie/flickr8k/tree/56f58c967835f7c508d684f36bd7897cca9d7634) | 실제 이미지–캡션 쌍과 다른 사진의 캡션을 짝지은 불일치 예시를 만듭니다. 두 조합을 구별하는 보조 손실로 행동 예측과 같은 은닉층을 학습합니다. |
| 사전학습 시각·언어 인코더 | [SmolVLM2-500M](https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct/tree/4cde9d208e19519c36917aa170fffc7e381aa0ad) | 인코더는 고정하고 영상·텍스트 특징과 로봇 상태를 결합합니다. 학습 헤드는 행동 축별 257개 구간을 예측합니다. 가운데 구간이 정확한 정지 명령입니다. |

가져오기 도구는 영상 프레임과 Parquet의 에피소드 ID·프레임 인덱스·시각·관절 순서·유한값을 확인합니다. 관절 1–4는 rad, 그리퍼는 m로 해석했으며 실제 기록 범위와 URDF 한계를 대조합니다. 리비전·원본 파일 SHA-256·제한값을 넘긴 행동 수는 에피소드별 `episode.json`에 남깁니다. 학습/평가는 에피소드 단위로 분리하며, 4개일 때 3개로 학습하고 나머지 1개로 평가합니다. 외부 영상의 카메라 배치와 Waffle 전방 D435 배치는 다를 수 있습니다.

RT-2에서 참고한 부분은 웹의 이미지·언어 지식과 로봇 시연을 함께 사용하고 행동을 이산 토큰으로 예측하는 방식입니다. 이 구현은 공개 SmolVLM 백본과 Waffle 전용 행동 헤드를 사용합니다. RT-2 원 논문 모델의 가중치나 원래의 웹 규모 학습 성능은 검증 대상에 포함되지 않습니다. 보조 손실의 효과를 비교하려면 같은 시드·에피소드에서 `--web`을 생략한 두 번째 체크포인트를 학습합니다. [RT-2 연구](https://robotics-transformer2.github.io/)

같은 보류 에피소드, 시드 42, 학습 50회에서 실행한 대조 실험 결과는 다음과 같습니다. 값은 정규화된 평균 절대 오차이며 낮을수록 기록된 행동에 가깝습니다. 두 모델 모두 같은 웹 사전학습 인코더를 사용합니다.

| 추가 학습 데이터 | 관절 1 | 관절 2 | 관절 3 | 관절 4 | 그리퍼 |
|---|---:|---:|---:|---:|---:|
| 로봇 시연 | 0.018 | 0.110 | 0.117 | 0.111 | 0.524 |
| 로봇 시연 + 웹 이미지·캡션 16쌍 | 0.018 | 0.158 | 0.120 | 0.113 | 0.554 |

이 표본에서는 웹 보조학습으로 보류 행동 오차가 줄지 않았습니다. 양쪽 모두 한 가지 작업 지시로 평가했으므로 새로운 언어 지시를 따르는 능력은 별도 평가가 필요합니다.

### 확인한 결과

- HF에서 받은 4개 영상의 총 1,044프레임을 표 자료와 대조했고, 176개 관측–행동 샘플을 작성했습니다. 웹 이미지·캡션 16쌍을 보조 학습에 사용했습니다.
- 보류한 시연의 행동 오차는 절대오차 평균으로 평가합니다. 이 실행의 정규화 오차는 전진·회전 0, 관절 1–4 각각 0.018, 0.158, 0.120, 0.113, 그리퍼 0.554였습니다. 그리퍼 일반화에는 추가 시연이 필요합니다.
- Isaac Sim에서 32개 동기화 프레임 중 31개 명령을 적용했습니다. 관절 1–4의 측정 이동 범위는 0.088, 0.810, 0.499, 0.146 rad였고 그리퍼는 0.0151 m였습니다. 차체 명령은 정지였습니다. 방향을 판정할 만큼 큰 1축 명령 4회 중 3회에서 다음 프레임의 회전 방향이 일치했습니다.
- 이 검사는 다운로드·공동 학습·온라인 추론·관절 피드백을 다룹니다. 물체 파지·운반은 아래의 독립적인 물리 시험으로 평가합니다. 실물 성능은 별도 검증이 필요합니다.

## 직접 시연을 모아 모방학습

Isaac Sim과 `mode:=isaac` 제어기를 실행한 뒤 아래 명령으로 한 에피소드를 기록합니다. 다른 터미널에서 기존 키보드 텔레옵으로 조작하고 기록기는 Ctrl+C로 종료합니다. 다음 시연은 다른 디렉터리 이름으로 기록합니다. 실물은 `mode:=hardware`와 시스템 시계를 사용합니다.

```bash
cd ~/waffle_mpx/src
source tools/lyrical_env.bash
export ROS_DOMAIN_ID=43
python3 learning/ros_policy.py --record ~/waffle_mpx/learning_runs/my-demos/ep01 \
  --instruction '앞으로 이동한 후 그리퍼를 열어' --ros-args -p use_sim_time:=true
# 서로 독립적인 에피소드를 2개 이상 기록한 후
export PYTHONPATH="$HOME/waffle_mpx/.learning-deps:$PYTHONPATH:/usr/lib/python3/dist-packages"
~/IsaacLab/.venv/bin/python learning/policy.py ~/waffle_mpx/learning_runs/my-demos \
  ~/waffle_mpx/learning_runs/my-bc.pt --kind bc
~/IsaacLab/.venv/bin/python learning/ros_policy.py --policy ~/waffle_mpx/learning_runs/my-bc.pt \
  --instruction '앞으로 이동한 후 그리퍼를 열어' --ros-args -p use_sim_time:=true
```

BC는 상태 기반 연속 행동 복제입니다. 이미지·지시까지 조건으로 삼으려면 `--kind vla`를 사용합니다. 데이터에는 RGB·관절 상태·오도메트리를 최대 0.10초 차이로 대응시킨 관측과 해당 시점의 텔레옵 명령이 들어갑니다. 이 기록기는 단일 지점 텔레옵을 대상으로 합니다. MoveIt 다중 지점 궤적을 그대로 교사 명령으로 저장하는 용도에는 별도의 궤적 샘플링이 필요합니다. 행동 순서는 전진 m/s, 회전 rad/s, 관절 1–4의 절대 rad, 왼쪽 그리퍼의 절대 m입니다.

온라인 추론은 기본적으로 `/learning/predicted_action`만 발행합니다. `--execute` 실행 시 명령 범위와 관절 스텝을 제한하고, 오래된 관측이나 0.45초 이상 걸린 추론은 적용하지 않습니다. 직접 관절 위치 명령은 MoveIt 충돌 계획을 경유하지 않습니다. 위 Isaac 전용 검증 스크립트로 먼저 동작을 비교할 수 있습니다.

[명령과 측정값을 겹쳐 본 그래프](hf-sim-motion.png)는 위 실험의 실제 추적 로그에서 생성했습니다. 새 실행은 `python3 learning/plot_trace.py 결과경로/trace.jsonl 결과경로/motion.png`로 비교할 수 있습니다.

[색상 시연을 추가한 재학습 및 미학습 좌표 평가](color-pick-place.md)에서 기존 HF 정책을 바탕으로 새 궤적 예측층을 학습할 수 있습니다.

## 지시한 물체 집어 놓기 평가

고정한 HF 정책에 전방 D435 RGB, 관절 상태, 차체 속도와 영어 지시를 입력합니다. 시드에 따라 빨간색과 파란색 블록의 시작 좌표를 바꿉니다. 같은 배치를 두 번 초기화하고 각각 빨간 블록과 파란 블록을 지시합니다. 초록색 목표 위치는 일정합니다. 정확한 지시문은 `Pick up the red cube and place it on the green square.`와 여기서 red를 blue로 바꾼 문장입니다.

```bash
cd ~/waffle_mpx/src
RUN="$HOME/waffle_mpx/learning_runs"
HF_HUB_OFFLINE=1 ~/isaacsim6_venv/bin/python sim/evaluate_pick_place.py \
  ../simulation/scene.usda "$RUN/waffle-hf-vla.pt" "$RUN/pick-place-$(date +%Y%m%d-%H%M%S)" \
  --layouts 4 --decisions 48 --seed 41
```

첫 실행에는 위의 HF 학습 예제에서 만든 체크포인트와 캐시된 SmolVLM 백본이 필요합니다. 장면이 없으면 [워크스페이스 시뮬레이션 안내](../README.md)에 따라 `sim/scene.py`에 `--headless --steps 5`를 추가해 한 번 생성합니다. 평가기는 장면을 메모리에 열고 시험 물체를 추가합니다. 학습 환경이 다른 경로이면 `ISAAC_LAB_PYTHON`을 지정합니다. `--layouts` 하나당 색상별 2회 시험이 진행됩니다.

- 40 mm 높이의 작업대에 한 변 20 mm, 질량 8 g의 자유 강체 블록 두 개를 놓습니다. 52 mm 정사각형 목표의 중심은 월드 기준 (254, 8) mm입니다. 각 시행 전 물체가 지정 좌표에 정착했는지, RGB에 두 색상과 목표가 모두 보이는지 확인합니다.
- 4 Hz에서 48번 정책을 호출하고 0.5초 더 관찰합니다. 시뮬레이션은 추론 중 멈추므로 매번 같은 물리 시간 예산으로 평가합니다. 모델은 RGB와 로봇 상태만 받으며 정답 물체 좌표와 목표 좌표는 채점에만 사용합니다. 그리퍼로의 강제 부착이나 궤적 보정은 없습니다.
- 집기는 블록 중심이 시작점보다 25 mm 이상 올라가고 양손가락 끝의 중점에서 24 mm 이내에 들어온 경우로 판정합니다. 놓기는 블록 바닥 전체가 목표 영역 안에 있고, 지지면 높이 오차 3 mm 미만, 선속도 12 mm/s 미만, 각속도 0.2 rad/s 미만, 손끝 중점과 블록 간격 35 mm 초과가 끝까지 0.5초 연속 유지돼야 합니다. 다른 색 블록을 들어 올린 시행도 실패입니다.
- `results.json`에는 체크포인트 SHA-256, 시드, 전체·시행별 결과가 있습니다. 각 시행 폴더는 초기·최종 RGB, 실제 물체 위치, 손끝 중점, 정책 명령과 적용 목표의 시계열을 포함합니다. 새 결과 디렉터리를 사용해 기존 로그를 보존합니다. `python3 learning/summarize_pick_place.py 결과디렉터리`로 배치별 성공, 들어 올린 높이, 제어 시점에서 측정한 손끝과 블록의 최소 거리를 확인합니다.

### 시드 41 실측 결과

**집기 0/8, 지시한 목표에 놓기 0/8**이었습니다. 빨간 블록과 파란 블록 각각 4회 모두 작업대에 남았습니다. 384개 추론 전체에서 그리퍼 목표는 개방 방향의 15.0–18.0 mm였습니다. 각 시행에서 4 Hz로 기록한 손끝 중점과 지정 블록 중심의 최소 거리는 41.9–88.0 mm였습니다. 학습 시연 4개의 작업 지시문은 모두 `pick_and_place`였으며, 이번 평가의 색상별 지시는 학습 시연에 없었습니다. [배치별 좌표와 측정 결과](pick-place-seed41.json)

## 강화학습

Isaac Lab Newton MJWarp의 Waffle 물리 모델에서 Stable-Baselines3 PPO를 사용합니다. 기본 `shoulder` 작업은 관절 1의 무작위 목표에 도달해 **0.07 rad 이내로 다섯 제어 주기** 유지하면 성공입니다. 한 제어 주기는 0.05초입니다. `posture` 작업은 팔 4축과 그리퍼의 동시 자세 추종이며, 목표에 대한 잔차를 학습합니다. 두 작업의 체크포인트는 각각 다른 파일을 사용합니다.

```bash
cd ~/waffle_mpx/src
export PYTHONPATH="$HOME/waffle_mpx/.learning-deps:${PYTHONPATH:-}"
LAB="$HOME/IsaacLab/.venv/bin/python"
USD="$HOME/waffle_mpx/simulation/waffle.usda"
POLICY="$HOME/waffle_mpx/learning_runs/ppo-shoulder"
"$LAB" sim/lab_ppo.py "$USD" "$POLICY" --task shoulder --timesteps 12288
"$LAB" sim/lab_ppo.py "$USD" "$POLICY" --task shoulder --eval-episodes 12 --seed 321
```

1축 정책은 학습 후 별도 시드의 목표 **12/12**에 성공했습니다. 5축 자세 정책은 16,384스텝 후 같은 방식으로 **0/12**였습니다. 5축의 보상·구동기 튜닝과 작업별 학습이 남아 있습니다. `--resume`은 저장 모델에서 학습을 계속합니다.
