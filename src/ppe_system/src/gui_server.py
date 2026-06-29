#!/usr/bin/env python3
import rospy
from flask import Flask, render_template, Response
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import threading
import os
import logging
import time

template_dir = os.path.abspath(os.path.dirname(__file__)) + '/templates'
app = Flask(__name__, template_folder=template_dir)

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

def start_ros_node():
    rospy.init_node('gui_server_node', anonymous=True, disable_signals=True)
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
    return render_template('kiosk.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=start_ros_node, daemon=True).start()
    
    # 끄기
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Kiosk GUI 서버 구동 (포트 8787)
    app.run(host='0.0.0.0', port=8787, debug=False)
