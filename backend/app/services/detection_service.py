# services/detection_service.py - 탐지 관련 비즈니스 로직 분리
from datetime import datetime
from ..db import db
from ..ws_manager import manager
from ..models import Detection
import logging

logger = logging.getLogger(__name__)

class DetectionService:
    @staticmethod
    def normalize_detection(detection: Detection) -> dict:
        """탐지 데이터를 DB 저장 형식으로 정규화"""
        # cctv_id 추론
        if not detection.cctv_id and detection.image_name:
            if detection.image_name.startswith("D01_"):
                detection.cctv_id = "camera_01"
            elif detection.image_name.startswith("D02_"):
                detection.cctv_id = "camera_02"
            else:
                detection.cctv_id = "unknown"
        
        # 시간 설정
        if not detection.captured_at:
            detection.captured_at = datetime.now()
        
        return {
            "cctv_id": detection.cctv_id,
            "bbox": [detection.x1, detection.y1, detection.x2, detection.y2],
            "pos": [detection.center_x, detection.center_y],
            "risk": detection.risk,
            "confidence": detection.confidence,
            "captured_at": detection.captured_at,
            "frame_url": f"/frames/{detection.image_name}" if detection.image_name else None,
            "image_name": detection.image_name,
            "object_id": detection.object_id,
            "class_name": detection.class_name
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
