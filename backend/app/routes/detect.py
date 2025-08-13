# detect.py
from fastapi import APIRouter, HTTPException, File, UploadFile
from datetime import datetime
from ..db import db
from ..models import Detection, DetectionCSV, DetectionBatch, Result
from app.ws_manager import manager
from bson import ObjectId
import logging
import base64
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# 이미지 저장 디렉토리
STATIC_DIR = "app/static/frames"
os.makedirs(STATIC_DIR, exist_ok=True)

def calculate_risk(confidence: float) -> str:
    """신뢰도 기반 위험도 계산"""
    if confidence >= 0.8:
        return "red"
    elif confidence >= 0.6:
        return "orange"
    elif confidence >= 0.4:
        return "yellow"
    else:
        return "green"

@router.post(
    "/detect/csv",
    response_model=Result,
    summary="CSV 형식 탐지 결과 수신 (AI 모델용)"
)
async def ingest_csv_detection(detection: DetectionCSV):
    """
    CSV 형식의 탐지 결과를 받아서 처리
    - AI 모델에서 직접 사용할 수 있는 형식
    - detection_results.csv와 동일한 구조
    """
    try:
        # cctv_id가 없으면 이미지명에서 추출 시도
        if not detection.cctv_id:
            # 이미지명에서 카메라 정보 추출 (예: D01_... -> camera_01)
            if detection.image_name.startswith("D01_"):
                detection.cctv_id = "camera_01"
            elif detection.image_name.startswith("D02_"):
                detection.cctv_id = "camera_02"
            else:
                detection.cctv_id = "unknown"
        
        # captured_at이 없으면 현재 시간 사용
        if not detection.captured_at:
            detection.captured_at = datetime.now()
        
        # DB에 저장할 데이터 준비
        detection_data = {
            "cctv_id": detection.cctv_id,
            "bbox": [detection.x1, detection.y1, detection.x2, detection.y2],
            "pos": [detection.center_x, detection.center_y],
            "risk": calculate_risk(detection.confidence),
            "confidence": detection.confidence,
            "captured_at": detection.captured_at,
            "frame_url": f"/frames/{detection.image_name}",
            "image_name": detection.image_name,
            "image_path": detection.image_path,
            "bird_count": 1,
            "object_id": detection.object_id,
            "class_name": detection.class_name,
            "width": detection.width,
            "height": detection.height
        }

        # 1) DB 저장
        col_name = f"detections_{detection.captured_at:%Y%m}"
        col = db[col_name]
        result = await col.insert_one(detection_data)

        # 2) WS 브로드캐스트 (ObjectId를 문자열로 변환)
        ws_data = detection_data.copy()
        ws_data["_id"] = str(result.inserted_id)  # ObjectId를 문자열로 변환
        if "captured_at" in ws_data and hasattr(ws_data["captured_at"], "isoformat"):
            ws_data["captured_at"] = ws_data["captured_at"].isoformat()
        await manager.broadcast(ws_data)

        # 3) 성공 응답
        return Result(ok=True, error=None)

    except Exception as exc:
        logger.error(f"Failed to ingest CSV detection: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="CSV 탐지 결과를 처리하지 못했습니다."
        )

@router.post(
    "/detect/batch",
    response_model=Result,
    summary="다중 탐지 결과 일괄 처리"
)
async def ingest_batch_detections(batch: DetectionBatch):
    """
    여러 탐지 결과를 한 번에 처리
    - 한 이미지에서 여러 새가 탐지된 경우
    """
    try:
        if not batch.captured_at:
            batch.captured_at = datetime.now()
        
        col_name = f"detections_{batch.captured_at:%Y%m}"
        col = db[col_name]
        
        # 각 탐지 결과를 처리
        for detection in batch.detections:
            detection_data = {
                "cctv_id": batch.cctv_id,
                "bbox": [detection.x1, detection.y1, detection.x2, detection.y2],
                "pos": [detection.center_x, detection.center_y],
                "risk": calculate_risk(detection.confidence),
                "confidence": detection.confidence,
                "captured_at": batch.captured_at,
                "frame_url": f"/frames/{detection.image_name}",
                "image_name": detection.image_name,
                "image_path": detection.image_path,
                "bird_count": 1,
                "object_id": detection.object_id,
                "class_name": detection.class_name,
                "width": detection.width,
                "height": detection.height
            }
            
            # DB 저장
            result = await col.insert_one(detection_data)
            
            # WS 브로드캐스트 (ObjectId를 문자열로 변환)
            ws_data = detection_data.copy()
            ws_data["_id"] = str(result.inserted_id)
            if "captured_at" in ws_data and hasattr(ws_data["captured_at"], "isoformat"):
                ws_data["captured_at"] = ws_data["captured_at"].isoformat()
            await manager.broadcast(ws_data)
        
        return Result(ok=True, error=None)
        
    except Exception as exc:
        logger.error(f"Failed to ingest batch detections: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="일괄 탐지 결과를 처리하지 못했습니다."
        )

@router.post(
    "/detect/result",
    response_model=Result,
    summary="탐지 결과 수신 → DB 저장 → WS 브로드캐스트"
)
async def ingest(det: Detection):
    """
    - det: Pydantic Detection 모델
    - DB 컬렉션명: detections_YYYYMM
    """
    try:
        # 이미지 저장 처리
        frame_url = None
        if det.image_data:
            # base64 이미지 디코딩 및 저장
            image_bytes = base64.b64decode(det.image_data)
            timestamp = det.captured_at.strftime("%Y%m%d_%H%M%S")
            filename = f"{det.cctv_id}_{timestamp}.jpg"
            filepath = os.path.join(STATIC_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            frame_url = f"/static/frames/{filename}"
        
        # DB에 저장할 데이터 준비
        detection_data = {
            "cctv_id": det.cctv_id,
            "bbox": det.bbox,
            "pos": det.pos,  # property로 자동 계산
            "risk": det.risk,  # property로 자동 계산
            "confidence": det.confidence,
            "captured_at": det.captured_at,
            "frame_url": frame_url,
            "image_name": det.image_name,
            "bird_count": det.bird_count
        }

        # 1) DB 저장
        col_name = f"detections_{det.captured_at:%Y%m}"
        col = db[col_name]
        await col.insert_one(detection_data)

        # 2) WS 브로드캐스트 (image_data 제외하고 전송)
        ws_data = detection_data.copy()
        if "image_data" in ws_data:
            del ws_data["image_data"]
        await manager.broadcast(ws_data)

        # 3) 성공 응답
        return Result(ok=True, error=None)

    except Exception as exc:
        # 에러 로깅
        logger.error(f"Failed to ingest detection: {exc}", exc_info=True)
        # HTTP 500 반환
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류로 탐지 결과를 처리하지 못했습니다."
        )

# 수정된 get_history 엔드포인트: 모든 detections_ 컬렉션을 조회해서 결과를 합쳐 반환
@router.get("/detect/history/{cctv_id}")
async def get_history(cctv_id: str):
    try:
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
        docs.sort(key=lambda d: d.get("captured_at", ""), reverse=True)
        return docs
    except Exception as exc:
        logger.error(f"Failed to get history for {cctv_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="탐지 내역을 조회하지 못했습니다."
        )
