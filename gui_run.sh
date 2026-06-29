#!/bin/bash

# ========================================================
#  PPE Detection System - Unified Launcher
# ========================================================

# 이 스크립트가 종료될 때 백그라운드 프로세스(ROS)를 모두 깔끔하게 종료합니다.
trap "echo -e '\n[시스템 종료] 모든 백그라운드 프로세스를 종료합니다...'; rosnode kill -a > /dev/null 2>&1; pkill -f 'rosmaster'; pkill -f 'pinggy'; pkill -f 'ssh'; exit 0" SIGINT SIGTERM

echo "========================================================"
echo "      🚀 PPE Detection System 로딩 중... "
echo "========================================================"

# 기존 프로세스 찌꺼기 정리
pkill -f 'rosmaster' > /dev/null 2>&1
pkill -f 'pinggy' > /dev/null 2>&1
pkill -f 'ssh' > /dev/null 2>&1
rm -f /tmp/ppe_public_url.txt

# 워크스페이스 소싱
source devel/setup.bash

# 백그라운드로 ROS 통합 런치 파일 실행 (터미널 출력 로그 무시)
echo "▶ 로봇 운영 체제(ROS) 및 Picam 노드 활성화 중..."
roslaunch ppe_system ppe_full.launch > /dev/null 2>&1 &

echo "▶ 딥러닝(YOLOv5) 추론 엔진 로딩 중..."
sleep 3
echo "▶ 웹 대시보드 외부망 접속 주소 발급 대기 중 (Pinggy)..."

# Pinggy URL이 생성될 때까지 대기
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

WSL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "========================================================"
echo "🌍 네트워크 환경 분석 완료!"
echo "   WSL 환경 내부 IP 주소: $WSL_IP"
echo ""

if [ -z "$public_url" ]; then
    echo "⚠️ 외부 접속 주소를 가져오지 못했습니다."
    echo "✅ 윈도우 브라우저에서 아래 주소로 대시보드에 접속하세요:"
    echo "🌐 -> http://$WSL_IP:5000"
    echo "   (※ http://localhost:5000 이 안될 경우 위 주소 사용)"
else
    echo "✅ 윈도우 브라우저(로컬) 접속 주소:"
    echo "🌐 -> http://$WSL_IP:5000"
    echo ""
    echo "✅ 스마트폰/외부(localtunnel) 접속 주소:"
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
