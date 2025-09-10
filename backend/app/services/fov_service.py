# fov_service.py - 시야각 내 새 위치 계산 서비스
import math
from typing import List, Dict, Any, Tuple
from .detection_preprocessor import DetectionPreprocessor


class FovService:
    @staticmethod
    def process_airbirds_detection(detection_json: Dict[str, Any], cctv_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        AirBirds 탐지 결과를 지리적 좌표로 변환
        """
        # 1. 픽셀 좌표 → 상대좌표 변환
        processed = DetectionPreprocessor.convert_bbox_to_relative(detection_json)
        
        # 2. CCTV 메타데이터에서 FOV 정보 가져오기
        camera_lat = cctv_metadata["lat"]
        camera_lon = cctv_metadata["lon"]
        direction = cctv_metadata["direction"]
        fov_angle = cctv_metadata["angle"]
        fov_length = cctv_metadata["length"]
        
        # 3. 각 탐지에 대해 지리적 위치 계산
        geo_detections = []
        for detection in processed:
            u, v = detection["pos"]
            
            # 상대좌표를 실제 지리적 위치로 변환
            dx, dy = FovService.compute_world_offset(u, v, fov_angle, fov_length, direction)
            lat, lon = FovService.compute_lat_lon(camera_lat, camera_lon, dx, dy)
            
            geo_detections.append({
                **detection,
                "geo_pos": [lat, lon],
                "world_offset": [dx, dy]
            })
        
        return geo_detections
    
    @staticmethod
    def compute_world_offset(u: float, v: float, fov_angle: float, fov_length: float, direction: float) -> Tuple[float, float]:
        """상대좌표를 실제 거리로 변환"""
        # FOV 중심에서의 오프셋 계산
        angle_offset = (u - 0.5) * fov_angle
        distance = v * fov_length * 1000  # km를 m로 변환
        
        # 실제 방향 계산 (카메라 방향 + 각도 오프셋)
        actual_bearing = direction + angle_offset
        
        # 극좌표를 직교좌표로 변환
        dx = distance * math.sin(math.radians(actual_bearing))
        dy = distance * math.cos(math.radians(actual_bearing))
        
        return dx, dy
    
    @staticmethod
    def compute_lat_lon(center_lat: float, center_lon: float, dx: float, dy: float) -> Tuple[float, float]:
        """거리 오프셋을 위도/경도로 변환"""
        earth_radius = 6371000  # 지구 반지름 (미터)
        
        d_lat = dy / earth_radius
        d_lon = dx / (earth_radius * math.cos(math.radians(center_lat)))
        
        new_lat = center_lat + math.degrees(d_lat)
        new_lon = center_lon + math.degrees(d_lon)
        
        return new_lat, new_lon
