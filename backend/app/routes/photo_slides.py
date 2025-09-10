from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.photo_slides_service import photo_slides_service

router = APIRouter()

@router.get("/photo-slides/{cctv_id}")
async def get_photo_slides(
    cctv_id: str,
    confidence_threshold: float = Query(0.3, ge=0.0, le=1.0, description="최소 신뢰도 임계값")
):
    """
    특정 CCTV의 포토 슬라이드 데이터를 반환
    신뢰도가 낮은 이미지는 제외
    """
    return photo_slides_service.get_photo_slides_data(cctv_id, confidence_threshold)

@router.get("/photo-slides/stats")
async def get_photo_slides_statistics():
    """전체 이미지 통계 정보 반환"""
    return photo_slides_service.get_image_statistics()
