# Inspire Hand Visualization
python을 이용하여 inspire hand로 수집한 데이터를 rerun을 이용해서 시각화하는 코드입니다. rerun을 이용하여 3d 공간 상에 로봇 손의 움직임과 sensor pad를 볼 수 있습니다.

## Enviorments
- python 3.10.10 or higher
- `pip install -r requirements.txt` or <br> `pip install numpy pandas scipy rerun-sdk trimesh yourdfpy pillow opencv-python`

## 실행 인자
- `-c` | `--chunk`: episode에 해당하는 데이터가 들어있는 chuck값입니다. int로 입력 받으며, 기본값은 0 입니다.
- `-e` | `--episode`: 시각화 하기 위한 episode값입니다. int로 입력 받으며, 기본값은 0입니다.

## Directory Structure
이 코드는 URDF 모델 파일, 데이터셋(Parquet), 그리고 비디오 파일이 특정 디렉토리 규칙에 따라 배치되어 있다고 가정합니다.
```
inspire-visualization/
├── main.py
├── config.py
├── robot_handler.py
├── utils.py
├── models/
│  ├── inspire_hand_left.urdf
│  ├── inspire_hand_right.urdf
│  └── meshes/
└── data/
   ├── data/
   │  └── chunk-{chunk:03}/
   │     └── episode_{episode:06}.parquet
   └── videos/
      └── chunk-{chunk:03}/
         └── observation.images.cam_left_high/
            └── episode_{episode:06}.mp4
```

## Dataset Format
`.parquet` 파일은 매 프레임의 로봇 상태와 센서 데이터를 담고 있는 시계열 데이터셋입니다.

**Required Columns**
- `frame_index`: 각 데이터 행의 순서를 나타내는 index (int).
- `observation.state`: 로봇의 관측 상태 값 (배열 또는 배열 형태의 string).
	- `config.py`의 `JOINT_MAP`에 정의된 인덱스(14~25번)를 통해 각 손가락 joint 값으로 변환됩니다.
- `observation.images.[sensor_info]`: 촉각 또는 포인트 센서 이미지 데이터 (바이트 형태).
	-   `utils.py`의 파싱 규칙에 따라 컬럼명에 `left`/`right`, 파트 이름(`thumb`, `index` 등), 센서 종류(`tip`, `pad`, `nail` 등)가 포함되어야 합니다.
	- 예시 컬럼명: `observation.images.index_tip_left`, `observation.images.palm_pad_right`.

**데이터 형식 (Data Format)**
-   이미지 데이터: Python의 `dict` 형태(`{'bytes': ...}`)이거나, 이를 문자열로 변환한 형태, 혹은 순수 `bytes` 데이터여야 합니다.
-   상태 데이터: 정규화된 값(`0.0` ~ `1.0`)으로 저장되어 있어야 하며, 코드는 이를 바탕으로 실제 조인트 각도로 변환합니다.

## Third-party Assets
- Inspire Hand Model: Based on the URDF and meshes provided by [dex-urdf](https://github.com/dexsuite/dex-urdf).