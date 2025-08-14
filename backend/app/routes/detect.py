# detect.py - 간소화된 탐지 API
from fastapi import APIRouter, HTTPException
from ..models.cctv import Detection, DetectionBatch, Result
from ..services.detection_service import DetectionService
from ..db import db
from bson import ObjectId
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

# 기존 경로와의 호환성을 위한 별칭
@router.post("/detect/result", response_model=Result)
async def detect_result(detection: Detection):
    """탐지 결과 처리 - 기존 경로 호환성"""
    return await detect(detection)

@router.post("/detect/batch", response_model=Result)
async def detect_batch(batch: DetectionBatch):
    """여러 탐지 결과 일괄 처리"""
    try:
        for csv_detection in batch.detections:
            # DetectionCSV를 Detection으로 변환
            detection = DetectionService.csv_to_detection(csv_detection, batch.cctv_id)
            
            await DetectionService.process_detection(detection)
        
        return Result(ok=True)
    except Exception as exc:
        logger.error(f"Batch detection failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="일괄 탐지 결과 처리 실패")

@router.get("/detect/history/{cctv_id}")
async def get_history(cctv_id: str):
    """특정 CCTV의 탐지 내역 조회"""
    try:
        # MongoDB에서 모든 detections_ 컬렉션을 조회
        all_collections = await db.list_collection_names()
        detection_cols = [name for name in all_collections if name.startswith("detections_")]
        
        docs = []
        for col_name in detection_cols:
            col = db[col_name]
            results = await col.find({"cctv_id": cctv_id}).to_list(None)
            for d in results:
                # ObjectId를 문자열로 변환
                if "_id" in d and isinstance(d["_id"], ObjectId):
                    d["_id"] = str(d["_id"])
                # captured_at이 datetime이면 ISO 문자열로 변환
                if "captured_at" in d and hasattr(d["captured_at"], "isoformat"):
                    d["captured_at"] = d["captured_at"].isoformat()
            docs.extend(results)
        
        # 시간 순으로 정렬 (최신 순)
        docs.sort(key=lambda d: d.get("captured_at", ""), reverse=True)
        return docs
    except Exception as exc:
        logger.error(f"Failed to get history for {cctv_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="탐지 내역을 조회하지 못했습니다.")
