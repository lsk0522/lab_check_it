# YOLOv5 커스텀 데이터셋 학습 가이드 (Google Colab용)

본 문서는 실습실 보호장비(PPE) 감지를 위한 YOLOv5 모델 학습 가이드입니다.
아래 코드 블록들을 순서대로 Google Colab의 셀(Cell)에 복사하여 실행하세요.

### 1. YOLOv5 클론 및 필수 라이브러리 설치
```python
# YOLOv5 소스코드 다운로드 및 이동
!git clone https://github.com/ultralytics/yolov5
%cd yolov5

# 필수 라이브러리 설치
%pip install -qr requirements.txt

# PyTorch GPU 활성화 확인 (런타임 유형이 T4 GPU로 설정되어 있어야 함)
import torch
print('GPU 활성화 확인:', torch.cuda.get_device_name(0))
```

### 2. Roboflow 데이터셋 다운로드
```python
# roboflow 라이브러리 설치
!pip install -q roboflow
from roboflow import Roboflow

# 주의: 아래 api_key 문자열 안에 본인의 API Key를 입력해야 합니다!
rf = Roboflow(api_key="본인의_API_키를_여기에_입력하세요") 
project = rf.workspace("keremberke").project("protective-equipment-detection")

# YOLOv5 PyTorch 형식으로 데이터셋 다운로드
dataset = project.version(1).download("yolov5")
```

### 3. 커스텀 모델 학습 진행
```python
# 640 사이즈, 배치 16, 100 에포크로 학습 진행 (yolov5s 사전학습 가중치 사용)
!python train.py --img 640 --batch 16 --epochs 100 --data {dataset.location}/data.yaml --weights yolov5s.pt --cache
```

### 4. 학습된 가중치 다운로드
```python
from google.colab import files

# 가장 성능이 좋은 가중치(best.pt)를 내 컴퓨터로 다운로드
files.download('./runs/train/exp/weights/best.pt')
```

학습 완료 후 다운로드 받은 `best.pt` 파일을 워크스페이스의 `models/ppe_yolov5s.pt` 로 복사하여 사용하세요.
