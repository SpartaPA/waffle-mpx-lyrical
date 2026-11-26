# 한국어 지시와 블록 배치에 따른 Isaac Sim 평가

동일한 지시를 서로 다른 두 배치에서 한 번씩 수행합니다. 매 시험마다 Isaac Sim 장면과 대화 이력을 새로 시작합니다. 개선된 실행기에서는 Qwen2.5 7B가 지시문에서 요청한 행동 순서를 생성합니다. 색상별 집기 행동에서는 SmolVLM2 기반 Waffle 정책이 현재 RGB와 로봇 상태에서 팔의 관절 목표를 예측합니다. 실행기는 좌우 지시를 해석할 때 시뮬레이터에서 관측한 두 블록의 좌표와 로봇 자세를 사용합니다. 턴별로 다시 계획할 때는 모델에도 현재 장면 상태를 전달합니다.

[개선 전후 성공률과 재시험 로그](ordered-results/README.md)에서 동일한 8개 조건의 결과를 비교할 수 있습니다. [기존 실행의 실패 분석](results/README.md)에는 개선 전 턴별 기록이 있습니다.

## 재현 방법

[자유 지시 실습의 설치와 실행](../free-instruction.md)에 따라 장면과 체크포인트를 준비하고 Ollama 서버를 실행합니다. 저장소 루트에서 다음 명령을 실행합니다. 출력 경로는 실행할 때마다 새로 지정합니다. 채점용 Python에는 Pillow가 필요합니다.

```bash
export ISAAC_SIM_PYTHON="$HOME/isaacsim6_venv/bin/python"
export WAFFLE_LEARNING_DEPS="$HOME/waffle_mpx/.learning-deps"
export WAFFLE_PLANNER_MODEL=qwen2.5:7b
python3 lessons/13-react/evaluation/run.py "$HOME/waffle_mpx/simulation/scene.usda" "$HOME/waffle_mpx/order-eval-01"
python3 lessons/13-react/evaluation/score.py "$HOME/waffle_mpx/order-eval-01"
```

공개된 기록만 다시 채점할 때는 다음 명령을 사용합니다.

```bash
python3 lessons/13-react/evaluation/score.py lessons/13-react/evaluation/results
python3 lessons/13-react/evaluation/score.py lessons/13-react/evaluation/ordered-results
```

## 판정 방법

- 턴 번호는 0부터 시작하며 최대 6턴입니다. 지시문별 촬영 횟수와 운반 순서를 대조합니다. 같은 동작을 추가로 반복하면 순서 항목에서 실패로 기록합니다.
- 운반 중 두 블록의 높이 변화를 기록합니다. 선택한 블록은 25 mm 이상 올라가야 하고 다른 블록은 25 mm 미만이어야 합니다. ‘왼쪽’은 초기 로봇 자세를 기준으로 각 블록의 좌표를 왼쪽 축에 투영해 판정합니다.
- 운반 뒤 0.5초 동안 물리를 진행합니다. 목표 중심과 수평 거리가 16 mm 이내이고 블록 중심 높이가 51 ± 4 mm여야 합니다. 종료 상태에서도 같은 조건을 확인합니다.
- 촬영 당시의 목표 도달 여부를 지시의 촬영 시점과 비교하고, 실제 사진 파일이 640 × 480으로 디코딩되는지 확인합니다. 모델의 완료 선언과 각 행동의 실행 오류도 확인합니다.
- 배치 A는 시드 9201, 배치 B는 시드 9302에 좌우 반전을 적용합니다. 두 배치 모두 같은 초록 목표 칸을 사용합니다. 각 지시문·배치 조합을 한 번씩 실행하므로 성공률은 이 8회의 관측값입니다.
