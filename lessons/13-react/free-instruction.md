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

- 계획 모델은 관절값, 차체 자세, 블록 위치와 목표 좌표, 이전 행동의 실행 결과를 읽습니다. 기본 Isaac 백엔드는 물리 엔진에서 블록 위치를 읽습니다. 하드웨어 백엔드는 D435의 정렬된 RGB-D와 TF에서 현재 보이는 색상 영역의 표면 위치를 추정합니다.
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
| `free_command.py --backend hardware` | Qwen이 실제 RGB-D로 추정한 장면 상태와 이전 실행 결과에서 다음 행동을 선택합니다. 색상 운반에는 SmolVLM2 기반 정책을 호출하고 궤적을 팔·그리퍼의 `joint_trajectory` 토픽으로 전달합니다. 차체 명령은 `/cmd_vel`, 이동 피드백은 `/odom`을 사용합니다. |

하드웨어 모드의 URDF를 전개하여 MoveIt과 ROS 2 제어기의 관절 목록을 대조했습니다. `joint1`부터 `joint4`까지와 `gripper_left_joint` 모두 위치 명령·피드백 인터페이스가 일치합니다. 팔 관절 명령 단위는 rad, 그리퍼는 m이며 OpenCR 드라이버가 각각 모터 틱으로 변환합니다. 이 확인은 코드 구성에 대한 검증입니다.

[하드웨어 실행 설정](../../turtlebot3_manipulation_bringup/launch/robot.launch.py) · [MoveIt 제어기](../../turtlebot3_manipulation_moveit_config/config/moveit_controllers.yaml) · [OpenCR 변환과 전송](../../turtlebot3_manipulation_hardware/src/opencr.cpp) · [ROS 학습 정책 실행기](../../learning/ros_policy.py)

### Pi와 GPU 제어 PC에서 실행하기

두 기기에서 [실물 설치](../../docs/install.md)에 따라 워크스페이스를 빌드하고 같은 ROS 도메인과 LAN을 사용합니다. 두 기기의 시스템 시각도 동기화합니다. Pi에는 OpenCR, D435와 LDS-03을 연결하고 제어 PC에서 Qwen과 VLA를 실행합니다. 다음은 도메인 42를 사용하는 예입니다.

```bash
# Pi
source ~/waffle_mpx/src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=42 ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
ros2 launch turtlebot3_manipulation_bringup robot.launch.py mode:=hardware \
  opencr_port:=/dev/ttyACM0 lidar_port:=/dev/ttyUSB0
```

```bash
# GPU 제어 PC
cd ~/waffle_mpx/src
git switch feature/open-instruction-vla
source tools/lyrical_env.bash
export ROS_DOMAIN_ID=42 ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
sudo apt install ros-lyrical-cv-bridge ros-lyrical-message-filters ros-lyrical-tf2-ros \
  python3-opencv python3-scipy python3-pil
export ISAAC_LAB_PYTHON="$HOME/IsaacLab/.venv/bin/python"
export WAFFLE_LEARNING_DEPS="$HOME/waffle_mpx/.learning-deps"
ollama pull qwen2.5:7b
ros2 control list_controllers
python3 lessons/13-react/free_command.py --backend hardware \
  --turns 6 --output ~/waffle_mpx/hardware-run-01
```

팔·그리퍼와 차체 제어기가 `active`인지 확인합니다. 새 출력 디렉터리를 지정하고 터미널에 지시를 입력합니다. 예를 들어 “작업대 사진을 한 장 찍고 종료해”를 입력하면 촬영 턴의 PNG와 `turns.jsonl`을 확인할 수 있습니다. 하드웨어 백엔드에서는 모델이 고른 이동·조작이 즉시 제어기로 전달됩니다. 차체의 직진·회전은 로컬 오도메트리 제어이므로 장애물이 없는 공간에서 실행합니다.

### D435 작업대와 관측값

- 컬러 영상, 컬러에 정렬된 깊이, 컬러 카메라 내부 파라미터, 관절 상태와 오도메트리가 필요합니다. RGB와 깊이는 640 × 480이고 광학 프레임이 일치해야 합니다. 카메라 장착 위치와 방향은 실제 조립값으로 설정합니다.
- 빨간색·파란색 블록과 초록 칸을 각각 한 개씩 사용합니다. 화면에서 같은 색 영역이 여러 개이거나 유효 깊이 픽셀이 부족하면 해당 물체의 좌표를 사용할 수 없습니다. 특히 근거리에서는 RGB에 보이는 블록에서도 유효 깊이가 나오지 않을 수 있습니다. 촬영 로그의 `before.cubes_xyz`, `before.goal_xyz`에서 인식 결과를 확인합니다.
- 색상 운반 정책은 20 mm 큐브와 고정 목표로 학습했습니다. `base_footprint`에서 목표 표면을 (0.254, 0.008, 0.041) m 부근에 놓고, 블록은 x 약 0.215 m, y 약 −0.022 또는 +0.043 m의 학습 배치 부근에 놓습니다. 정책은 시작 RGB에서 92개 관절 목표를 예측합니다. 초록 칸 중심의 수평 편차가 16 mm를 넘거나 높이 편차가 10 mm를 넘으면 해당 운반을 거부합니다.
- 운반 후에는 다시 촬영한 색 영역의 표면 좌표를 비교합니다. 수평 거리 16 mm 이내, 목표보다 2~26 mm 높은 경우 위치 검사를 통과합니다. 이 값은 영상에서 보이는 표면에 대한 추정치입니다. 파지력이나 실제로 들어 올린 높이를 측정하지 않습니다. `model_finished`는 모델이 내린 종료 판단입니다.

### 장치 없이 확인한 항목

ROS 2 Lyrical의 `mode:=mock` 제어기와 고정 RGB-D 입력을 같은 PC의 독립 도메인에서 사용했습니다. 팔 1번 관절 목표 0.18 rad에 대해 0.175 rad, 그리퍼 목표 0.008 m에 대해 0.0071 m의 피드백을 읽었습니다. 직진과 회전은 오도메트리 변화를 확인했고, 한국어 촬영 지시는 Qwen이 사진 한 장을 저장한 뒤 종료했습니다. 색상 운반에서는 배포 체크포인트의 92개 관절 목표를 전달했습니다. 고정 영상에 남아 있는 블록과 목표의 수평 오차 46.6 mm를 감지해 배치 실패로 판정했습니다. 실기체의 파지·배치 성공률은 아직 측정하지 않았습니다.

색 영역의 좌표 변환, 깊이 누락·중복 색상 처리, 고정 물체의 배치 실패 판정은 제어 PC에서 다음 명령으로 다시 검사할 수 있습니다.

```bash
source ~/waffle_mpx/src/tools/lyrical_env.bash
cd ~/waffle_mpx/src
python3 lessons/13-react/evaluation/test_hardware_command.py
```
