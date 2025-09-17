# detect.py - 간소화된 탐지 API
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from ..models.cctv import Detection, DetectionObject, Result
from ..services.detection_service import DetectionService
from ..db import db
from bson import ObjectId
import logging
import os
import uuid
import shutil
from pathlib import Path
from typing import List

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

@router.post("/detect/objects", response_model=Result)
async def detect_objects(objects: List[DetectionObject], cctv_id: str, frame_url: str):
    """다중 객체 탐지 결과 처리"""
    detection = DetectionService.csv_batch_to_detection(objects, cctv_id, frame_url)
    await DetectionService.process_detection(detection)
    return Result(ok=True)

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


@router.post("/detect/airbirds", response_model=Result)
async def detect_airbirds(detection_data: dict):
    """AirBirds 형식 탐지 결과 처리"""
    try:
        from ..services.fov_service import FovService
        from ..db import db
        
        # CCTV ID 추출
        cctv_id = detection_data.get("image_name", "").split("_")[0] if detection_data.get("image_name") else "D02"
        
        # CCTV 메타데이터 조회
        cctv_meta = await db.cctv.find_one({"id": cctv_id})
        if not cctv_meta:
            # 기본 CCTV 메타데이터 (테스트용)
            cctv_meta = {
                "id": cctv_id,
                "lat": 34.8423,  # 여수공항 좌표
                "lon": 127.6169,
                "direction": 0,   # 동쪽 방향
                "angle": 60,      # 60도 시야각
                "length": 2       # 2km 거리
            }
        else:
            # 데이터베이스 형식을 FovService가 기대하는 형식으로 변환
            if "pos" in cctv_meta and isinstance(cctv_meta["pos"], list) and len(cctv_meta["pos"]) >= 2:
                cctv_meta["lat"] = cctv_meta["pos"][0]
                cctv_meta["lon"] = cctv_meta["pos"][1]
            else:
                # pos가 없거나 형식이 다르면 기본값 사용
                cctv_meta["lat"] = 34.8423
                cctv_meta["lon"] = 127.6169
            
            # 필수 필드들이 없으면 기본값 설정
            if "direction" not in cctv_meta:
                cctv_meta["direction"] = 0
            if "angle" not in cctv_meta:
                cctv_meta["angle"] = 60
            if "length" not in cctv_meta:
                cctv_meta["length"] = 2
        
        # AirBirds 탐지 결과를 지리적 좌표로 변환
        geo_detections = FovService.process_airbirds_detection(detection_data, cctv_meta)
        
        # 변환된 결과를 기존 Detection 형식으로 저장
        for geo_detection in geo_detections:
            from datetime import datetime
            import re
            
            # 타임스탬프 파싱 개선
            timestamp_str = geo_detection["timestamp"]
            try:
                # Z를 제거하고 datetime 파싱
                if timestamp_str.endswith("Z"):
                    timestamp_str = timestamp_str[:-1] + "+00:00"
                captured_at = datetime.fromisoformat(timestamp_str)
            except Exception as dt_error:
                logger.warning(f"Timestamp parsing failed: {dt_error}, using current time")
                captured_at = datetime.now()
            
            detection = Detection(
                cctv_id=geo_detection["cctv_id"],
                bbox=[
                    geo_detection["original_bbox"]["x1"],
                    geo_detection["original_bbox"]["y1"],
                    geo_detection["original_bbox"]["x2"] - geo_detection["original_bbox"]["x1"],
                    geo_detection["original_bbox"]["y2"] - geo_detection["original_bbox"]["y1"]
                ],
                pos=geo_detection["pos"],
                risk="yellow" if geo_detection["confidence"] > 0.3 else "green",
                captured_at=captured_at,
                frame_url=None  # AirBirds 데이터에는 이미지 URL이 없으므로 None
            )
            
            await DetectionService.process_detection(detection)
        
        return Result(ok=True, message=f"{len(geo_detections)}개의 새 탐지 결과가 처리되었습니다.")
        
    except Exception as exc:
        logger.error(f"AirBirds detection failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="AirBirds 탐지 결과 처리 실패")
