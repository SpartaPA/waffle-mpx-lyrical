# 14~18강 용어와 작동 원리

각 항목에서 용어의 뜻과 계산 또는 판단 방법을 확인한 뒤, 같은 제목의 슬라이드에서 실습 예를 확인합니다.

## 용어 찾아보기

[계획과 인식](#waffle_terms_18_3) · [관계와 디코더](#waffle_terms_16_6) · [관절 궤적](#waffle_terms_14_2) · [관측](#waffle_terms_0_1) · [관측의 나이](#waffle_terms_14_3) · [광축 깊이](#waffle_terms_15_3) · [교란과 통제](#waffle_terms_18_5) · [그라운딩](#waffle_terms_15_1) · [그래프와 의존성](#waffle_terms_18_1) · [근거 포함률](#waffle_terms_17_4) · [기록과 피드백](#waffle_terms_16_4) · [기준선과 검증 경로](#waffle_terms_18_2) · [내적](#waffle_terms_15_6) · [노드와 토픽](#waffle_terms_14_1) · [단위와 유한값](#waffle_terms_14_3) · [닫힌 루프](#waffle_terms_16_7) · [대응점](#waffle_terms_15_5) · [도구와 모델](#waffle_terms_17_3) · [도구와 종료](#waffle_terms_18_3) · [롤아웃](#waffle_terms_16_7) · [마스크와 문턱값](#waffle_terms_15_2) · [모달리티](#waffle_terms_15_1) · [모델 호출과 추론](#waffle_terms_18_6) · [모델과 방법](#waffle_terms_17_5) · [모방학습](#waffle_terms_16_1) · [모의 장치](#waffle_terms_14_5) · [목표와 핸들](#waffle_terms_14_4) · [물리와 렌더링](#waffle_terms_0_3) · [미세조정](#waffle_terms_16_5) · [밀집 검색](#waffle_terms_17_2) · [반환 상태](#waffle_terms_17_3) · [배열과 NPZ](#waffle_terms_0_5) · [벡터와 노름](#waffle_terms_15_6) · [벤치마크](#waffle_terms_18_2) · [분기와 예외](#waffle_terms_0_6) · [비동기와 퓨처](#waffle_terms_14_4) · [상태](#waffle_terms_0_1) · [서비스](#waffle_terms_14_1) · [성공률과 %p](#waffle_terms_18_4) · [스키마와 버전](#waffle_terms_14_3) · [슬롯과 어텐션](#waffle_terms_16_6) · [시드와 재생](#waffle_terms_0_5) · [시차와 깊이](#waffle_terms_15_5) · [실행 환경](#waffle_terms_0_4) · [안착과 오차](#waffle_terms_18_4) · [액션](#waffle_terms_14_1) · [어댑터](#waffle_terms_16_4) · [역정규화](#waffle_terms_16_3) · [역투영](#waffle_terms_15_3) · [열린 루프](#waffle_terms_16_7) · [오류 주입](#waffle_terms_18_2) · [외부 보정](#waffle_terms_15_4) · [위상 정렬](#waffle_terms_18_1) · [은닉 표현](#waffle_terms_16_2) · [인용과 근거](#waffle_terms_17_3) · [인코더](#waffle_terms_16_2) · [일반화](#waffle_terms_18_5) · [임베딩](#waffle_terms_15_1) · [자료와 계약](#waffle_terms_18_3) · [자유도와 관절각](#waffle_terms_14_2) · [저랭크](#waffle_terms_16_5) · [저장소와 브랜치](#waffle_terms_0_4) · [정규화](#waffle_terms_16_3) · [정책](#waffle_terms_16_1) · [제어기](#waffle_terms_14_5) · [조건부 정확도](#waffle_terms_17_4) · [종단 간 정확도](#waffle_terms_17_4) · [종료 상태](#waffle_terms_14_4) · [종료와 채점](#waffle_terms_18_6) · [좌우 카메라](#waffle_terms_15_5) · [좌표계](#waffle_terms_14_2) · [중앙값과 표면](#waffle_terms_15_4) · [중앙값의 효과](#waffle_terms_15_6) · [질의와 문서 조각](#waffle_terms_17_1) · [짝지은 비교](#waffle_terms_18_5) · [차체와 팔](#waffle_terms_0_3) · [체크포인트](#waffle_terms_0_4) · [초점거리와 주점](#waffle_terms_15_3) · [카메라](#waffle_terms_0_3) · [코사인 유사도](#waffle_terms_15_2) · [키와 인덱스](#waffle_terms_0_6) · [턴과 예산](#waffle_terms_18_6) · [토큰](#waffle_terms_16_6) · [파지와 오파지](#waffle_terms_18_4) · [평가 도구](#waffle_terms_17_5) · [포화와 속도 제한](#waffle_terms_16_4) · [프롬프트와 문맥](#waffle_terms_17_1) · [피드백 오차](#waffle_terms_14_5) · [픽셀과 채널](#waffle_terms_15_2) · [필터와 top-k](#waffle_terms_17_2) · [하위 작업](#waffle_terms_18_1) · [학회와 프리프린트](#waffle_terms_17_5) · [함수와 인자](#waffle_terms_0_6) · [행동](#waffle_terms_0_1) · [행동 공간](#waffle_terms_16_3) · [행동 헤드](#waffle_terms_16_2) · [행렬과 점](#waffle_terms_15_4) · [회귀와 가중치](#waffle_terms_16_1) · [희소 검색](#waffle_terms_17_2) · [JSON과 JSONL](#waffle_terms_0_5) · [LLM](#waffle_terms_0_2) · [LoRA](#waffle_terms_16_5) · [RAG](#waffle_terms_17_1) · [VLA](#waffle_terms_0_2) · [VLM](#waffle_terms_0_2)

## 공통 준비

<a id="waffle_terms_0_1"></a>
### 로봇이 보고 판단하고 움직인다는 뜻

[통합 교안 2쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_0_1)

- **관측** 관측(observation)은 한 시점에 센서로 얻은 값입니다. 카메라는 밝기와 색을, 관절 센서는 각도를 측정합니다.
- **상태** 상태(state)는 로봇과 환경의 상황을 수치로 나타냅니다. 같은 카메라 영상이라도 팔의 시작각이 다르면 필요한 움직임이 달라집니다.
- **행동** 행동(action)은 제어기에 보낼 명령입니다. 집게를 닫으라는 명령을 보낸 뒤 새 관측으로 물체가 따라 올라왔는지 확인합니다.

확인 문제 · 집게 목표값과 블록 높이 중 어느 쪽이 실제로 들렸다는 증거일까요? 높이 변화를 이전 관측과 비교합니다.

<a id="waffle_terms_0_2"></a>
### LLM, VLM, VLA의 입출력

[통합 교안 3쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_0_2)

- **LLM** 대규모 언어 모델(Large Language Model)은 앞선 토큰을 바탕으로 다음 토큰을 예측합니다. Qwen은 지시를 읽어 촬영과 운반의 순서를 생성합니다.
- **VLM** 시각·언어 모델(Vision-Language Model)은 이미지와 글을 함께 처리합니다. ‘파란 큐브’라는 글과 카메라 영상의 특징을 함께 표현할 수 있습니다.
- **VLA** 시각·언어·행동 모델(Vision-Language-Action model)은 관측과 지시로 행동을 예측합니다. 이 실습의 Waffle 정책은 팔과 집게가 갈 목표값을 출력합니다.

입출력을 적어 봅니다 · Qwen의 출력은 작업 순서이고 Waffle 색상 정책의 출력은 시점별 숫자 배열입니다.

<a id="waffle_terms_0_3"></a>
### 실제 로봇의 어느 부분을 모사할까요?

[통합 교안 4쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_0_3)

- **차체와 팔** Waffle은 이동 차체, OpenMANIPULATOR-X는 관절식 로봇팔입니다. 그리퍼(gripper)는 팔 끝에서 손가락 사이의 간격을 바꿔 물체를 잡습니다.
- **카메라** D435는 색과 깊이를 관측하는 카메라입니다. 교안의 Isaac 화면은 시뮬레이션에 배치한 카메라의 시점에서 렌더링한 영상입니다.
- **물리와 렌더링** 물리 엔진은 힘·접촉으로 다음 위치와 속도를 계산합니다. 렌더러는 그 장면을 카메라의 픽셀로 바꿉니다. Isaac Sim은 두 과정을 함께 실행합니다.

실습 기록에서 장면 이미지(start.png), 관절 명령(trace.jsonl), 물리 판정(result.json)을 각각 찾습니다.

<a id="waffle_terms_0_4"></a>
### 코드와 데이터를 같은 상태로 준비합니다

[통합 교안 5쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_0_4)

- **저장소와 브랜치** Git은 변경 이력을 관리하고 GitHub는 저장소를 공유합니다. 브랜치는 변경의 흐름이고 커밋은 특정 시점의 내용입니다. git switch로 사용할 흐름을 선택합니다.
- **실행 환경** Python은 코드 실행기입니다. NumPy는 수치 배열 계산을, Pillow는 이미지 읽기를 담당합니다. 가상환경은 실습이 쓸 패키지와 버전을 따로 둡니다.
- **체크포인트** 체크포인트는 학습된 모델 값을 저장한 파일입니다. 해시(hash)는 파일 내용에서 계산한 식별값입니다. 재실행 전 파일의 해시를 대조해 같은 가중치를 사용합니다.

터미널에서 cd는 작업 폴더를 바꾸고 python3 lab.py 15는 그 폴더의 파일을 실행해 15강 경로를 선택합니다.

<a id="waffle_terms_0_5"></a>
### 파일 이름과 확장자로 기록을 읽습니다

[통합 교안 6쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_0_5)

- **JSON과 JSONL** JSON은 키와 값을 묶은 구조화 문서입니다. JSONL은 한 줄마다 독립 JSON이 있어서 행동이 생길 때마다 한 행씩 추가할 수 있습니다.
- **배열과 NPZ** 배열은 숫자를 축과 순서에 맞춰 담습니다. NPZ는 이름이 붙은 여러 NumPy 배열을 한 파일에 담습니다. rgbd.npz에는 깊이, 내부 보정값, 좌표 변환이 들어 있습니다.
- **시드와 재생** 시드(seed)는 난수 생성기의 시작값입니다. 기록 재생(replay)은 저장된 입력을 다시 읽습니다. 물리 재실행은 장면을 열어 접촉과 움직임을 다시 계산합니다.

cases.json은 시험 입력, manual.json은 규칙 원문, trace.jsonl은 시간순 행동 기록입니다.

<a id="waffle_terms_0_6"></a>
### 터미널과 코드 조각에서 반복되는 표기

[통합 교안 7쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_0_6)

- **함수와 인자** 함수는 이름으로 호출하는 계산 절차입니다. 괄호 안의 인자는 함수에 전달할 값입니다. ground(color, folder)에는 찾을 색과 파일이 있는 폴더가 들어갑니다.
- **키와 인덱스** goal["unit"]은 사전에서 이름이 unit인 값을 찾습니다. trajectory[step]은 배열의 특정 시점을 읽습니다. Python의 첫 번째 원소 번호는 0입니다.
- **분기와 예외** if는 조건이 참일 때 실행하고 continue는 다음 반복으로 넘어갑니다. raise Reject(...)는 이유를 담아 현재 처리를 멈춥니다. except는 그 예외를 받아 결과에 기록합니다.

len은 개수를, str은 문자열 표현을 구합니다. --color와 --version은 터미널에서 이번 실행에 전달하는 옵션입니다.

**코드와 원문**

- [README.md](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/lessons/14-18/README.md)

## 14강

<a id="waffle_terms_14_1"></a>
### ROS 2에서 프로그램이 대화하는 세 방식

[통합 교안 11쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_14_1)

- **노드와 토픽** ROS 2는 로봇 프로그램 간 통신을 지원합니다. 노드(node)는 통신의 주체입니다. 토픽(topic)에서는 발행자가 값을 보내면 구독자들이 연속으로 받습니다.
- **서비스** 서비스(service)는 한 요청에 한 응답을 돌려줍니다. 현재 설정처럼 짧은 질문에 적합합니다. 요청 형식이 같아야 양쪽이 값을 해석할 수 있습니다.
- **액션** 액션(action)은 오래 걸리는 작업에 목표·중간 피드백·최종 결과를 제공합니다. 클라이언트가 목표를 보내고 서버가 실행하며 취소 요청도 받을 수 있습니다.

예측해 봅니다 · 3초 동안 팔을 움직이며 중간 각도를 확인하려면 Action, 전체 관절각을 계속 보고 싶으면 joint_states 토픽을 사용합니다.

<a id="waffle_terms_14_2"></a>
### 월드 좌표와 관절각은 어떻게 다를까요?

[통합 교안 12쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_14_2)

- **좌표계** 좌표계(frame)는 위치를 재는 원점과 축의 방향을 정합니다. world는 장면에 고정된 기준입니다. 로봇이 돌아도 같은 물체의 world 좌표는 그대로일 수 있습니다.
- **자유도와 관절각** 자유도(DOF)는 독립적으로 움직일 수 있는 축입니다. 네 팔 관절은 각각 회전합니다. 라디안(rad)은 회전각 단위이며 π rad가 180°입니다.
- **관절 궤적** 궤적(trajectory)은 시간에 따른 목표들의 순서입니다. FollowJointTrajectory는 이름이 지정된 관절들이 주어진 시점까지 갈 목표를 전달하는 액션입니다.

14강 contract는 월드 좌표 요청을 검사합니다. 별도 action_client 실습은 시작 관절각에서 목표각을 직접 정해 모의 제어기에 보냅니다.

<a id="waffle_terms_14_3"></a>
### 명령 계약은 수치에 의미를 붙입니다

[통합 교안 13쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_14_3)

- **스키마와 버전** 스키마(schema)는 데이터의 필드·순서·형식에 관한 약속입니다. version이 command.v1이면 해당 형식을 사용합니다. request_id는 요청 하나를 식별합니다.
- **단위와 유한값** unit은 수치의 단위입니다. 1 m는 1,000 mm입니다. NaN은 수치가 정의되지 않았음을 뜻하며 무한대와 함께 좌표로 사용할 수 없어 검사를 거부합니다.
- **관측의 나이** age_s는 관측부터 사용 시점까지 경과한 초입니다. 오래된 위치에는 물체가 이미 없을 수 있으므로 이 예제는 0~0.4초만 허용합니다.

경계 실험 · 좌표와 단위를 그대로 두고 age_s를 0.400에서 0.401로 바꾸면 contract.stale이 발생합니다.

<a id="waffle_terms_14_4"></a>
### 수락, 피드백, 취소, 종료의 시간차

[통합 교안 14쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_14_4)

- **목표와 핸들** Goal은 서버가 실행할 목표입니다. 수락하면 그 목표를 가리키는 handle을 받습니다. 여러 목표가 오가도 이 핸들로 원하는 요청의 결과를 조회합니다.
- **비동기와 퓨처** 비동기(async) 호출은 응답 도착 전에 제어를 돌려줍니다. Future는 나중에 채워질 결과를 담습니다. 콜백(callback)은 피드백이 도착할 때 실행되는 함수입니다.
- **종료 상태** status는 목표의 생애주기, error_code는 제어기의 결과 코드입니다. cancel은 취소 요청입니다. 취소 수락, CANCELED 도달, 실제 속도 0의 시점은 각각 측정합니다.

wait()의 timeout은 기다릴 시간을 넘겼다는 뜻입니다. 결과가 미확정이면 같은 목표를 곧바로 중복 전송할 근거가 없습니다.

<a id="waffle_terms_14_5"></a>
### 모의 제어기로 무엇을 확인할 수 있을까요?

[통합 교안 15쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_14_5)

- **제어기** 제어기(controller)는 목표를 받아 구동기에 줄 명령을 만듭니다. 관절 궤적 제어기는 시간에 맞춰 어느 관절이 어느 각도로 가야 하는지 계산합니다.
- **모의 장치** 모의(mock) 하드웨어는 센서와 구동기의 인터페이스를 소프트웨어로 대신합니다. 서버 수락·취소·피드백 처리 절차를 실제 모터 연결 전에 확인할 수 있습니다.
- **피드백 오차** 목표값에서 관측값을 빼면 추종 오차가 나옵니다. 관절 이름 순서가 어긋나면 다른 관절끼리 빼게 되므로 joint1~4의 이름과 배열 순서를 먼저 맞춥니다.

Action의 Feedback과 제어 루프의 피드백은 맥락이 다릅니다. 전자는 서버가 알리는 진행 메시지이며 후자는 관측을 다음 제어에 사용하는 원리입니다.

**코드와 원문**

- [ROS 2 Action 설계](https://design.ros2.org/articles/actions.html)
- [action_client.py](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/lessons/14-18/action_client.py)

## 15강

<a id="waffle_terms_15_1"></a>
### 영상과 언어를 숫자로 비교하는 원리

[통합 교안 24쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_15_1)

- **모달리티** 모달리티(modality)는 정보의 형태입니다. 사진과 문장은 같은 물체를 다른 방식으로 표현합니다. 멀티모달 모델은 여러 형태의 정보를 함께 처리합니다.
- **임베딩** 임베딩(embedding)은 대상을 숫자 벡터로 나타낸 것입니다. 공통 공간에서는 서로 다른 입력의 벡터를 같은 기준으로 비교합니다. 일반적인 VLM은 이 표현을 학습합니다.
- **그라운딩** 그라운딩(grounding)은 ‘파란 블록’이라는 말이 현재 장면의 어느 대상이나 위치를 가리키는지 정하는 과정입니다. 같은 색의 블록이 둘이면 색만으로 대상을 정하기 어렵습니다.

수업의 색상 기준선에서는 파랑을 [0, 0, 1]로 직접 지정합니다. 이 기준선과 학습된 시각·언어 표현의 차이를 설명합니다.

<a id="waffle_terms_15_2"></a>
### 픽셀에서 파란색 마스크를 만드는 계산

[통합 교안 25쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_15_2)

- **픽셀과 채널** 픽셀(pixel, px)은 영상 격자의 한 칸입니다. RGB 영상은 그 칸마다 빨강·초록·파랑 채널 값을 갖습니다. 같은 색도 밝기에 따라 세 수의 크기가 달라집니다.
- **코사인 유사도** 두 벡터의 내적을 각 벡터 길이의 곱으로 나눕니다. 방향이 같으면 1입니다. 파랑 축과 [0, 0, 100]의 유사도는 1이고 [100, 0, 0]의 유사도는 0입니다.
- **마스크와 문턱값** 마스크(mask)는 픽셀마다 포함 여부를 표시합니다. threshold는 포함을 가르는 기준값입니다. 코드에서는 코사인 값과 채널 밝기 조건을 모두 통과해야 합니다.

왜 밝기도 볼까요? [0, 0, 1]도 방향은 파랑이지만 매우 어둡습니다. 파랑 채널이 45를 넘어야 이 픽셀이 남습니다.

<a id="waffle_terms_15_3"></a>
### 깊이와 카메라 보정값이 필요한 이유

[통합 교안 26쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_15_3)

- **광축 깊이** RGB-D에서 D는 깊이입니다. 여기서 Z는 카메라 정면 축을 따라 잰 거리(m)입니다. 영상 가장자리에서는 광축 깊이와 카메라에서 점까지의 직선거리가 다릅니다.
- **초점거리와 주점** 내부 파라미터 fx, fy는 픽셀 단위 초점거리이고 cx, cy는 광축이 영상면을 지나는 위치입니다. 주점에서 멀어진 픽셀 수가 시선의 방향을 결정합니다.
- **역투영** 역투영은 픽셀 (u,v)와 깊이 Z로 광학 좌표의 3차원 점을 구합니다. X=(u−cx)Z/fx입니다. 같은 픽셀 방향의 실제 옆 거리는 Z에 비례합니다.

수치 확인 · 주점에서 오른쪽으로 60 px, fx=600 px, Z=0.5 m라면 X=0.05 m입니다. 한 픽셀만으로는 Z를 정할 수 없습니다.

<a id="waffle_terms_15_4"></a>
### 카메라의 점을 로봇이 쓰는 점으로 옮깁니다

[통합 교안 27쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_15_4)

- **외부 보정** 외부 파라미터는 두 좌표계 사이의 회전 R과 위치 이동 t입니다. optical_to_world는 광학 좌표의 점을 월드 좌표로 표현하는 변환입니다.
- **행렬과 점** 행렬은 숫자를 행과 열에 배치한 변환입니다. [X,Y,Z,1]처럼 끝에 1을 붙이면 회전과 평행이동을 한 번의 행렬 곱으로 적용할 수 있습니다.
- **중앙값과 표면** 중앙값은 값을 정렬했을 때 가운데 값입니다. ground()는 축마다 중앙값을 구해 일부 튀는 깊이의 영향을 줄입니다. 결과는 카메라가 본 표면을 대표합니다.

평행이동 예 · 카메라 축이 월드와 평행하고 원점만 X 방향 0.20 m 떨어져 있으면 카메라 X=0.05 m인 점은 월드 X=0.25 m입니다.

<a id="waffle_terms_15_5"></a>
### 스테레오 영상에서 깊이가 나오는 이유

[통합 교안 28쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_15_5)

- **좌우 카메라** 스테레오는 떨어진 두 시점에서 같은 장면을 봅니다. 두 카메라 중심 사이의 거리를 베이스라인 B라고 합니다. 로봇 성능을 비교할 때의 기준선과 문맥이 다릅니다.
- **시차와 깊이** 정렬한 좌우 영상에서 같은 점의 가로 위치 차이가 시차 d입니다. 이상적인 경우 Z=fB/d입니다. 같은 장치에서 가까운 물체는 시차가 더 큽니다.
- **대응점** 대응점은 두 영상에서 같은 물리적 표면을 가리키는 점입니다. 무늬가 없거나 반사되는 표면은 대응 찾기가 어렵습니다. FoundationStereo는 이 대응을 학습합니다.

공식 영상을 보기 전에 예측합니다 · 멀리 있는 물체의 시차가 작은 경우, 1픽셀의 시차 오차가 깊이에 더 큰 영향을 줄 수 있습니다.

<a id="waffle_terms_15_6"></a>
### 평균, 중앙값, 노름을 어떻게 읽을까요?

[통합 교안 29쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_15_6)

- **벡터와 노름** 벡터는 순서가 있는 숫자 묶음입니다. 유클리드 노름은 각 성분의 제곱을 더해 제곱근을 취한 길이입니다. [3,4]의 길이는 5입니다.
- **내적** 내적은 대응하는 성분끼리 곱해 더한 값입니다. [1,2,3]과 파랑 축 [0,0,1]의 내적은 3입니다. 두 벡터의 길이로 나누면 코사인 유사도가 됩니다.
- **중앙값의 효과** [0.49,0.50,2.00] m의 평균은 약 1.00 m, 중앙값은 0.50 m입니다. 중앙값은 소수의 깊이 이상값에 덜 민감하지만 대부분이 잘못되면 역시 실패합니다.

카메라 보정은 센서 기하를 추정하는 작업입니다. 18강의 실행 예산 보정은 허용 턴 수를 바꾸는 작업입니다. 무엇을 바꿨는지 단위와 함께 적습니다.

**코드와 원문**

- [FoundationStereo 공식 프로젝트](https://nvlabs.github.io/FoundationStereo/)
- [lab.py](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/lessons/14-18/lab.py#L34-L50)

## 16강

<a id="waffle_terms_16_1"></a>
### 시연으로 정책을 학습한다는 뜻

[통합 교안 38쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_1)

- **정책** 정책(policy)은 관측과 지시에서 행동을 고르는 규칙 또는 모델입니다. Waffle에서는 시작 영상, 지시, 로봇 상태를 받아 목표 관절들의 시간 순서를 냅니다.
- **모방학습** 모방학습은 시연자가 어떤 상황에서 어떤 행동을 했는지 배웁니다. 행동 복제는 같은 관측에서 시연 행동에 가까운 출력을 내도록 모델의 값을 조정합니다.
- **회귀와 가중치** 회귀는 목표각처럼 연속된 수치를 예측하는 방법입니다. 가중치(weight)는 특징이 출력에 미치는 정도를 정합니다. 학습은 시연과 예측의 오차를 줄이도록 이 값을 조정합니다.

학습과 추론을 구분합니다 · 궤적 헤드의 가중치를 맞추는 과정은 학습, 저장한 가중치로 새 배치의 궤적을 구하는 과정은 추론입니다.

<a id="waffle_terms_16_2"></a>
### 인코더, 은닉값, 헤드를 차례로 읽습니다

[통합 교안 39쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_2)

- **인코더** 인코더(encoder)는 이미지와 문장을 계산 가능한 특징으로 바꿉니다. 부모 모델은 SmolVLM2 계열의 시각·언어 표현과 정규화한 로봇 상태를 함께 사용합니다.
- **은닉 표현** 은닉값(hidden representation)은 모델 내부 층의 출력입니다. 부모 행동 헤드의 마지막 층 앞 값을 꺼내 벡터 길이로 나누면 특징의 방향을 유지하며 크기를 맞출 수 있습니다.
- **행동 헤드** 헤드(head)는 특징을 과제의 출력으로 바꾸는 부분입니다. ColorPolicy는 색상 기하 특징과 부모 VLA 특징을 모아 각 시점·행동 축의 수치를 계산합니다.

np.einsum의 i,itj→tj에서 공통 첨자 i를 따라 곱해 더합니다. 남는 t는 시점, j는 행동 축이므로 결과는 92행 7열입니다.

<a id="waffle_terms_16_3"></a>
### 단위가 다른 행동을 한 배열에 담습니다

[통합 교안 40쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_3)

- **행동 공간** 행동 공간은 허용하는 명령의 종류와 범위입니다. 배열 순서는 차체 선속도(m/s), 회전속도(rad/s), 팔 절대각 4개(rad), 그리퍼 위치(m)입니다.
- **정규화** 정규화는 서로 다른 단위와 범위를 공통 척도로 바꿉니다. 최솟값 L과 최댓값 H를 [−1,1]에 대응시키면 실제 중간값은 0으로 표현됩니다.
- **역정규화** 역정규화는 모델 수치를 물리 단위로 되돌립니다. actions.py는 L+(a+1)(H−L)/2를 사용합니다. 평균·표준편차 방식에는 다른 역변환식이 필요합니다.

계산 · 그리퍼 범위가 −0.010~0.019 m일 때 정규화 출력 0은 (−0.010+0.019)/2=0.0045 m입니다.

<a id="waffle_terms_16_4"></a>
### 행동 후보가 한 번에 관절로 가지 않는 이유

[통합 교안 41쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_4)

- **어댑터** 어댑터(adapter)는 모델 출력을 제어기 입력 형식에 맞춥니다. adapt()는 축 순서, 일곱 값의 유한성, 범위, 차체 정지 조건을 검사합니다.
- **포화와 속도 제한** clip은 값을 범위 안에 묶습니다. 실행기는 전체 범위를 제한하고 현재 위치와 목표의 차이도 제한합니다. 0.35 rad/s 제한이면 0.25초당 최대 0.0875 rad 움직입니다.
- **기록과 피드백** action은 예측 후보, applied는 실행기가 적용한 목표입니다. 관절의 실제 위치나 블록 위치는 물리 피드백입니다. 목표를 보냈다는 사실만으로 도달 여부를 정할 수 없습니다.

4 Hz는 1초에 네 번이라는 뜻입니다. 실행 간격은 1/4초입니다. 시뮬레이션 시간과 영상을 재생하는 실제 시간도 구분합니다.

<a id="waffle_terms_16_5"></a>
### LoRA가 학습할 값의 수를 줄이는 원리

[통합 교안 42쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_5)

- **미세조정** 미세조정(fine-tuning)은 기존 모델을 새 과제 데이터에 맞추는 학습입니다. 동결(freeze)은 선택한 가중치를 학습 중 그대로 두는 것입니다.
- **저랭크** 랭크(rank)는 행렬이 표현하는 독립적인 방향 수입니다. 큰 변화 행렬을 폭 r인 두 작은 행렬의 곱 BA로 나타내면 변화의 랭크는 최대 r입니다.
- **LoRA** Low-Rank Adaptation은 기존 W를 동결하고 작은 A, B를 학습합니다. 512×512 층에서 r=8이라면 A와 B는 합쳐 8,192개 값을 가집니다.

이 계산은 적응 기법 비교용입니다. 수업의 Waffle 색상 체크포인트는 LoRA 대신 부모 특징 위에 궤적 회귀 헤드를 맞췄습니다.

<a id="waffle_terms_16_6"></a>
### 슬롯과 관계 토큰으로 논문 그림을 읽습니다

[통합 교안 43쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_6)

- **토큰** 토큰(token)은 모델이 한 단위로 처리하는 입력 조각입니다. 언어에서는 단어나 단어의 일부, 영상에서는 영역에서 추출한 특징을 토큰으로 표현할 수 있습니다.
- **슬롯과 어텐션** 슬롯(slot)은 영상 속 대상을 요약하는 표현입니다. 어텐션(attention)은 관련 있는 입력 특징에 더 큰 가중치를 주어 어떤 정보를 모을지 결정합니다.
- **관계와 디코더** 관계 토큰은 집게와 블록처럼 대상 간 상호작용을 담습니다. 디코더(decoder)는 이런 표현을 받아 행동 등 필요한 출력을 계산합니다.

SlotVLA 그림에서 그릇 자체를 나타내는 경로와 집게가 그릇에 접근하는 관계를 나타내는 경로를 각각 찾습니다.

<a id="waffle_terms_16_7"></a>
### 시간에 따라 로봇을 제어하는 두 방식

[통합 교안 44쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_16_7)

- **열린 루프** 열린 루프(open loop)는 시작 때 정한 행동을 이후 관측에 따라 다시 계획하지 않고 진행합니다. 색상 운반 정책이 첫 영상에서 92개 목표를 정하는 층이 이 방식입니다.
- **닫힌 루프** 닫힌 루프(closed loop)는 현재 관측을 다음 명령에 반영합니다. 이 실행기는 매 시점 관절 위치 q를 다시 읽고 q에서 허용한 이동량만큼 다음 목표를 적용합니다.
- **롤아웃** 롤아웃(rollout)은 초기 상태에서 정책을 실제로 전개해 얻는 관측·행동의 연속 기록입니다. 에피소드(episode)는 시작부터 종료까지 이어진 한 번의 시험입니다.

같은 시스템 안에서도 상위 궤적 예측과 하위 관절 적용은 서로 다른 주기로 피드백을 사용할 수 있습니다.

**코드와 원문**

- [LoRA 원 논문](https://arxiv.org/abs/2106.09685)
- [SlotVLA 공식 프로젝트](https://slot-vla.github.io/)
- [color_imitation.py](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/learning/color_imitation.py#L28-L58)

## 17강

<a id="waffle_terms_17_1"></a>
### RAG에서 검색과 생성이 맡는 일

[통합 교안 55쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_17_1)

- **RAG** Retrieval-Augmented Generation은 외부 문서에서 질문에 맞는 근거를 찾아 모델 입력에 붙인 뒤 답을 생성하는 방식입니다. 규칙 문서를 바꾸면 검색되는 내용도 바뀝니다.
- **질의와 문서 조각** 질의(query)는 찾으려는 질문입니다. 청크(chunk)는 독립적으로 검색할 문서 조각입니다. 각 조각의 ID, 버전, 원문을 보관해야 근거를 되짚을 수 있습니다.
- **프롬프트와 문맥** 프롬프트는 모델에 전달하는 지시와 입력입니다. 문맥(context)에 검색 원문을 넣고 ID와 인용문을 요청합니다. 이 예제의 생성 모델은 Qwen2.5 7B입니다.

7B는 약 70억 규모의 모델 파라미터를 가리킵니다. 검색된 문서 수나 답을 생성한 횟수를 뜻하는 표기는 아닙니다.

<a id="waffle_terms_17_2"></a>
### 질문에 가까운 근거를 고르는 원리

[통합 교안 56쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_17_2)

- **희소 검색** 희소 검색은 단어 일치 같은 제한된 특징을 사용합니다. retrieve()에서는 질문과 각 문서의 검색어 집합이 공유하는 서로 다른 단어 수가 점수입니다.
- **밀집 검색** 밀집 검색은 문장이나 문서를 학습한 숫자 벡터로 나타내고 가까운 것을 찾습니다. 동의어를 연결할 수 있지만 비슷한 구버전 문서가 섞일 수도 있습니다.
- **필터와 top-k** 필터는 버전 같은 조건으로 후보를 거릅니다. top-k는 점수가 높은 k개를 뜻합니다. 실습 기본값 k=2이며 일치 단어가 없는 조각은 후보로 넣지 않습니다.

질문 단어가 {블록, 운반, 조건}이고 문서 검색어가 {운반, 블록, 촬영}이면 교집합은 두 단어이고 점수는 2입니다.

<a id="waffle_terms_17_3"></a>
### 근거가 있다는 사실을 어디까지 믿을까요?

[통합 교안 57쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_17_3)

- **인용과 근거** 근거(evidence)는 판단을 뒷받침하는 자료입니다. 인용(quote)은 원문의 일부를 옮긴 문구입니다. answer()는 반환 ID와 해당 원문의 부분 문자열을 대조합니다.
- **반환 상태** cited는 ID와 인용 대조 통과, unsupported는 인용 검증 실패, no_evidence는 검색된 근거가 없다는 뜻입니다. 올바른 문장을 인용해도 질문과 무관할 수 있습니다.
- **도구와 모델** Ollama는 로컬에서 언어 모델 요청을 처리합니다. 코드는 HTTP 요청에 질문과 검색 문서를 JSON으로 보내고 모델 응답의 ID와 문구를 꺼냅니다.

문서에 ‘0.5초’가 있으면 규칙의 출처를 확인할 수 있습니다. 현재 블록이 그 규칙을 충족했는지는 stable_s와 물리 관측으로 판단합니다.

<a id="waffle_terms_17_4"></a>
### 검색 성공률과 답변 정확도의 분모

[통합 교안 58쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_17_4)

- **근거 포함률** 이 예에서는 질문마다 필요한 근거가 하나입니다. 상위 k개 안에 그 근거가 들어온 질문 수를 전체 질문 수로 나누면 검색의 적중 비율을 얻습니다.
- **조건부 정확도** 조건부 정확도는 특정 조건을 충족한 사례만 분모로 삼습니다. 근거가 들어온 질문 8건 중 6건에 정답을 썼다면 그 조건에서 6/8=75%입니다.
- **종단 간 정확도** 처음부터 끝까지 답이 맞은 비율은 전체 질문을 분모로 셉니다. 나머지 두 질문도 틀렸다면 전체 10건 중 6건이므로 60%입니다.

질문 · 검색된 근거가 없는 질문까지 버리고 75%만 보고하면 어떤 문제가 숨겨질까요? 검색 단계의 누락이 가려집니다.

<a id="waffle_terms_17_5"></a>
### 연구 자료에서 모델과 평가 이름을 구분합니다

[통합 교안 59쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_17_5)

- **학회와 프리프린트** ICRA는 로봇·자동화 학회이고 CVPR은 컴퓨터 비전·패턴인식 학회입니다. 프리프린트는 연구자가 공개한 원고입니다. 공개 날짜와 학회 발표 여부를 따로 확인합니다.
- **모델과 방법** SmolVLM2는 시각·언어 모델 계열, SlotVLA는 물체와 관계 표현을 쓰는 연구 모델입니다. Embodied RAG++는 장면의 물체와 가능한 기능을 고려해 근거를 찾는 연구입니다.
- **평가 도구** LIBERO-Plus는 조건을 바꿔 로봇 정책의 견고성을 평가하는 벤치마크입니다. 견고성은 잡음·조명·시점 등 조건이 달라질 때도 성능을 유지하는 정도입니다.

논문의 수치를 옮길 때는 모델 이름, 사용 장비, 시험 과제, 실제 반복 횟수를 함께 읽습니다. Waffle의 측정값은 수업 실험에서 따로 확인합니다.

**코드와 원문**

- [RAG 원 논문](https://arxiv.org/abs/2005.11401)
- [Embodied RAG++](https://arxiv.org/abs/2611.07517)
- [lab.py](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/lessons/14-18/lab.py#L62-L82)

## 18강

<a id="waffle_terms_18_1"></a>
### 플래너가 작업 순서를 표현하는 방법

[통합 교안 68쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_18_1)

- **하위 작업** 플래너(planner)는 목표를 실행 가능한 하위 작업들의 계획으로 바꿉니다. ‘운반 후 사진’은 운반과 촬영 두 작업이며 촬영에는 운반 완료 조건이 붙습니다.
- **그래프와 의존성** 그래프의 노드(node)는 작업 하나이고 방향이 있는 간선(edge)은 선행 관계입니다. depends_on=[0]은 그 턴이 0번 턴의 완료에 의존한다는 뜻입니다.
- **위상 정렬** 위상 정렬은 선행 작업이 끝난 노드를 먼저 꺼내 실행 가능한 순서를 만듭니다. 남은 노드 중 어느 것도 꺼낼 수 없으면 순환 같은 잘못된 의존 관계를 검사합니다.

A가 B를 기다리고 B도 A를 기다리면 시작할 작업이 없습니다. ordered_nodes()는 이 상태를 plan.cycle로 반환합니다.

<a id="waffle_terms_18_2"></a>
### 검증 실험에서 바꾸는 것과 고정하는 것

[통합 교안 69쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_18_2)

- **벤치마크** 벤치마크(benchmark)는 같은 조건으로 여러 방법을 비교하는 시험 집합과 절차입니다. 수업의 고정 사례는 지시문과 기대 종료 사유를 함께 담습니다.
- **기준선과 검증 경로** baseline은 비교의 기준이 되는 방법입니다. guarded는 같은 입력에 추가 검사를 적용하는 경로입니다. 둘의 입력과 정답을 고정해야 차이의 원인을 좁힐 수 있습니다.
- **오류 주입** 오류 주입은 특정 검사가 작동하는지 확인하기 위해 입력이나 도구 상태를 의도적으로 바꾸는 방법입니다. 예를 들어 좌표 단위를 m에서 mm로만 바꿉니다.

expected는 기대한 종료 사유, observed는 실제 관측한 종료 사유입니다. 거부가 기대값이면 올바르게 거부한 실행도 정답입니다.

<a id="waffle_terms_18_3"></a>
### 첫 실패 단계를 로그에서 찾는 법

[통합 교안 70쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_18_3)

- **계획과 인식** ground.ambiguous는 대상 해석이 하나로 정해지지 않았다는 뜻입니다. plan.cycle은 실행 가능한 선후 관계를 만들지 못한 상태입니다.
- **자료와 계약** rag.no_evidence는 요청 버전의 관련 근거를 찾지 못한 상태입니다. contract.frame_unit_version은 좌표계·단위·버전 중 계약 불일치, contract.stale은 오래된 관측입니다.
- **도구와 종료** tool.unavailable은 도구 사용 실패, result.unknown은 제한 시간에 결과를 확인하지 못한 상태, completed는 이 평가 경로의 검사를 끝까지 통과했다는 뜻입니다.

검사 순서도 결과를 바꿉니다. 대상과 단위가 모두 잘못됐어도 첫 Reject만 기록하므로 보고된 이유가 유일한 문제라고 결론 내릴 수 없습니다.

<a id="waffle_terms_18_4"></a>
### 파지, 안착, 성공을 각각 어떻게 셀까요?

[통합 교안 71쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_18_4)

- **파지와 오파지** 파지(pick)는 목표 물체를 잡아 드는 행동입니다. 실습은 높이 증가와 손끝 거리를 함께 봅니다. wrong_pick은 다른 물체를 들어 올렸는지를 표시합니다.
- **안착과 오차** 안착(settle)은 목표 위에서 안정된 상태가 유지되는 것입니다. 중심 오차는 최종 물체 중심과 목표 중심의 수평 거리입니다. 한 프레임의 겹침만으로는 부족합니다.
- **성공률과 %p** 성공률은 성공 횟수/실행 횟수입니다. 40%에서 100%로 바뀐 차이는 60퍼센트포인트(%p)입니다. 물리 실행, 정답 사유 일치, 모델 종료 선언은 서로 다른 지표입니다.

실습의 두 채점기를 비교합니다. 색상 궤적 시험은 연속 안착 시간을, 복합 미션은 들기·목표 오차·촬영 순서 및 종료 상태를 확인합니다.

<a id="waffle_terms_18_5"></a>
### 새 배치에서의 성공은 어떻게 확인할까요?

[통합 교안 72쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_18_5)

- **일반화** 일반화는 학습에 쓰지 않은 조건에서도 과제를 수행하는 능력입니다. 미관측(held-out) 배치는 훈련과 겹치지 않도록 떼어 둔 시험 배치입니다.
- **교란과 통제** 교란(perturbation)은 조명·카메라·배치 등 한 조건의 변화입니다. 같은 지시를 유지하고 배치만 반전하면 왼쪽의 색이 바뀌어도 위치 지시를 따르는지 확인할 수 있습니다.
- **짝지은 비교** 두 방법을 같은 시드·배치에서 각각 실행해 같은 난이도의 결과끼리 비교합니다. 지연(latency)은 입력부터 응답까지 걸린 시간이며 단위 ms는 1/1,000초입니다.

각 배치를 1회씩 실행한 결과는 그 두 번의 관측입니다. 서로 다른 시드에서 반복한 성공 횟수와 실패 단계를 함께 기록합니다.

<a id="waffle_terms_18_6"></a>
### 한 턴, 실행 예산, 종료 사유를 구분합니다

[통합 교안 73쪽](https://docs.google.com/presentation/d/1FeQRLIcLisJhND0R2zncbqJo7Z8gOo95KewRqR4kKms/edit#slide=id.waffle_terms_18_6)

- **턴과 예산** 턴(turn)은 실행기가 다음 행동을 골라 처리하는 한 차례입니다. 예산(budget)은 허용하는 최대 턴 수입니다. 한 번의 운반 턴 안에서 여러 관절 목표를 적용할 수 있습니다.
- **모델 호출과 추론** planner_calls는 계획 모델에 요청한 횟수이고 vla_inferences는 행동 정책에 예측을 요청한 횟수입니다. 92개 목표를 한꺼번에 예측하면 행동 추론은 한 번입니다.
- **종료와 채점** budget_exhausted는 예산 소진, blocked는 수행 불가 판단, model_finished는 실행 루프의 완료 사유입니다. photo_count는 독립 채점기가 요구한 사진 수와 실측 수의 불일치입니다.

같은 지시라도 2턴이면 촬영 → 운반에서 끝날 수 있습니다. ‘운반 후 촬영’까지 관측돼야 전체 지시의 성공입니다.

**코드와 원문**

- [lab.py](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/lessons/14-18/lab.py#L85-L130)
- [score.py](https://github.com/SpartaPA/waffle-mpx-lyrical/blob/feature/open-instruction-vla/lessons/13-react/evaluation/score.py)

