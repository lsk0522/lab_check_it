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
        # msg.detected_classes = ['mask', 'no_goggles']
        # msg.confidences = [0.95, 0.88]
        # msg.status = 'PARTIAL'  # 이 판단은 ppe_judge.py에서 하거나 여기서 할 수 있음
        
        # self.result_pub.publish(msg)
        
        # 디버깅용 화면 출력 (실제 적용 시 rqt_image_view 사용 권장)
        cv2.imshow("YOLO Detection Stream", cv_image)
        cv2.waitKey(3)

if __name__ == '__main__':
    try:
        detector = YoloDetector()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
