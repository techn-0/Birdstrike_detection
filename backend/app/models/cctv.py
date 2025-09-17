# models/cctv.py
from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime


class FovAngle(BaseModel):
    direction: float # 방향 각도 (0-360도) 0: 동쪽, 90: 북쪽, 180: 서쪽, 270: 남쪽
    angle: float # 시야각 (0-180도)
    length: float # 거리

class DetectionObject(BaseModel):
    """개별 탐지 객체"""
    object_id: int
    class_name: str = "bird"
    confidence: float
    bbox: List[float]  # [x, y, w, h]
    pos: List[float]   # [u, v]

class Detection(BaseModel):
    cctv_id: str
    bbox: List[float]     # [x, y, w, h]
    pos: List[float]      # [u, v]
    risk: Literal["red", "orange", "yellow", "green"]
    captured_at: datetime
    frame_url: Optional[str]
    fov: Optional[FovAngle] = None  # ← 이렇게 하면 fov 없이도 탐지 결과 저장 가능
    bird_count: int = 1   # 새 마리 수 기본값 1로 추가
    # 다중 객체 지원 추가
    objects: Optional[List[DetectionObject]] = None  # 개별 객체들


class Result(BaseModel):
    ok: bool
    error: Optional[str] = None
    message: Optional[str] = None


class CctvMeta(BaseModel):
    id: str
    name: str
    pos: list[float]  # [u, v]
    direction: float
    angle: float
    length: float
    color: Optional[str] = None   # 색상 필드 추가
    sensor_size: Optional[List[float]] = None  # 센서 크기 [가로, 세로] (mm)
    resolution: Optional[List[int]] = None     # 해상도 [가로, 세로]
    focal_length: Optional[float] = None       # 초점거리 (mm)
    sensor_diagonal: Optional[float] = None    # 센서 대각선 길이 (mm)
    crop_factor: Optional[float] = None        # 크롭팩터
    model_name: Optional[str] = None           # 모델명
    is_photo_slides: bool = False              # 사진 슬라이드 활성화 여부
