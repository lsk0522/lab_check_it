#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from flask import Flask
from ppe_system.msg import PPEResult
import threading
import subprocess
import time
import os
import logging

app = Flask(__name__)

# 전역 변수로 상태 저장
current_status = "WAITING"
detected_items = []

def ros_status_callback(msg):
    global current_status
    current_status = msg.data

def ros_result_callback(msg):
    global detected_items
    detected_items = list(msg.detected_classes)

def start_ros_node():
    rospy.init_node('web_server_node', anonymous=True, disable_signals=True)
    rospy.Subscriber("/ppe_status", String, ros_status_callback)
    rospy.Subscriber("/ppe_detection/result", PPEResult, ros_result_callback)
    rospy.spin()

@app.route('/')
def index():
    return f"""
    <html>
        <head>
            <title>PPE Detection Dashboard</title>
            <meta http-equiv="refresh" content="1"> <!-- 1초마다 자동 새로고침 -->
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin-top: 100px; background-color: #f4f7f6; }}
                h1 {{ color: #333; }}
                .status-PASS {{ color: #2ecc71; font-size: 4em; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
                .status-FAIL {{ color: #e74c3c; font-size: 4em; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
                .status-PARTIAL {{ color: #f39c12; font-size: 4em; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
                .status-WAITING {{ color: #95a5a6; font-size: 4em; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
                .detected {{ font-size: 1.5em; color: #555; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>실시간 보호장비 착용 현황</h1>
            <div class="status-{current_status}">{current_status}</div>
            <div class="detected">감지된 객체: {', '.join(detected_items) if detected_items else '없음'}</div>
        </body>
    </html>
    """

def start_localtunnel():
    # 기존 프로세스 정리
    os.system("pkill -f 'localtunnel' > /dev/null 2>&1")
    time.sleep(1)
    
    # npx localtunnel을 실행하여 외부 접속 URL 획득
    try:
        proc = subprocess.Popen(['npx', 'localtunnel', '--port', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in proc.stdout:
            if "your url is:" in line:
                url = line.strip().split("your url is:")[1].strip()
                # 쉘 스크립트에서 읽을 수 있도록 파일로 저장
                with open("/tmp/ppe_public_url.txt", "w") as f:
                    f.write(url)
                rospy.loginfo(f"Localtunnel URL obtained: {url}")
                break
    except Exception as e:
        rospy.logerr(f"Localtunnel 실행 실패 (npx가 설치되어 있는지 확인하세요): {e}")

if __name__ == '__main__':
    # ROS 통신용 스레드 시작
    threading.Thread(target=start_ros_node, daemon=True).start()
    
    # Localtunnel 터널링 스레드 시작
    threading.Thread(target=start_localtunnel, daemon=True).start()
    
    # 터미널 출력(로그)을 최소화하기 위해 Flask 자체 로거 끄기
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # 웹 서버 구동
    app.run(host='0.0.0.0', port=5000, debug=False)
