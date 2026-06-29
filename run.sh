#!/bin/bash

# ========================================================
#  PPE Detection System - Unified Launcher
# ========================================================

# 이 스크립트가 종료될 때 백그라운드 프로세스(ROS)를 모두 깔끔하게 종료합니다.
trap "echo -e '\n[시스템 종료] 모든 백그라운드 프로세스를 종료합니다...'; rosnode kill -a > /dev/null 2>&1; pkill -f 'rosmaster'; pkill -f 'localtunnel'; exit 0" SIGINT SIGTERM

echo "========================================================"
echo "      🚀 PPE Detection System 로딩 중... "
echo "========================================================"

# 기존 프로세스 찌꺼기 정리
pkill -f 'rosmaster' > /dev/null 2>&1
pkill -f 'localtunnel' > /dev/null 2>&1
rm -f /tmp/ppe_public_url.txt

# 워크스페이스 소싱
source devel/setup.bash

# 백그라운드로 ROS 통합 런치 파일 실행 (터미널 출력 로그 무시)
echo "▶ 로봇 운영 체제(ROS) 및 Picam 노드 활성화 중..."
roslaunch ppe_system ppe_full.launch > /dev/null 2>&1 &

echo "▶ 딥러닝(YOLOv5) 추론 엔진 로딩 중..."
sleep 3
echo "▶ 웹 대시보드 외부망 접속 주소(localtunnel) 발급 대기 중..."

# localtunnel URL이 생성될 때까지 대기
timeout=20
count=0
public_url=""

while [ $count -lt $timeout ]; do
    if [ -f "/tmp/ppe_public_url.txt" ]; then
        public_url=$(cat /tmp/ppe_public_url.txt)
        if [ ! -z "$public_url" ]; then
            break
        fi
    fi
    sleep 1
    count=$((count+1))
done

echo ""
echo "========================================================"
if [ -z "$public_url" ]; then
    echo "⚠️ 외부 접속 주소를 가져오지 못했습니다. 로컬(http://localhost:5000)에서 접속해 주세요."
    echo "   (※ npx 명령어가 설치되어 있는지 확인이 필요합니다.)"
else
    echo "✅ 웹 대시보드 스마트폰/외부 접속 주소:"
    echo "🌐 -> $public_url"
fi
echo ""
echo "🎨 다이렉트 GUI 화면(OpenCV 창)이 팝업되었습니다."
echo "   (창이 안 보이면 터미널 뒤에 숨어있는지 확인해 주세요!)"
echo ""
echo "🛑 시스템을 종료하려면 이 창에서 [Ctrl + C] 를 누르세요."
echo "========================================================"

# 백그라운드 프로세스가 유지되도록 무한 대기
while true; do
    sleep 1
done
