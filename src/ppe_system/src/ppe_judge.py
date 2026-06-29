#!/usr/bin/env python3
import rospy
from ppe_system.msg import PPEResult
from std_msgs.msg import String

class PPEJudge:
    def __init__(self):
        rospy.init_node('ppe_judge_node', anonymous=True)
        # YOLO 판단 결과 구독
        self.result_sub = rospy.Subscriber("/ppe_detection/result", PPEResult, self.result_callback)
        # 최종 상태 (PASS/FAIL/PARTIAL) 발행
        self.status_pub = rospy.Publisher("/ppe_status", String, queue_size=10)
        rospy.loginfo("PPE Judge Node Initialized.")

    def result_callback(self, data):
        detected = data.detected_classes
        
        has_mask = 'mask' in detected
        has_goggles = 'goggles' in detected
        
        # 판단 로직
        status = ""
        if has_mask and has_goggles:
            status = "PASS"    # 초록 LED
        elif not has_mask and not has_goggles:
            status = "FAIL"    # 빨간 LED + 부저
        else:
            status = "PARTIAL" # 노란 LED (둘 중 하나만 착용)
            
        rospy.loginfo(f"Current PPE Status: {status}")
        self.status_pub.publish(status)

if __name__ == '__main__':
    try:
        judge = PPEJudge()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
