#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
# from ultralytics import YOLO  # 향후 YOLO 연동 시 주석 해제
from ppe_system.msg import PPEResult

class YoloDetector:
    def __init__(self):
        rospy.init_node('yolo_detector_node', anonymous=True)
        self.bridge = CvBridge()
        
        # 모델 로드 (학습된 가중치 경로 지정)
        # self.model = YOLO('/path/to/ppe_yolov5s.pt')
        
        # 카메라 영상 토픽 구독
        self.image_sub = rospy.Subscriber("/picam/image_raw", Image, self.image_callback)
        # 추론 결과 발행 토픽
        self.result_pub = rospy.Publisher("/ppe_detection/result", PPEResult, queue_size=10)
        
        rospy.loginfo("YOLO Detector Node Initialized. Waiting for image...")

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
        
        # 상태 확인 (현재는 더미 상태 - 실제로는 ppe_judge.py의 판단 결과를 구독해야 함)
        # 로직 고도화 전까지 임시로 "WAITING" 표시 (추후 /ppe_status 구독 연동)
        status = "WAITING"
        
        if status == "PASS":
            bg_color = (0, 144, 74) # semantic-success
            msg_text = "ACCESS GRANTED: PPE VERIFIED"
        elif status == "FAIL":
            bg_color = (28, 41, 218) # Rosso Corsa (BGR)
            msg_text = "ACCESS DENIED: WEAR PPE"
        else:
            bg_color = (48, 48, 48) # canvas-elevated
            msg_text = "SYSTEM READY: SCANNING..."

        # 상단 블리드 배너 (Ferrari Design System - Sharp corners & flat colors)
        cv2.rectangle(overlay, (0, 0), (width, 80), bg_color, -1)
        # 반투명 합성
        cv2.addWeighted(overlay, 0.95, cv_image, 0.05, 0, cv_image)
        
        # 흰색 텍스트 오버레이 (Display-lg 느낌의 크기 및 굵기)
        cv2.putText(cv_image, msg_text, (32, 52), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

        # 다이렉트 GUI Kiosk 출력
        cv2.imshow("PPE Detection System - User Kiosk", cv_image)
        cv2.waitKey(1)

if __name__ == '__main__':
    try:
        detector = YoloDetector()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
