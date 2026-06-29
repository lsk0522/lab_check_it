# PPEResult.msg
# 객체 인식 결과 배열 및 전체 판단 상태
string[] detected_classes  # ["mask", "no_goggles", ...]
float32[] confidences      # [0.95, 0.88, ...]
string status              # 최종 상태: "PASS", "FAIL", "PARTIAL"
