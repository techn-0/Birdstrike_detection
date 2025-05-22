# detect.py
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..db import db
from ..models import Detection, Result
from app.ws_manager import manager

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
