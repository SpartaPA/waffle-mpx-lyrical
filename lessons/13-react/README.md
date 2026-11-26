# 13강 · ReAct와 Tool Use

한국어로 촬영·전진·블록 운반을 요청하고, Isaac Sim 6.1에서 실행 결과를 확인합니다. 기본 진입점은 [natural_command.py](natural_command.py)입니다. 실행 코드, 체크포인트, 녹화 영상과 결과는 이 GitHub 저장소에서 받습니다.

[Google Slides에서 영상과 함께 보기](https://docs.google.com/presentation/d/1fiq3HZHeNQnmrItNBD8PSHUfsjZaFz1hVdX47lO6Xyk/edit) · [강의 슬라이드 내려받기](lesson13.pptx) · [모델 명령 입력 화면](media/model-blue-input.png)

## 1. 설치와 준비

새 워크스페이스에서 저장소를 받습니다.

```bash
mkdir -p ~/waffle_mpx
git clone https://github.com/SpartaPA/waffle-mpx-lyrical.git ~/waffle_mpx/src
```

기존 main 복제본에서는 `git -C ~/waffle_mpx/src pull --ff-only`로 업데이트합니다. [ROS 2 Lyrical·Isaac Sim·Isaac Lab 설치](../../docs/install.md)와 [학습 환경 준비](../../learning/README.md)를 완료합니다.

### Ollama 설치와 서버 확인

Isaac Sim을 실행할 Ubuntu PC에서 Ollama를 설치합니다. 이미 설치했다면 서버 확인부터 진행합니다. [Ollama 공식 Linux 설치 안내](https://docs.ollama.com/linux)

```bash
curl -fsSL https://ollama.com/install.sh | sh
curl -fsS http://127.0.0.1:11434/api/tags
```

`models` 목록이 담긴 JSON이 나오면 서버가 준비됐습니다. 목록이 비어 있어도 서버 연결은 정상입니다. 연결이 거부되고 Ollama를 systemd 서비스로 설치했다면 `sudo systemctl start ollama`를 실행합니다. 직접 실행하는 환경에서는 별도 터미널에 `ollama serve`를 실행해 둡니다. [모델 목록 API](https://docs.ollama.com/api/tags)

### 모델 다운로드

Qwen과 고정 리비전의 SmolVLM2 가중치를 받습니다.

```bash
ollama pull qwen2.5:1.5b
ollama list
cd ~/waffle_mpx/src
~/IsaacLab/.venv/bin/python -m pip install -r learning/requirements.txt
~/IsaacLab/.venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('HuggingFaceTB/SmolVLM2-500M-Video-Instruct',revision='4cde9d208e19519c36917aa170fffc7e381aa0ad')"
(cd learning/checkpoints && sha256sum -c SHA256SUMS)
```

### Isaac Sim을 켜기 전에 LLM만 확인하기

다음 명령은 실습 실행기가 사용하는 `interpret()`를 그대로 호출합니다. 시뮬레이터 없이 한국어 해석과 단위 변환을 확인할 수 있습니다.

```bash
cd ~/waffle_mpx/src/lessons/13-react
python3 -c "from natural_command import interpret; print(interpret('20센티미터 이내에 물체가 있으면 사진을 찍어 줘.'))"
```

검증한 출력은 `{'intent': 'photo', 'meters': 0.2}`입니다. `intent`는 실행할 작업이고 `meters`는 미터 단위 거리입니다. 모델은 로컬 Ollama의 `/api/chat`에서 호출하므로 외부 API 키는 필요하지 않습니다. 프롬프트와 응답 형식은 [natural_command.py의 SYSTEM과 interpret 함수](natural_command.py)에 있습니다.

| LLM이 반환한 작업 | 실행기가 받는 값 |
|---|---|
| `photo` | 0m 초과 12m 이하의 촬영 기준 거리 |
| `drive` | 0m 초과 0.15m 이하의 전진 거리 |
| `approach` | 정면(±10°) 라이다 거리가 이 값 이하가 될 때까지 전진합니다. 0.2m 이상 1.5m 이하이며, 최대 이동은 1m입니다. |
| `pick_red`, `pick_blue` | 선택한 블록 색상. 거리는 사용하지 않습니다. |
| `unsupported` | 요청을 한 가지 지원 작업으로 다시 입력합니다. |

1.5B 모델은 거리가 들어간 문장을 `photo`로 잘못 고르기도 합니다. 그래서 실행기는 LLM 결과를 원문 단어와 대조합니다. `photo`는 문장에 사진·촬영·찍기가 있어야 하고, `approach`는 "~까지"와 이동 표현이 함께 있어야 합니다. `pick_*`는 문장에 나온 색 하나로 정합니다. 조건이 맞지 않으면 `approach` 또는 `unsupported`로 바꿉니다.

### 모델과 아키텍처

| 단계 | 모델 또는 제어기 | 입력 → 출력 |
|---|---|---|
| 모든 한국어 지시 | Ollama Qwen2.5 1.5B, JSON 스키마, temperature 0 | 한국어 문장 → 작업 종류와 미터 단위 거리. 허용 범위를 실행기에서 검사합니다. |
| 촬영 행동 선택 | [SmolVLM2-500M-Video-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct/tree/4cde9d208e19519c36917aa170fffc7e381aa0ad)의 언어 출력층을 이산 행동 선택에 사용하는 [시각·언어 정책](photo_policy.py) | D435 RGB, 지시 거리, 라이다 최솟값, 거리 조건 충족 여부 → Yes/No 로짓 → 저장/생략. 범위 초과 시 저장을 차단합니다. 이 촬영 정책은 별도의 행동 시연 학습을 하지 않았습니다. |
| 팔과 그리퍼 제어 | [Waffle 색상 VLA](../../learning/color_imitation.py). 고정 SmolVLM2, HF 시연으로 학습한 행동 헤드의 128차원 은닉 특징, 색상 궤적 회귀층 | 시작 RGB, LLM이 선택한 색상 지시, 로봇 상태 7개 → 영상의 색상 중심·크기와 결합 → 92시점의 관절 4개와 그리퍼 목표. 4Hz로 실행하고 물체의 실제 물리 상태로 채점합니다. |
| 차체 전진 | [휠 피드백 제어기](drive_feedback.py) | LLM이 지정한 거리(최대 0.15m) → 두 바퀴 속도 명령 → 양쪽 바퀴의 회전 환산 거리가 목표에 도달하면 정지합니다. |
| 거리까지 접근 | [라이다 피드백 제어기](drive_feedback.py) | 목표 거리 → 0.033m/s 전진 → 정면 ±10° 최근접 거리가 목표 이하이면 정지합니다. 5초 동안 거리가 줄지 않거나 1m를 이동하면 멈추고 오류를 냅니다. |

팔 VLA의 가중치는 [waffle-hf-vla.pt](../../learning/checkpoints/waffle-hf-vla.pt)와 [waffle-color-73.npz](../../learning/checkpoints/waffle-color-73.npz)입니다. 이 정책은 시작 영상에서 궤적을 한 번 계획합니다. 기준 좌표나 교사 역기구학은 평가 시 행동 생성에 사용하지 않습니다. 학습 방법과 별도 보류 배치 평가는 [색상 집기 안내](../../learning/color-pick-place.md)에 있습니다.

## 2. 장면 준비 · 터미널 A

```bash
cd ~/waffle_mpx
source src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=113 ROS_LOCALHOST_ONLY=1
mkdir -p simulation
python3 src/tools/export_urdf.py simulation/waffle.urdf
export PYTHONPATH="$PYTHONPATH:/usr/lib/python3/dist-packages"
~/isaacsim6_venv/bin/python src/sim/scene.py simulation/waffle.urdf --output simulation
```

촬영·전진 중에는 이 장면을 켜 둡니다. 이 과정에서 생성된 simulation/scene.usda를 팔 실습에도 사용합니다. 팔 실습에서는 터미널 A를 Ctrl+C로 종료해 GPU 메모리를 확보합니다. 팔 실행기가 작업대와 블록을 포함한 별도의 물리 장면을 엽니다.

## 3. 자연어 입력 · 터미널 B

```bash
source ~/waffle_mpx/src/tools/lyrical_env.bash
export ROS_DOMAIN_ID=113 ROS_LOCALHOST_ONLY=1
cd ~/waffle_mpx/src/lessons/13-react
python3 natural_command.py --output ~/waffle_mpx/lesson13-photo
```

`자연어 명령 >` 프롬프트에 한 문장을 입력합니다. 각 실행마다 새 결과 폴더 이름을 지정합니다. 다음 표에서 원하는 사례를 선택하세요.

| 입력할 문장 | 관찰할 결과 |
|---|---|
| 1.5미터 안에 물체가 있으면 사진을 찍어 줘. | request.json의 LLM 해석, outcome.json의 두 로짓·선택 행동, 저장되면 photo.png를 확인합니다. |
| 20센티미터 이내에 물체가 있으면 사진을 찍어 줘. | meters가 0.2로 해석되는지, 거리 조건이 촬영을 허용하는지 확인합니다. |
| 앞 물체와 1미터가 될 때까지 다가가 줘. | 정면 거리가 1m 이하가 되면 멈춥니다. outcome.json에서 시작·종료 정면 거리와 바퀴 이동 거리를 확인합니다. |
| 차체를 앞으로 10센티미터 전진해 줘. | 장면에서 차체가 움직입니다. 양쪽 휠의 회전각을 반지름 0.033m로 환산한 거리를 출력합니다. 이 값은 차체 중심의 월드 좌표 변위와 다를 수 있습니다. |
| 빨간 블록을 집어서 초록색 사각형 위에 놓아 줘. | 아래 명령으로 창을 열고, 팔이 접근·파지·운반·해제하는 과정을 관찰합니다. |
| 파란 블록을 집어서 초록색 사각형 위에 놓아 줘. | 같은 초기 배치에서 선택 블록, 상승 높이와 목표 안착 판정을 빨강 케이스와 비교합니다. |

```bash
python3 natural_command.py --output ~/waffle_mpx/lesson13-red --show
python3 natural_command.py --output ~/waffle_mpx/lesson13-blue --show
```

창 없이 실행하려면 --show를 생략합니다. 작업 종류와 거리는 request.json에서, 실제 결과는 outcome.json에서 확인합니다. 집기·놓기에는 physics 아래에 step별 프레임과 trace.jsonl도 남습니다. success 판정에는 목표 내 안정적으로 안착하고 다른 색 물체를 들지 않은 조건이 포함됩니다. 임계값을 넘겼거나 센서가 준비되지 않은 경우에는 촬영 성공으로 처리하지 않습니다.

### 실제 로봇에서 실행하기

Pi에서 `robot.launch.py`(기본 `mode:=hardware`)를 실행하고, 제어 PC에서 같은 ROS_DOMAIN_ID로 `--hardware`를 붙입니다. 전진·접근 명령은 `/isaac/wheel_commands` 대신 `/cmd_vel`로 보내고, 바퀴 각도는 `/joint_states`에서 읽습니다. 촬영은 같은 `/camera/color/image_raw`와 `/scan`을 사용합니다. 블록 집기는 Isaac Sim 전용입니다.

```bash
python3 natural_command.py --hardware --output ~/waffle_mpx/real-$(date +%H%M%S)
```

`앞에 있는 텀블러와의 거리가 20cm가 될 때까지 가까이 가 줘.`는 `approach` 0.2m로 실행됩니다. 거리는 라이다(base_scan) 기준이고, 카메라 마운트 앞면은 라이다보다 약 15cm 앞에 있습니다.

## 4. 실측 결과와 영상

[SeongminJaden YouTube 채널](https://www.youtube.com/@SeongminJaden)에 일부 공개로 게시한 영상입니다. 아래 링크로 바로 재생하거나 Google Slides 발표 화면에서 시청합니다.

| 슬라이드 | YouTube 영상 |
|---|---|
| 15 | [Waffle VLA로 빨간 블록 집어 놓기](https://youtu.be/_jZU7IrpjoM) |
| 16 | [한국어 지시로 파란 블록 집어 놓기](https://youtu.be/bRJ0UW_Or1g) |
| 18 | [거리 조건에 따라 D435 사진 저장하기](https://youtu.be/Of1D111E5QE) |
| 19 | [거리 조건을 바꿔 촬영 생략하기](https://youtu.be/d3v4smfxUc0) |
| 20 | [호출 예산과 센서 오류 비교하기](https://youtu.be/nafUpiIKDk8) |

[모델 실행 결과](model-results.json)에는 한국어 원문, Qwen 해석과 각 실행의 물리 판정이 있습니다. [빨간 블록 집기·놓기](media/red-arm.mp4)는 4Hz로 기록한 실제 D435 관측 프레임을 제어 주기에 맞춰 재생합니다. [파란 블록 명령 입력과 실행](media/model-blue.mp4)은 터미널과 시뮬레이션 영상을 함께 보여줍니다.

### 비교 실험 · 호출 예산과 도구 오류

기존 규칙 기반 실행기는 오류 처리 비교용으로 제공합니다. 예전 녹화에서 natural_command.py라는 이름으로 실행한 규칙 기반 입력기는 현재 [baseline_command.py](baseline_command.py)입니다. 터미널 A의 기본 장면을 다시 실행한 뒤 다음 명령을 사용합니다.

```bash
python3 baseline_command.py --image near.ppm
python3 waffle_react.py --budget 1
python3 waffle_react.py --first-tool locate_cup
ROS_DOMAIN_ID=112 python3 waffle_react.py --timeout 2
```

[촬영](media/near.mp4) · [생략](media/far.mp4) · [오류 처리](media/errors.mp4) · [입력 캡처](media/near-input.png) · [기준 로그](measured.jsonl). 시간 초과 실험은 도메인 112에 /scan 발행자가 없는 환경에서 실행합니다.

## 실행이 멈췄을 때 확인할 항목

| 증상 | 확인 방법 |
|---|---|
| Ollama 연결 거부 또는 모델을 찾을 수 없음 | 위의 /api/tags 명령으로 서버를 확인합니다. ollama list에 qwen2.5:1.5b가 없으면 ollama pull qwen2.5:1.5b를 실행합니다. |
| 해석한 작업 또는 거리가 예상과 다름 | 결과 폴더의 request.json에서 원문과 plan을 비교합니다. 위의 LLM 단독 점검으로 거리·단위 또는 블록 색상을 명시한 한 문장을 다시 시험합니다. |
| 촬영 중 카메라·라이다 시간 초과 | 오류 메시지에 두 토픽의 수신 개수가 나옵니다. 0인 토픽을 `ros2 topic info -v`로 확인합니다. 두 터미널의 ROS_DOMAIN_ID가 같아야 합니다. 실물에서 `/camera/color/image_raw`만 0이면 Wi-Fi로 640×480 원본 영상이 전달되지 않은 것입니다. 제어 PC와 Pi를 유선으로 연결하거나 실행기를 Pi에서 실행합니다. 대기 시간은 `--sensor-timeout`으로 늘릴 수 있습니다. |
| FileExistsError | 실행기는 기존 결과를 보존합니다. --output에 새 폴더 이름을 지정합니다. |
| 팔 실습에서 장면을 찾을 수 없음 | 터미널 A에서 scene.usda 생성까지 완료합니다. 다른 위치에 생성했다면 --scene에 해당 파일 경로를 지정합니다. |
| 팔 실습 중 하위 프로세스 오류 | 결과 폴더의 isaac.log 마지막 부분을 확인합니다. 시뮬레이터와 학습용 Python을 다른 위치에 설치했다면 ISAAC_SIM_PYTHON과 ISAAC_LAB_PYTHON에 각 실행 파일의 절대 경로를 지정합니다. |
