#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from flask import Flask, render_template, jsonify, Response
from datetime import datetime
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
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

# 영상 스트리밍용
bridge = CvBridge()
latest_frame = None

def image_callback(msg):
    global latest_frame
    try:
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        ret, buffer = cv2.imencode('.jpg', cv_image)
        if ret:
            latest_frame = buffer.tobytes()
    except Exception as e:
        pass

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
    rospy.Subscriber("/ppe_detection/image_overlay", Image, image_callback)
    rospy.spin()

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        else:
            time.sleep(0.1)

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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_pinggy_tunnel():
    # 기존 SSH 터널 프로세스 정리
    os.system("pkill -f 'pinggy' > /dev/null 2>&1")
    time.sleep(1)
    
    # Pinggy SSH 터널(회원가입/설치 필요없는 외부망 접속) 실행
    try:
        proc = subprocess.Popen(
            ['ssh', '-o', 'StrictHostKeyChecking=no', '-p', '443', '-R0:localhost:5000', 'a.pinggy.io'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in proc.stdout:
            if "https://" in line and "pinggy" in line:
                url = line.strip()
                # 쉘 스크립트에서 읽을 수 있도록 파일로 저장
                with open("/tmp/ppe_public_url.txt", "w") as f:
                    f.write(url)
                rospy.loginfo(f"Pinggy URL obtained: {url}")
                break
    except Exception as e:
        rospy.logerr(f"Pinggy SSH 터널 실행 실패: {e}")

if __name__ == '__main__':
    # ROS 통신용 스레드 시작
    threading.Thread(target=start_ros_node, daemon=True).start()
    
    # Pinggy 터널링 스레드 시작 (외부망 스마트폰 접속용)
    threading.Thread(target=start_pinggy_tunnel, daemon=True).start()
    
    # 터미널 출력(로그)을 최소화하기 위해 Flask 자체 로거 끄기
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # 웹 서버 구동
    app.run(host='0.0.0.0', port=5000, debug=False)
