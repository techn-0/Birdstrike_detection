# models.py
from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime

class Detection(BaseModel):
    cctv_id: str
    bbox: List[float]     # [x, y, w, h]
    pos: List[float]      # [u, v]
    risk: Literal["red", "orange", "yellow", "green"]
    captured_at: datetime
    frame_url: Optional[str]

class Result(BaseModel):
    ok: bool
    error: Optional[str] = None
