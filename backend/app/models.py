# models.py - 간소화된 모델
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 단일 탐지 결과 모델 (모든 형식 통합)
class Detection(BaseModel):
    """탐지 결과 - 모든 입력 형식을 지원하는 통합 모델"""
    # 필수 필드
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    
    # 메타데이터
    cctv_id: Optional[str] = None
    captured_at: Optional[datetime] = None
    image_name: Optional[str] = None
    
    # 추가 정보 (선택적)
    object_id: Optional[int] = None
    class_name: str = "bird"
    
    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2
    
    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2
    
    @property
    def risk(self) -> str:
        # 새로운 위험도 계산 기준 적용
        if self.confidence < 0.30:  # 30% 미만
            return "yellow"  # 모니터링 대상
        else:
            return "orange"  # 주의 필요

# 다중 탐지 결과
class DetectionBatch(BaseModel):
    detections: List[Detection]
    cctv_id: str
    captured_at: Optional[datetime] = None

# API 응답
class Result(BaseModel):
    ok: bool
    error: Optional[str] = None

# CCTV 메타데이터
class CctvMeta(BaseModel):
    id: str
    name: str
    pos: List[float]
    direction: float
    angle: float
    length: float
    color: Optional[str] = None
