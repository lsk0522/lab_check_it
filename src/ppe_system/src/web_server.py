#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from flask import Flask, render_template, jsonify
from datetime import datetime
from ppe_system.msg import PPEResult
import threading
import subprocess
import time
import os
import logging

template_dir = os.path.abspath(os.path.dirname(__file__)) + '/templates'
app = Flask(__name__, template_folder=template_dir)

# 전역 변수로 상태 저장
current_status = "WAITING"
last_logged_status = "WAITING"
detected_items = []
stats = {"total": 0, "violations": 0}
logs = []

def ros_status_callback(msg):
    global current_status, stats, logs, last_logged_status
    current_status = msg.data
    
    # 상태가 변경될 때만 통계 및 로그 업데이트 (중복 카운트 방지)
    if current_status != last_logged_status and current_status in ["PASS", "FAIL"]:
        stats["total"] += 1
        if current_status == "FAIL":
            stats["violations"] += 1
            
        logs.insert(0, {
            "status": "ACCESS GRANTED" if current_status == "PASS" else "ACCESS DENIED",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        if len(logs) > 5:
            logs.pop()
            
        last_logged_status = current_status
    elif current_status == "WAITING":
        last_logged_status = "WAITING"

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
    return render_template('admin.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": current_status,
        "items": detected_items,
        "stats": stats,
        "logs": logs
    })

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
