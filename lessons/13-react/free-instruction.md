# 자유 지시로 Waffle 작업 구성하기

이 브랜치의 실행기는 한국어 지시 전체와 현재 시뮬레이션 상태를 Qwen2.5 7B에 전달합니다. 모델은 한 번에 다음 행동 하나와 인자를 선택합니다. 바퀴·팔·그리퍼의 물리 실행 뒤 결과를 다시 관측합니다. 작업 도중 사진을 요청하면 같은 장면의 D435 프레임을 저장합니다.

## 실행

기본 13강의 Isaac Sim, Isaac Lab, SmolVLM2와 Waffle 체크포인트 설치를 먼저 마칩니다. 기본 장면 생성 방법은 [13강 설치와 실행](README.md)에 있습니다. scene.usda 생성 후 기존 시뮬레이터를 종료합니다. 이 실습은 별도 장면을 한 번 열고 한 지시가 끝날 때까지 유지합니다.

```bash
cd ~/waffle_mpx/src
git fetch origin
git switch feature/open-instruction-vla
ollama pull qwen2.5:7b
python3 lessons/13-react/free_command.py --show --output ~/waffle_mpx/free-run-01
```

프롬프트에 원하는 결과를 한 문장으로 입력합니다. 예를 들어 “파란 블록을 초록 칸으로 옮겨 놓은 다음, 그 결과를 사진 한 장으로 남겨 줘.”라고 입력할 수 있습니다. 매번 새 출력 폴더를 지정합니다. 기본 계획 예산은 8턴이며 --turns로 1~32 범위에서 바꿀 수 있습니다.

## 모델과 제어 범위

- 계획 모델은 관절값, 차체 자세, 블록 위치와 목표 좌표, 이전 행동의 실행 결과를 읽습니다. 블록 위치는 Isaac 물리 엔진에서 관측합니다. 실물용 카메라 위치 추정기는 이 경로에 연결되어 있지 않습니다.
- 색상 블록 운반은 시작 RGB와 지시, 로봇 상태에서 관절 궤적 92개를 한 번 예측합니다. 일반 팔 행동은 영어 하위 목표, 최신 RGB와 로봇 상태를 입력해 8번 연속 VLA 추론을 수행합니다. 직진·회전, 개별 관절, 그리퍼, 사진 저장은 별도 제어 동작입니다.
- 문장은 자유롭게 입력할 수 있습니다. 수행 가능한 일은 장면, 제어 인터페이스, 학습된 정책에 좌우됩니다. 도구 사용, 미학습 물체 조작, 임의의 목적지 배치는 이 브랜치의 검증 범위 밖입니다.
- 모델이 완료를 선택하면 model_finished, 수행 불가를 선택하면 blocked, 턴을 모두 쓰면 budget_exhausted로 기록됩니다. model_finished는 모델의 종료 판단입니다. 실제 작업 성공은 목표 좌표, 물체 높이, 사진 등 관측으로 별도로 확인합니다.

## 의존성과 호출 횟수 읽기

```bash
cd ~/waffle_mpx/free-run-01
python3 -m json.tool outcome.json
python3 - <<'PY'
import json
for line in open("turns.jsonl"):
    row = json.loads(line)
    step = row["decision"]
    print(row["turn"], step["action"], step["depends_on"], row["evidence"])
PY
```

depends_on은 이번 행동이 필요로 한다고 모델이 **명시한 이전 턴 번호**입니다. 번호는 0부터 시작합니다. 예를 들어 사진 촬영의 depends_on이 [0]이면 해당 턴의 직접 선행 작업은 1개입니다. 빈 목록은 0개이며 모델이 의존성을 누락할 수도 있습니다.

| outcome.json 필드 | 의미 |
|---|---|
| declared_dependency_edges | 오류 없이 처리한 각 턴의 직접 선행 번호를 중복 제거한 뒤 모두 더한 값입니다. 종료 판단이 명시한 의존성도 포함합니다. |
| planner_calls | 지시와 현재 상태를 보고 다음 행동을 선택한 LLM 호출 횟수입니다. |
| vla_inferences | 실행기가 VLA 작업 프로세스에 예측을 요청한 횟수입니다. 한 번에 예측한 궤적의 관절 목표 개수와 구별합니다. |

설치 의존성의 수를 묻는 경우에는 별도로 셉니다. 예를 들어 저장소 루트에서 아래 명령은 학습용 requirements 파일에 직접 명시된 패키지 수를 출력합니다. ROS 패키지와 전이 의존성은 이 값에 포함되지 않습니다.

```bash
grep -Ec '^[[:space:]]*[[:alnum:]]' learning/requirements.txt
```

## 지시문과 물체 배치별 실험

촬영 순서와 상대 위치 지시를 바꾼 8회 시험의 결과, 턴별 로그와 재현 명령은 [Isaac Sim 평가](evaluation/README.md)에서 확인할 수 있습니다.

## 실기체에서 사용할 수 있는 제어 경로

| 진입점 | 팔·그리퍼로 명령이 전달되는 경로 |
|---|---|
| MoveIt과 `mode:=hardware` | MoveIt의 `FollowJointTrajectory` 액션을 팔·그리퍼 제어기가 받아 처리합니다. 하드웨어 플러그인이 OpenCR로 목표 위치를 쓰고 실제 관절 위치와 속도를 읽습니다. |
| `learning/ros_policy.py --policy` | D435 RGB, 관절 상태와 오도메트리를 동기화해 학습 정책을 호출합니다. 기본값에서는 예측을 발행합니다. `--execute`를 지정하고 시간 조건을 만족하면 팔 4축과 그리퍼의 목표를 각 제어기의 `joint_trajectory` 토픽에 발행합니다. 차체 속도 명령도 발행합니다. |
| 이 실습의 `free_command.py` | Isaac Sim 장면에서 Qwen이 다음 행동을 결정합니다. 색상 운반 정책으로 예측한 궤적은 시뮬레이션 관절에 직접 적용합니다. 이 실행기에는 실제 블록·목표 좌표를 얻는 관측기와 각 행동을 ROS 제어기에 전달하는 실행기가 추가로 필요합니다. |

하드웨어 모드의 URDF를 전개하여 MoveIt과 ROS 2 제어기의 관절 목록을 대조했습니다. `joint1`부터 `joint4`까지와 `gripper_left_joint` 모두 위치 명령·피드백 인터페이스가 일치합니다. 팔 관절 명령 단위는 rad, 그리퍼는 m이며 OpenCR 드라이버가 각각 모터 틱으로 변환합니다. 이 확인은 코드 구성에 대한 검증입니다.

[하드웨어 실행 설정](../../turtlebot3_manipulation_bringup/launch/robot.launch.py) · [MoveIt 제어기](../../turtlebot3_manipulation_moveit_config/config/moveit_controllers.yaml) · [OpenCR 변환과 전송](../../turtlebot3_manipulation_hardware/src/opencr.cpp) · [ROS 학습 정책 실행기](../../learning/ros_policy.py)
