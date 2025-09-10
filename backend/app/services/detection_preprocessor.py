# detection_preprocessor.py - AirBirds 탐지 결과 전처리
import re
from datetime import datetime
from typing import List, Dict, Any


class DetectionPreprocessor:
    @staticmethod
    def convert_bbox_to_relative(detection_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        AirBirds 탐지 결과를 상대좌표로 변환
        """
        image_height, image_width = detection_result["image_shape"]
        processed_detections = []
        
        for detection in detection_result["detections"]:
            bbox = detection["bbox"]
            
            # 바운딩 박스 중심점 계산
            center_x = (bbox["x1"] + bbox["x2"]) / 2
            center_y = (bbox["y1"] + bbox["y2"]) / 2
            
            # 상대좌표로 변환 (0~1 범위)
            u = center_x / image_width   # 수평 상대좌표
            v = center_y / image_height  # 수직 상대좌표
            
            # 이미지명에서 CCTV ID와 타임스탬프 추출
            cctv_id = DetectionPreprocessor.extract_cctv_id(detection_result["image_name"])
            timestamp = DetectionPreprocessor.extract_timestamp(detection_result["image_name"])
            
            processed_detections.append({
                "cctv_id": cctv_id,
                "pos": [u, v],
                "class": detection["class_name"],
                "confidence": detection["confidence"],
                "timestamp": timestamp,
                "original_bbox": bbox
            })
        
        return processed_detections
    
    @staticmethod
    def extract_cctv_id(image_name: str) -> str:
        """이미지명에서 CCTV ID 추출"""
        # "D02_20210721142744_0007999.png" -> "D02"
        parts = image_name.split("_")
        if len(parts) >= 1:
            return parts[0]
        return "unknown"
    
    @staticmethod
    def extract_timestamp(image_name: str) -> str:
        """이미지명에서 타임스탬프 추출"""
        # "D02_20210721142744_0007999.png" -> "2021-07-21T14:27:44Z"
        parts = image_name.split("_")
        if len(parts) >= 3:
            date_str = parts[1]  # "20210721"
            time_str = parts[2]  # "142744"
            
            # 파일 확장자 제거
            if "." in time_str:
                time_str = time_str.split(".")[0]
            
            # 숫자만 추출
            time_str = re.sub(r'\D', '', time_str)[:6]  # 6자리만 가져오기
            
            if len(date_str) == 8 and len(time_str) >= 6:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                hour = time_str[:2]
                minute = time_str[2:4]
                second = time_str[4:6]
                
                return f"{year}-{month}-{day}T{hour}:{minute}:{second}Z"
        
        return datetime.now().isoformat() + "Z"  # 기본값
