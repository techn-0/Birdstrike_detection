from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime


class FovAngle(BaseModel):
    direction: float # 방향 각도 (0-360도) 0: 동쪽, 90: 북쪽, 180: 서쪽, 270: 남쪽
    angle: float # 시야각 (0-180도)
    length: float # 거리


class Detection(BaseModel):
    cctv_id: str
    bbox: List[float]     # [x, y, w, h]
    pos: List[float]      # [u, v]
    risk: Literal["red", "orange", "yellow", "green"]
    captured_at: datetime
    frame_url: Optional[str]
    fov: Optional[FovAngle] = None  # ← 이렇게 하면 fov 없이도 탐지 결과 저장 가능
    bird_count: int = 1   # 새 마리 수 기본값 1로 추가


class Result(BaseModel):
    ok: bool
    error: Optional[str] = None


class CctvMeta(BaseModel):
    id: str
    name: str
    pos: list[float]  # [u, v]
    direction: float
    angle: float
    length: float
    color: Optional[str] = None   # 색상 필드 추가
