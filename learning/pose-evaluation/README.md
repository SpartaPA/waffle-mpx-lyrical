# 팔 시작 자세에 따른 색상 블록 운반

차체를 정지한 상태에서 팔 4축과 그리퍼의 시작 위치, 빨강·파랑 블록의 좌표를 함께 바꿉니다. 목표는 같은 초록 칸입니다. 한 배치에서 빨강과 파랑을 각각 한 번씩 지시합니다. 시연 생성, 기존 정책 평가, 추가 학습 정책 평가 모두 같은 물리 판정을 사용합니다. 요청한 블록을 그리퍼 가까이에서 25 mm 이상 들어야 하고, 다른 블록을 집으면 실패합니다. 블록 전체가 목표 칸 안에 있고 그리퍼를 뗀 상태에서 약 0.5초 이상 안정적으로 놓여야 성공합니다.

| 초기화 항목 | 표본 추출 범위 |
|---|---|
| 관절 1 / 2 | −0.38~0.38 rad / −0.18~0.28 rad |
| 관절 3 / 4 | −0.16~0.20 rad / −0.20~0.24 rad |
| 그리퍼 | 2~12 mm |
| 각 블록의 x | 204~226 mm |
| 두 블록의 y | 10 mm를 중심으로 각각 반대 방향에 28~41 mm 떨어지도록 배치합니다. |

각 시험의 `start_joints`는 초기화 후 물리가 안정됐을 때 읽은 값입니다. 팔 자세와 블록 배치는 별도의 난수열을 사용합니다. 기존 시연은 시드 73, 새 시연은 시드 111, 두 모델 비교는 시드 1927을 사용합니다. 부모 SmolVLM2 정책을 고정하고, 기존·추가 시연과 Hugging Face의 OpenMANIPULATOR-X 시연을 함께 사용해 92단계 관절 궤적을 예측하는 헤드를 다시 학습합니다.

### 새 시연의 시작 자세

아래 값은 각 배치의 빨간 블록 시연에서 안정화 직후 측정한 값입니다. 같은 설정으로 파란 블록 시연도 생성했습니다.

| 배치 | 관절 1 (rad) | 관절 2 (rad) | 관절 3 (rad) | 관절 4 (rad) | 그리퍼 (mm) |
|---|---:|---:|---:|---:|---:|
| 0 | 0.100 | 0.118 | -0.093 | -0.149 | 2.2 |
| 1 | -0.248 | 0.015 | -0.016 | 0.150 | 2.6 |
| 2 | 0.034 | 0.266 | 0.098 | -0.004 | 4.9 |
| 3 | 0.231 | -0.095 | 0.141 | 0.123 | 3.2 |
| 4 | 0.248 | -0.151 | 0.073 | -0.198 | 3.1 |
| 5 | 0.228 | -0.067 | 0.157 | 0.065 | 10.7 |

## 비교 결과

추가 시연 12건 중 물리 판정을 통과한 12건과 기존 시연 16건, Hugging Face 시연 4건으로 학습했습니다. 미학습 시드에서 기존 정책은 **10/10 (100%)**, 추가 학습 정책은 **10/10 (100%)** 성공했습니다. 한 자세·색상 조합을 한 번씩 시험한 결과입니다.

| 배치 | 지시 대상 | 기존 정책 | 추가 학습 | 기존 → 추가 학습 최종 수평 오차 |
|---|---|---|---|---:|
| 0 | red | 성공 | 성공 | 7.6 → 6.9 mm |
| 0 | blue | 성공 | 성공 | 4.2 → 3.6 mm |
| 1 | red | 성공 | 성공 | 1.9 → 2.4 mm |
| 1 | blue | 성공 | 성공 | 8.3 → 8.1 mm |
| 2 | red | 성공 | 성공 | 7.9 → 8.1 mm |
| 2 | blue | 성공 | 성공 | 6.0 → 10.4 mm |
| 3 | red | 성공 | 성공 | 3.0 → 3.2 mm |
| 3 | blue | 성공 | 성공 | 7.0 → 7.4 mm |
| 4 | red | 성공 | 성공 | 16.5 → 11.7 mm |
| 4 | blue | 성공 | 성공 | 2.2 → 2.8 mm |

10회 전체의 최종 수평 오차 중앙값은 기존 정책 6.5 mm, 추가 학습 정책 7.2 mm였습니다.

같은 시드로 생성한 쌍에서 초기 블록 좌표 차이는 1 mm 미만이었고 안정화 후 읽은 팔 4축의 최대 차이는 0.0000 rad였습니다. 이번 비교는 고정 목표에서 색상 운반 정책을 직접 호출했습니다. 13강의 자연어 계획 8개 시험과는 평가 단위가 다릅니다.

[추가 시연](teacher.json) · [기존 정책의 물리 기록](original.json) · [추가 학습 정책의 물리 기록](trained.json) · [학습에 사용한 데이터와 가중치 해시](../checkpoints/waffle-color-pose-111.json)

## 재현하기

[학습 환경 및 Hugging Face 시연 준비](../README.md)에 따라 `hf-examples`를 준비합니다. 아래 명령은 저장소 루트에서 실행합니다. 결과 경로는 새 경로를 지정합니다.

```bash
RUN="$HOME/waffle_mpx/learning_runs"
OUT="$RUN/pose-experiment-01"
SCENE="$HOME/waffle_mpx/simulation/scene.usda"
SIM="$HOME/isaacsim6_venv/bin/python"
LAB="$HOME/IsaacLab/.venv/bin/python"
PARENT="learning/checkpoints/waffle-hf-vla.pt"
export WAFFLE_LEARNING_DEPS="$HOME/waffle_mpx/.learning-deps"
mkdir "$OUT"

"$SIM" sim/evaluate_pick_place.py "$SCENE" - "$OUT/original-demos" \
  --controller teacher --seed 73 --layouts 8 --decisions 92
"$SIM" sim/evaluate_pick_place.py "$SCENE" - "$OUT/new-demos" \
  --controller teacher --varied-poses --seed 111 --layouts 6 --decisions 92
PYTHONPATH="$WAFFLE_LEARNING_DEPS" "$LAB" learning/color_imitation.py \
  "$RUN/hf-examples" "$OUT/original-demos" "$OUT/new.npz" \
  --extra-demos "$OUT/new-demos" --parent-vla "$PARENT"

for policy in original new; do
  ckpt="$OUT/new.npz"
  if [[ "$policy" == original ]]; then ckpt="learning/checkpoints/waffle-color-73.npz"; fi
  "$SIM" sim/evaluate_pick_place.py "$SCENE" "$ckpt" "$OUT/test-$policy" \
    --parent-vla "$PARENT" --controller color --varied-poses --seed 1927 --layouts 5 --decisions 92
done
```

13강 자유 지시에서 새 체크포인트를 선택하려면 아래처럼 실행합니다. 기본 체크포인트는 `waffle-color-73.npz`입니다.

```bash
WAFFLE_COLOR_CHECKPOINT="$PWD/learning/checkpoints/waffle-color-pose-111.npz" \
  python3 lessons/13-react/free_command.py --backend isaac --output "$OUT/free-01"
```
