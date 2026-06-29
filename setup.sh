#!/bin/bash

echo "================================================"
echo "   PPE Detection System - Environment Setup     "
echo "================================================"

# 1. 시스템 패키지 업데이트
echo "[1/5] 패키지 목록 업데이트 중..."
sudo apt-get update

# 2. ROS 의존성 패키지 설치
echo "[2/5] ROS 필수 패키지 설치 중..."
sudo apt-get install -y ros-noetic-usb-cam \
                        ros-noetic-cv-bridge \
                        ros-noetic-vision-opencv \
                        ros-noetic-rosbridge-server

# 3. Python 의존성 설치
echo "[3/5] Python 필수 라이브러리 설치 중..."
sudo apt-get install -y python3-pip
pip3 install ultralytics flask flask-socketio roboflow

# 4. 스크립트 실행 권한 부여
echo "[4/5] ROS 파이썬 노드 실행 권한 부여 중..."
if [ -d "src/ppe_system/src" ]; then
    chmod +x src/ppe_system/src/*.py
    echo "권한 부여 완료."
else
    echo "경고: src/ppe_system/src 경로를 찾을 수 없습니다."
fi

# 5. 워크스페이스 빌드
echo "[5/5] ROS 워크스페이스 빌드 (catkin_make)..."
if [ -d "src" ]; then
    catkin_make
    echo "================================================"
    echo " 🚀 셋업이 모두 완료되었습니다! "
    echo " 터미널에 아래 명령어를 입력하여 환경을 적용해 주세요:"
    echo " source devel/setup.bash"
    echo "================================================"
else
    echo "❌ 오류: 'src' 폴더를 찾을 수 없습니다. 이 스크립트를 워크스페이스 최상단에서 실행해 주세요."
fi
