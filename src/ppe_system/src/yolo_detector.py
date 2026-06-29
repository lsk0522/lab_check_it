#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
# from ultralytics import YOLO  # 향후 YOLO 연동 시 주석 해제
from ppe_system.msg import PPEResult
from std_msgs.msg import String

class YoloDetector:
    def __init__(self):
        rospy.init_node('yolo_detector_node', anonymous=True)
        self.bridge = CvBridge()
        
        # 모델 로드 (학습된 가중치 경로 지정)
        # self.model = YOLO('/path/to/ppe_yolov5s.pt')
        
        # 카메라 영상 토픽 구독
        self.image_sub = rospy.Subscriber("/picam/image_raw", Image, self.image_callback)
        # 추론 결과 및 오버레이 이미지 발행 토픽
        self.result_pub = rospy.Publisher("/ppe_detection/result", PPEResult, queue_size=10)
        self.overlay_pub = rospy.Publisher("/ppe_detection/image_overlay", Image, queue_size=10)
        
        # 상태 구독 (ppe_judge 로부터)
        self.current_status = "WAITING"
        self.status_sub = rospy.Subscriber("/ppe_status", String, self.status_callback)
        
        rospy.loginfo("YOLO Detector Node Initialized. Waiting for image...")

    def status_callback(self, msg):
        self.current_status = msg.data

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(f"CV Bridge Error: {e}")
            return

        # -----------------------------
        # TODO: YOLOv5 추론 로직 구현
        # -----------------------------
        # results = self.model(cv_image)
        
        # PPEResult 메시지 생성 (테스트용 더미 데이터)
        msg = PPEResult()
        
        # Kiosk GUI 드로잉 (사용자 화면용 프리미엄 오버레이)
        height, width = cv_image.shape[:2]
        overlay = cv_image.copy()
        
        # 상태 확인 (ppe_judge 결과 반영)
        status = self.current_status
        
        # 람보르기니 테마 색상 (BGR)
        if status == "PASS":
            bg_color = (226, 171, 41) # Cyan Pulse (#29ABE2)
            msg_text = "ACCESS GRANTED"
            text_color = (0, 0, 0) # Black text
        elif status == "FAIL":
            bg_color = (0, 192, 255) # Lamborghini Gold (#FFC000)
            msg_text = "ACCESS DENIED"
            text_color = (0, 0, 0) # Black text
        else:
            bg_color = (32, 32, 32) # Charcoal (#202020)
            msg_text = "SYSTEM READY"
            text_color = (255, 255, 255) # White text

        # 상단 블리드 배너 (Lamborghini Design System - Sharp corners & flat colors)
        cv2.rectangle(overlay, (0, 0), (width, 100), bg_color, -1)
        # 불투명도를 높여 강렬한 대비를 줌
        cv2.addWeighted(overlay, 0.95, cv_image, 0.05, 0, cv_image)
        
        # 날카로운 대문자(ALL-CAPS) 오버레이 
        cv2.putText(cv_image, msg_text, (32, 64), cv2.FONT_HERSHEY_TRIPLEX, 1.5, text_color, 2, cv2.LINE_AA)

        # 오버레이 이미지 토픽으로 발행 (웹 서버용)
        try:
            overlay_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
            self.overlay_pub.publish(overlay_msg)
        except CvBridgeError as e:
            rospy.logerr(f"Overlay Publish Error: {e}")

if __name__ == '__main__':
    try:
        detector = YoloDetector()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
