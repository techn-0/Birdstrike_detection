# models.py
from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime

class FovAngle(BaseModel):
    direction: float # 방향 각도 (0-360도) 0: 동쪽, 90: 북쪽, 180: 서쪽, 270: 남쪽
    angle: float # 시야각 (0-180도)
    length: float # 거리

class Detection(BaseModel):
    cctv_id: str
    bbox: List[float]     # [x1, y1, x2, y2] - CSV 형식에 맞춤
    confidence: float     # 0.0 ~ 1.0
    captured_at: datetime
    image_name: Optional[str] = None  # 이미지 파일명
    image_data: Optional[str] = None  # base64 인코딩된 이미지 (작은 이미지용)
    bird_count: int = 1   # 새 마리 수
    
    # 자동 계산되는 필드들
    @property
    def pos(self) -> List[float]:
        """bbox에서 중심점 계산 - CSV 형식 [x1, y1, x2, y2]"""
        if len(self.bbox) == 4:
            x1, y1, x2, y2 = self.bbox
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            return [center_x, center_y]
        return [0, 0]
    
    @property
    def width_height(self) -> List[float]:
        """bbox에서 너비, 높이 계산"""
        if len(self.bbox) == 4:
            x1, y1, x2, y2 = self.bbox
            width = x2 - x1
            height = y2 - y1
            return [width, height]
        return [0, 0]
    
    @property
    def risk(self) -> str:
        """confidence 기반 위험도 자동 계산"""
        if self.confidence >= 0.8:
            return "red"
        elif self.confidence >= 0.6:
            return "orange"
        elif self.confidence >= 0.4:
            return "yellow"
        else:
            return "green"

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
