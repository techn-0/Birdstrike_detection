import requests
from datetime import datetime, timezone

data = {
    "cctv_id": "cctv-1",  # 반드시 실제 등록된 CCTV id와 일치해야 함
    "bbox": [0.5, 0.5, 0.1, 0.1],  # 예시값 (정규화된 좌표)
    "pos": [0.5, 0.5],             # 예시값 (정규화된 중심 좌표)
    "risk": "green",                # 위험도 (red, orange, yellow, green 중 하나)
    "captured_at": datetime.now(timezone.utc).isoformat(),  # UTC 권장
    "frame_url": "/frames/result.png",          # 실제 서버에 있는 이미지 경로
    "bird_count": 1,                            # 새 마리
    # "fov": {"direction": 90, "angle": 100, "length": 1}  # 필요시 주석 해제
}

res = requests.post("http://localhost:8000/detect/result", json=data)
print(res.status_code, res.text)