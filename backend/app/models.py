# models.py
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

class FovAngle(BaseModel):
    direction: float # 방향 각도 (0-360도) 0: 동쪽, 90: 북쪽, 180: 서쪽, 270: 남쪽
    angle: float # 시야각 (0-180도)
    length: float # 거리

# CSV 형식에 맞는 탐지 결과 모델
class DetectionCSV(BaseModel):
    """CSV 탐지 결과 형식 - 실제 AI 모델에서 제공하는 데이터"""
    image_index: int
    image_path: str
    image_name: str
    object_id: int
    class_name: str = "bird"
    class_id: int = 0
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    width: float
    height: float
    center_x: float
    center_y: float
    
    # 추가 메타데이터 (API에서 보충)
    cctv_id: Optional[str] = None
    captured_at: Optional[datetime] = None

# 기존 Detection 모델 (하위 호환성 유지)
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

# 다중 탐지 결과 (CSV에서 여러 개 객체 포함 가능)
class DetectionBatch(BaseModel):
    """여러 탐지 결과를 한 번에 처리"""
    detections: List[DetectionCSV]
    cctv_id: str
    captured_at: Optional[datetime] = None

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
