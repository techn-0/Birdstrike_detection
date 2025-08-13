# detect.py - 간소화된 탐지 API
from fastapi import APIRouter, HTTPException
from ..models import Detection, DetectionBatch, Result
from ..services.detection_service import DetectionService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/detect", response_model=Result)
async def detect(detection: Detection):
    """탐지 결과 처리 - 모든 형식 지원"""
    try:
        await DetectionService.process_detection(detection)
        return Result(ok=True)
    except Exception as exc:
        logger.error(f"Detection failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="탐지 결과 처리 실패")

@router.post("/detect/batch", response_model=Result)
async def detect_batch(batch: DetectionBatch):
    """여러 탐지 결과 일괄 처리"""
    try:
        for detection in batch.detections:
            # batch 정보로 보완
            if not detection.cctv_id:
                detection.cctv_id = batch.cctv_id
            if not detection.captured_at:
                detection.captured_at = batch.captured_at
            
            await DetectionService.process_detection(detection)
        
        return Result(ok=True)
    except Exception as exc:
        logger.error(f"Batch detection failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="일괄 탐지 결과 처리 실패")
