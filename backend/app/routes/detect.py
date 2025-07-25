# detect.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..db import db
from ..models import Detection, Result
from app.ws_manager import manager
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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
        # 1) DB 저장
        col_name = f"detections_{det.captured_at:%Y%m}"
        col = db[col_name]
        await col.insert_one(det.dict())

        # 2) WS 브로드캐스트
        await manager.broadcast(det.dict())

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
