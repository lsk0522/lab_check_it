#!/bin/bash

echo "========================================================"
echo "    🔄 PPE Detection System 최신 업데이트 스크립트      "
echo "========================================================"

echo "[1/3] GitHub에서 최신 코드 강제 다운로드 중..."
# 로컬에 임의로 변경된 사항이 있으면 무시하고 깃허브 원본으로 덮어씁니다.
git fetch --all
git reset --hard origin/main
git pull

echo "[2/3] 스크립트 실행 권한 업데이트 중..."
chmod +x *.sh src/ppe_system/src/*.py

echo "[3/3] ROS 워크스페이스 다시 빌드 중..."
if [ -d "src" ]; then
    catkin_make
    source devel/setup.bash
    echo "========================================================"
    echo " ✅ 업데이트가 성공적으로 완료되었습니다!"
    echo " 시스템을 실행하려면 아래 명령어를 입력하세요:"
    echo " ./gui_run.sh"
    echo "========================================================"
else
    echo "❌ 오류: 'src' 폴더를 찾을 수 없습니다. 워크스페이스 최상단에서 실행해 주세요."
fi
