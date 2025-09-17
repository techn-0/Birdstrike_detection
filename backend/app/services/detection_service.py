# services/detection_service.py - 탐지 관련 비즈니스 로직 분리
from datetime import datetime
from ..db import db
from ..ws_manager import manager
from ..models.cctv import Detection, DetectionObject
from typing import List
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
    def csv_batch_to_detection(objects: List[DetectionObject], cctv_id: str, frame_url: str) -> Detection:
        # DetectionObject 리스트를 받아서 처리
        confidences = [obj.confidence for obj in objects]
        
        representative_bbox = objects[0].bbox if objects else [0, 0, 0, 0]
        representative_pos = objects[0].pos if objects else [0, 0]
        
        bird_count = len(objects)
        max_confidence = max(confidences) if confidences else 0.0
        risk = DetectionService.calculate_risk_by_count_and_confidence(bird_count, max_confidence)
        
        return Detection(
            cctv_id=cctv_id,
            bbox=representative_bbox,
            pos=representative_pos,
            risk=risk,
            captured_at=datetime.now(),
            frame_url=frame_url,
            bird_count=bird_count,
            objects=objects
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
            "bird_count": detection.bird_count,
            "objects": [obj.dict() for obj in detection.objects] if detection.objects else None
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
