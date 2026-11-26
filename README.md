# Waffle MPX · ROS 2 Lyrical

TurtleBot3 Waffle Pi에 OpenMANIPULATOR-X, LDS-03(COIN-D4), 전방 RealSense D435를 장착하는 구성입니다. 실물과 Isaac Sim 모두 같은 ros2_control 컨트롤러, 관절 이름, 로봇 모델을 사용합니다. 출력할 카메라 선반과 조립 방법은 [마운트 설계](design/README.md)에 있습니다.

[강화학습·모방학습·Hugging Face VLA 실습](learning/README.md)에는 공개 시연과 웹 이미지로 학습한 모델을 Isaac에서 검증하는 예제가 있습니다. [색상 지시 및 배치별 집기·놓기 시험](learning/README.md#지시한-물체-집어-놓기-평가)은 물체의 물리 상태로 성공률을 계산합니다. [Isaac ROS GPU 실습](isaac_ros/README.md)에는 D435용 cuVSLAM·nvblox·영상 처리와 OpenMANIPULATOR-X용 cuMotion·cuRobo 실행 방법이 있습니다. [색상 시연을 추가한 재학습 예제](learning/color-pick-place.md)는 시연 생성부터 미학습 위치 평가까지 재현합니다.

[13강 · ReAct와 Tool Use](lessons/13-react/)에서는 Qwen으로 한국어 지시를 해석하고, Isaac Sim에서 시각·언어 모델로 촬영 여부를 결정합니다. Waffle VLA로 지정 색상의 블록을 옮기고 휠 피드백으로 차체도 전진시킵니다. 실행 코드, 녹화 영상, 터미널 캡처와 관측 로그를 함께 제공합니다.

이 브랜치에서 자연어 지시를 바로 실행하려면 [자유 지시 VLA 실행법과 호출 횟수 확인](lessons/13-react/free-instruction.md)을 따릅니다.

## 설치와 실습 순서

1. [장치별 설치와 첫 실행](docs/install.md)에서 저장소를 클론하고 ROS 패키지 8개를 빌드합니다. 먼저 mock에서 팔을 움직여 제어 구성을 확인할 수 있습니다.
2. [패키지 목록](docs/packages.md)에서 동봉한 ROS 패키지, 외부 의존성, GPU 선택 패키지 42개와 Python 환경을 확인합니다.
3. [배포 체크포인트로 색상 집기 평가](docs/install.md#6-배포-체크포인트로-색상-집기-평가)를 실행하면 같은 배치에서 빨강·파랑 지시를 번갈아 시험합니다. Isaac Sim 6.1에서 미학습 위치 8회 모두 목표에 놓았고, 실물 조립·파지 성능은 별도 검증 대상입니다.

![와플과 OpenMANIPULATOR-X, 전방 D435 조립 모델](design/assembled-waffle.png)

## 배치와 설치

| 장치 | 환경 | 실행 기능 |
|---|---|---|
| Raspberry Pi | Ubuntu Server **26.04 LTS arm64**, ROS 2 Lyrical | OpenCR, 바퀴·팔·그리퍼 제어, LDS-03, USB 3 D435, 로봇 TF |
| 제어 PC | ROS 2 Lyrical | 키보드 텔레옵, Cartographer, Nav2, MoveIt 2, RViz |
| NVIDIA GPU PC | Isaac Sim **6.1.0**, Python 3.12와 호환되는 Lyrical 환경 | 시뮬레이션과 Isaac ROS 5 영상 처리 |
| Isaac Lab 환경 | Isaac Lab 3.0 | Waffle USD를 articulation으로 불러와 Newton MJWarp로 제어 |

Pi 이미지를 굽고 SSH와 네트워크를 구성한 뒤 Ubuntu 공식 ROS 저장소를 등록합니다. 로봇의 Pi 기종은 지정되지 않아 64비트 Ubuntu Server 26.04가 지원하는 보드를 전제로 했습니다. GPU PC 검증 환경은 Ubuntu 24.04의 NVIDIA Lyrical 배포 패키지입니다. [Lyrical 지원 플랫폼](https://docs.ros.org/en/lyrical/Installation.html) · [Ubuntu용 ROS 패키지 설치](https://docs.ros.org/en/lyrical/Installation/Ubuntu-Install-Debs.html)

Pi와 제어 PC에서 이 저장소를 `~/waffle_mpx/src`에 클론하고 `~/waffle_mpx`에서 빌드합니다. 저장소 루트가 곧 colcon의 `src` 디렉터리이므로, 다른 위치(예: `~/waffle-mpx-lyrical`)에 클론하면 `rosdep install`에서 `given path 'src' does not exist` 오류가 납니다. 이미 다른 곳에 클론했다면 `mv ~/waffle-mpx-lyrical ~/waffle_mpx/src`로 옮긴 뒤 진행하세요.

```bash
sudo apt update
sudo apt install git ros-lyrical-ros-base ros-dev-tools
source /opt/ros/lyrical/setup.bash
mkdir -p ~/waffle_mpx
[ -d ~/waffle_mpx/src/.git ] || git clone https://github.com/SpartaPA/waffle-mpx-lyrical.git ~/waffle_mpx/src
cd ~/waffle_mpx
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then sudo rosdep init; fi
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro lyrical -y
colcon build --symlink-install --parallel-workers 2 --cmake-args -DBUILD_TESTING=OFF
source src/tools/lyrical_env.bash
```

제어 PC에서 RViz와 MoveIt 시각화를 사용합니다. 이 저장소에는 LDS-03 드라이버, DYNAMIXEL SDK ROS 패키지, Isaac 토픽 하드웨어 플러그인이 포함돼 있습니다. GPU용 `isaac_ros_image_proc`는 Isaac ROS 5가 설치된 GPU PC에 필요합니다. 현재 PC에서는 시스템 관리자 권한 없이 설치한 Cartographer 의존성을 `~/waffle_mpx/.cartographer`에 두었습니다. **새 터미널마다** 아래 환경 파일을 읽으면 해당 라이브러리와 워크스페이스를 함께 찾습니다.

```bash
source ~/waffle_mpx/src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=42
```

Pi와 제어 PC는 같은 도메인 번호와 DDS 통신이 가능한 네트워크를 사용합니다. 실물과 시뮬레이션을 동시에 켜면 각각 다른 도메인 번호를 사용합니다. 시뮬레이터·해당 제어 노드는 같은 번호여야 합니다.

## 실물 기동과 펌웨어

OpenCR은 USB 시리얼, LDS-03은 USB2LDS, D435는 Pi의 USB 3 포트에 연결합니다. 시리얼 권한은 `sudo usermod -aG dialout "$USER"` 후 다시 로그인해 적용합니다. 장치 경로는 `ls -l /dev/serial/by-id /dev/serial/by-path`로 확인합니다. D435의 USB 권한과 USB 3 연결은 librealsense 도구 `rs-enumerate-devices`로 확인할 수 있습니다.

OpenCR에는 **ROS 2용 turtlebot3_manipulation.opencr**이 필요합니다. 드라이버는 OpenCR ID 200에서 바퀴와 매니퓰레이터 연결 상태를 확인하고 기존 제어 테이블로 명령합니다. 두 USB 센서는 Pi가 읽으므로 이 구성에는 별도 펌웨어 소스 수정이 필요하지 않습니다. 기본 Waffle 펌웨어가 설치된 보드는 아래 공식 매뉴얼의 ROS 2 절에 따라 manipulation 이미지를 먼저 올립니다. 업데이트 후 팔이 초기 자세로 움직일 수 있습니다. [ROBOTIS 조립 및 OpenCR 업데이트 절차](https://emanual.robotis.com/docs/en/platform/turtlebot3/manipulation/) · [LDS-03 사양](https://emanual.robotis.com/docs/en/platform/turtlebot3/appendix_lds_03/)

```bash
# Pi에서 실행
ros2 launch turtlebot3_manipulation_bringup robot.launch.py mode:=hardware \
  opencr_port:=/dev/ttyACM0 lidar_port:=/dev/ttyUSB0
```

`camera_mount_xyz:="0.1061547 0 0.065"`와 `camera_mount_rpy:="0 0 0"`가 기본값입니다. 실기에서는 RealSense 드라이버가 카메라 내부 보정 TF를 발행합니다. 시뮬레이션은 URDF의 공칭 광학 프레임을 사용합니다.

## 주행과 조작

아래 명령은 각각 별도 터미널에서 실행합니다. 모의 제어만 확인할 때는 먼저 `ros2 launch turtlebot3_manipulation_bringup robot.launch.py mode:=mock`를 사용합니다.

| 목적 | 실행 명령 |
|---|---|
| 키보드 텔레옵 | `ros2 run turtlebot3_manipulation_bringup teleop` |
| MoveIt 경로 계획·실행과 RViz | `ros2 launch turtlebot3_manipulation_moveit_config move_group.launch.py` |
| Cartographer 지도 작성 | `ros2 launch turtlebot3_manipulation_cartographer cartographer.launch.py start_rviz:=true` |
| 지도 저장 | `ros2 run nav2_map_server map_saver_cli -f "$HOME/waffle_map"` |
| 저장된 지도로 Nav2 시작 | `ros2 launch turtlebot3_manipulation_bringup navigation.launch.py map:="$HOME/waffle_map.yaml"` |
| NVIDIA GPU에서 컬러→흑백 변환 | `ros2 launch turtlebot3_manipulation_bringup isaac_ros.launch.py` |

텔레옵은 W/S로 전후진, A/D로 회전합니다. 스페이스로 정지합니다. 1–4로 팔 관절, 5로 그리퍼를 선택한 뒤 +/−로 움직입니다. 바퀴 명령 타임아웃은 0.5초입니다. 팔은 현재 관절 피드백을 기준으로 한 스텝씩 이동합니다. MoveIt RViz에서는 arm 또는 gripper 그룹을 선택하고 **Plan & Execute**를 누릅니다.

매핑 종료 후 Cartographer를 끄고 Nav2를 시작합니다. RViz에 `nav2_bringup/rviz/nav2_default_view.rviz`를 열고 **2D Pose Estimate**로 현재 위치를 지정한 뒤 **Nav2 Goal**을 보냅니다. Nav2 footprint는 팔을 접고 주행하는 조건입니다. 팔을 뻗은 채 이동하려면 그 자세의 점유 영역을 costmap footprint에 반영해야 합니다.

## Isaac Sim 6.1과 Isaac Lab

현재 GPU PC에서 아래 명령으로 실행합니다. Isaac Sim 6.1의 Python 프로세스가 Lyrical `rclpy`로 직접 통신합니다. 별도 배포판의 ROS 브리지를 로드할 필요가 없습니다. 다른 GPU PC에서도 Isaac Sim Python과 ROS Python 확장 모듈의 ABI가 맞아야 합니다. [Isaac Sim 6.1 ROS 환경](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_ros_other_platforms.html)

```bash
cd ~/waffle_mpx
source src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=43
mkdir -p simulation
python3 src/tools/export_urdf.py simulation/waffle.urdf
PYTHONPATH="$PYTHONPATH:/usr/lib/python3/dist-packages" \
  ~/isaacsim6_venv/bin/python src/sim/scene.py simulation/waffle.urdf --output simulation
```

`--headless`는 창 없이 실행합니다. `--steps 300`은 유한 프레임 점검용입니다. 출력 디렉터리의 `waffle.usda`는 Lab용 로봇, `scene.usda`는 바닥·벽·장애물과 카메라가 배치된 장면입니다. ROS 센서 발행과 명령 수신은 `scene.py` 실행 중 동작합니다. D435 모델은 이상적인 핀홀 RGB와 m 단위 32FC1 깊이를 렌더링합니다. 센서 잡음 및 실제 IR 스테레오 복원 오차는 모델링하지 않았습니다. 실물 깊이 영상의 인코딩은 장치 드라이버 설정을 따릅니다.

두 번째 터미널에서 같은 도메인을 선택하고 컨트롤러를 기동합니다.

```bash
source ~/waffle_mpx/src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=43
ros2 launch turtlebot3_manipulation_bringup robot.launch.py mode:=isaac
```

위 기능표의 MoveIt·Cartographer·Nav2·Isaac ROS launch에 `use_sim_time:=true`를 추가합니다. 텔레옵은 `teleop --ros-args -p use_sim_time:=true`를 사용합니다. 이 장면에서 만든 예제 지도는 `~/waffle_mpx/src/maps/isaac_room.yaml`입니다.

Isaac Lab 자체 환경의 터미널에서는 다음과 같이 실행합니다. `lab_robot.py`의 `robot_config()`는 다른 Lab 환경의 scene에도 넣을 수 있습니다.

```bash
cd ~/waffle_mpx
~/IsaacLab/.venv/bin/python src/sim/lab_demo.py simulation/waffle.usda --steps 240
```

## 인터페이스와 검증

| 토픽 또는 액션 | 용도 |
|---|---|
| `/cmd_vel`, `/odom` | TwistStamped 차동구동 명령과 휠 오도메트리 |
| `/joint_states` | 팔·바퀴·그리퍼의 관절 피드백 |
| `/arm_controller/follow_joint_trajectory`, `/gripper_controller/follow_joint_trajectory` | 실제 장치·mock·Isaac 공통 액션 |
| `/scan`, `/map` | base_scan 프레임의 LaserScan과 Cartographer 점유 지도 |
| `/camera/color/image_raw`, `/camera/depth/image_rect_raw` | RGB·깊이 영상, 해당 스트림의 `camera_info` |
| `/camera/color/image_mono` | Isaac ROS GPU 변환 출력 |
| `/imu` | 실물 OpenCR IMU |
| `/clock` | Isaac 시뮬레이션 시간 |

로컬 PC에서 ros2_control 4개 컨트롤러 활성화, 팔·그리퍼 액션 성공, MoveIt OMPL 계획 및 궤적 실행을 확인했습니다. RTX 5060의 Isaac Sim 6.1에서 가상 센서, 오도메트리, Cartographer 지도 저장 및 해당 지도를 사용한 Nav2 목표 도달을 확인했습니다. Isaac Lab 3.0의 Newton MJWarp에서 로봇을 로드하고 240스텝 롤아웃을 실행했습니다. Isaac ROS에서 시뮬레이터의 RGB 영상을 640×480 mono8로 변환해 수신했습니다. 실물 카메라가 BEST_EFFORT로 발행하면 isaac_ros.launch.py에 `input_qos:=SENSOR_DATA`를 지정합니다. 실물 Pi·OpenCR·LDS-03·D435 조합과 출력물의 장착 공차는 실기 검증이 남아 있습니다.

포팅 기준은 [ROBOTIS 조작 패키지 d989240](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation/tree/d9892409da89a44ab1de0945a2ca3ea3fa87385f)와 [OpenMANIPULATOR-X 사양](https://docs.robotis.com/docs/systems/openmanipulator_x/overview/)입니다. 카메라 좌표는 RealSense D435 모델을 반영했습니다. 나머지 동봉 드라이버의 리비전은 [vendor 목록](vendor/revisions.repos)에 있습니다.

[14~18강 통합 교안과 실습](lessons/14-18/README.md)에서 명령 계약, RGB-D Grounding, VLA 어댑터, 근거 검색과 20개 사례 평가를 실행합니다.
