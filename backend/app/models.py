from pydantic import BaseModel, Field, Extra
from typing import List, Optional
from datetime import datetime

class Detection(BaseModel, extra=Extra.allow):   # 추가필드 허용!
    cctv_id: str
    bbox: List[float]            # [xc, yc, w, h] (0~1 비율)
    pos: List[float]             # [u, v] 지도 비율
    risk: str = "green"
    captured_at: datetime
    frame_url: Optional[str]
