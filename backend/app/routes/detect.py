# detect.py - 간소화된 탐지 API
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from ..models.cctv import Detection, DetectionBatch, Result
from ..services.detection_service import DetectionService
from ..db import db
from bson import ObjectId
import logging
import os
import uuid
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# 정적 파일 저장 경로
STATIC_DIR = Path("app/static/frames")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

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

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """
    이미지 파일 업로드 API
    
    Args:
        file: 업로드할 이미지 파일
    
    Returns:
        Dict: 업로드된 파일 정보 및 URL
    """
    try:
        # 파일 확장자 검증
        allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
            )
        
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = STATIC_DIR / unique_filename
        
        # 파일 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 파일 URL 생성
        file_url = f"/frames/{unique_filename}"
        
        logger.info(f"Image uploaded successfully: {unique_filename}")
        
        return {
            "ok": True,
            "filename": unique_filename,
            "original_filename": file.filename,
            "url": file_url,
            "size": file_path.stat().st_size
        }
        
    except Exception as exc:
        logger.error(f"Image upload failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="이미지 업로드에 실패했습니다.")

@router.post("/detect/with_image", response_model=Result)
async def detect_with_image(
    file: UploadFile = File(...),
    cctv_id: str = "camera_01",
    bbox: str = "[0,0,100,100]",
    pos: str = "[50,50]",
    risk: str = "green",
    bird_count: int = 1
):
    """
    이미지와 함께 탐지 결과 저장 API
    
    Args:
        file: 탐지 결과 이미지 파일
        cctv_id: 카메라 ID
        bbox: 바운딩 박스 (JSON 문자열)
        pos: 중심점 (JSON 문자열) 
        risk: 위험도
        bird_count: 조류 수
    
    Returns:
        Result: 처리 결과
    """
    try:
        # 이미지 업로드
        upload_result = await upload_image(file)
        
        if not upload_result["ok"]:
            raise HTTPException(status_code=500, detail="이미지 업로드 실패")
        
        # JSON 문자열 파싱
        import json
        bbox_list = json.loads(bbox)
        pos_list = json.loads(pos)
        
        # Detection 객체 생성
        from datetime import datetime
        detection = Detection(
            cctv_id=cctv_id,
            bbox=bbox_list,
            pos=pos_list,
            risk=risk,
            captured_at=datetime.now(),
            frame_url=upload_result["url"],
            bird_count=bird_count
        )
        
        # 탐지 결과 처리
        await DetectionService.process_detection(detection)
        
        return Result(ok=True)
        
    except Exception as exc:
        logger.error(f"Detection with image failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="이미지 포함 탐지 결과 처리 실패")
