# services/detection_service.py - 탐지 관련 비즈니스 로직 분리
from datetime import datetime
from ..db import db
from ..ws_manager import manager
from ..models.cctv import Detection, DetectionCSV
import logging

logger = logging.getLogger(__name__)

class DetectionService:
    @staticmethod
    def calculate_risk_by_count_and_confidence(bird_count: int, max_confidence: float = 0.0) -> str:
        """
        새로운 위험도 분류 기준:
        - Green: 객체 탐지 안됨 (bird_count = 0)
        - Yellow: 1개 객체 + confidence < 30%
        - Orange: 1개 객체 + confidence ≥ 30%
        - Red: 2개 이상의 조류 탐지
        """
        if bird_count == 0:
            return "green"  # 미탐지
        elif bird_count == 1:
            if max_confidence < 0.30:  # 30% 미만
                return "yellow"  # 모니터링 대상
            else:
                return "orange"  # 주의 필요
        else:  # bird_count >= 2
            return "red"  # 즉시 경보 필요

    @staticmethod
    def csv_to_detection(csv_detection: DetectionCSV, cctv_id: str = None) -> Detection:
        """DetectionCSV를 Detection 모델로 변환"""
        # bbox 배열 형식 [x1, y1, x2, y2]
        bbox = [csv_detection.x1, csv_detection.y1, csv_detection.x2, csv_detection.y2]
        
        # pos 배열 형식 [center_x, center_y]
        pos = [csv_detection.center_x, csv_detection.center_y]
        
        # risk 계산 (새로운 기준 적용)
        risk = DetectionService.calculate_risk_by_count_and_confidence(
            bird_count=1, 
            max_confidence=csv_detection.confidence
        )
        
        # frame_url 생성
        frame_url = f"/frames/{csv_detection.image_name}" if csv_detection.image_name else None
        
        # CCTV ID 결정
        final_cctv_id = csv_detection.cctv_id or cctv_id or "unknown"
        
        # 시간 설정
        captured_at = csv_detection.captured_at or datetime.now() 
        
        return Detection(
            cctv_id=final_cctv_id,
            bbox=bbox,
            pos=pos,
            risk=risk,
            captured_at=captured_at,
            frame_url=frame_url,
            bird_count=1
        )
    
    @staticmethod
    def normalize_detection(detection: Detection) -> dict:
        """탐지 데이터를 DB 저장 형식으로 정규화"""
        return {
            "cctv_id": detection.cctv_id,
            "bbox": detection.bbox,
            "pos": detection.pos,
            "risk": detection.risk,
            "captured_at": detection.captured_at,
            "frame_url": detection.frame_url,
            "fov": detection.fov.dict() if detection.fov else None,
            "bird_count": detection.bird_count
        }
    
    @staticmethod
    async def save_detection(detection_data: dict) -> str:
        """DB에 탐지 결과 저장"""
        col_name = f"detections_{detection_data['captured_at']:%Y%m}"
        col = db[col_name]
        result = await col.insert_one(detection_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def broadcast_detection(detection_data: dict, detection_id: str):
        """WebSocket으로 탐지 결과 브로드캐스트"""
        ws_data = detection_data.copy()
        ws_data["_id"] = detection_id
        if "captured_at" in ws_data and hasattr(ws_data["captured_at"], "isoformat"):
            ws_data["captured_at"] = ws_data["captured_at"].isoformat()
        await manager.broadcast(ws_data)
    
    @staticmethod
    async def process_detection(detection: Detection) -> str:
        """탐지 결과 전체 처리 플로우"""
        try:
            # 1. 데이터 정규화
            detection_data = DetectionService.normalize_detection(detection)
            
            # 2. DB 저장
            detection_id = await DetectionService.save_detection(detection_data)
            
            # 3. WS 브로드캐스트
            await DetectionService.broadcast_detection(detection_data, detection_id)
            
            return detection_id
        except Exception as exc:
            logger.error(f"Detection processing failed: {exc}", exc_info=True)
            raise
