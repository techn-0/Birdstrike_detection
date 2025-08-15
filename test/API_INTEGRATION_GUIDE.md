# 🚁 조류 탐지 API 통합 가이드

## 📋 개요
이 문서는 조류 탐지 모델 팀이 백엔드 API와 통합할 때 필요한 모든 정보를 제공합니다.

## 🎯 API 엔드포인트

### 1. 실시간 탐지 결과 저장
```http
POST /detect/result
Content-Type: application/json
```

**요청 데이터:**
```json
{
    "cctv_id": "airport_cam_01",           // 카메라 식별자
    "bbox": [100, 150, 100, 100],          // [x, y, width, height]
    "pos": [150, 200],                     // [center_x, center_y]
    "risk": "red",                         // red/orange/yellow/green
    "captured_at": "2025-08-15T12:34:56Z", // ISO 8601 형식
    "frame_url": "frames/frame_001.jpg",   // 프레임 이미지 URL
    "bird_count": 1                        // 탐지된 조류 수
}
```

**사용 시나리오:**
- 실시간 CCTV 모니터링
- 즉시 경보가 필요한 상황
- 스트리밍 처리 중 탐지 결과

### 2. 배치 탐지 결과 저장
```http
POST /detect/batch
Content-Type: application/json
```

**요청 데이터:**
```json
{
    "detections": [
        {
            "image_index": 1,
            "image_name": "frame_001.jpg",
            "x1": 100, "y1": 150, "x2": 200, "y2": 250,
            "confidence": 0.85,
            "class_name": "bird",
            "width": 100, "height": 100,
            "center_x": 150, "center_y": 200
        }
        // ... 더 많은 탐지 결과
    ],
    "cctv_id": "airport_cam_01",
    "captured_at": "2025-08-15T12:34:56Z"
}
```

**사용 시나리오:**
- 영상 파일 전체 분석 완료 후
- 오프라인 배치 처리 결과
- 대량의 과거 데이터 처리

### 3. 탐지 내역 조회
```http
GET /detect/history/{cctv_id}
Accept: application/json
```

**응답 데이터:**
```json
[
    {
        "id": "unique_detection_id",
        "cctv_id": "airport_cam_01",
        "bbox": [100, 150, 100, 100],
        "pos": [150, 200],
        "risk": "red",
        "captured_at": "2025-08-15T12:34:56Z",
        "frame_url": "frames/frame_001.jpg",
        "bird_count": 1,
        "created_at": "2025-08-15T12:34:57Z"
    }
]
```

## 🔧 Python 통합 예시

### 기본 설정
```python
import requests
from datetime import datetime, timezone

class BirdDetectionAPI:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
```

### 실시간 탐지 결과 전송
```python
def send_detection_result(self, detection_data):
    """실시간 탐지 결과 전송"""
    
    # API 형식으로 데이터 변환
    api_data = {
        "cctv_id": detection_data["camera_id"],
        "bbox": [
            detection_data["x"], 
            detection_data["y"], 
            detection_data["width"], 
            detection_data["height"]
        ],
        "pos": [
            detection_data["center_x"], 
            detection_data["center_y"]
        ],
        "risk": self.get_risk_level(detection_data["confidence"]),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "frame_url": detection_data["frame_path"],
        "bird_count": detection_data["bird_count"]
    }
    
    # API 호출
    response = self.session.post(
        f"{self.server_url}/detect/result",
        json=api_data
    )
    
    return response.status_code == 200

def get_risk_level(self, confidence):
    """신뢰도 기반 위험도 설정"""
    if confidence >= 0.8:
        return "red"      # 즉시 경보
    elif confidence >= 0.6:
        return "orange"   # 주의 필요
    elif confidence >= 0.4:
        return "yellow"   # 모니터링
    else:
        return "green"    # 참고용
```

### 배치 처리 결과 전송
```python
def send_batch_results(self, detection_list, cctv_id):
    """배치 탐지 결과 전송"""
    
    batch_data = {
        "detections": detection_list,
        "cctv_id": cctv_id,
        "captured_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = self.session.post(
        f"{self.server_url}/detect/batch",
        json=batch_data
    )
    
    return response.status_code == 200
```

## 📊 데이터 형식 가이드

### 바운딩 박스 형식
```python
# 입력: 탐지 모델 출력 (좌상단, 우하단)
x1, y1, x2, y2 = 100, 150, 200, 250

# 변환: API 형식 (좌상단, 폭, 높이)
bbox = [x1, y1, x2-x1, y2-y1]  # [100, 150, 100, 100]
```

### 중심점 계산
```python
center_x = x1 + (x2 - x1) / 2  # 150
center_y = y1 + (y2 - y1) / 2  # 200
pos = [center_x, center_y]     # [150, 200]
```

### 시간 형식
```python
from datetime import datetime, timezone

# UTC 시간으로 설정
captured_at = datetime.now(timezone.utc).isoformat()
# 결과: "2025-08-15T12:34:56.789123+00:00"
```

## ⚠️ 주의사항

### 1. 네트워크 처리
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 재시도 정책 설정
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)
```

### 2. 에러 처리
```python
try:
    response = session.post(api_url, json=data, timeout=10)
    response.raise_for_status()  # HTTP 에러 체크
    
    result = response.json()
    print(f"성공: {result}")
    
except requests.exceptions.Timeout:
    print("요청 시간 초과")
except requests.exceptions.ConnectionError:
    print("서버 연결 실패")
except requests.exceptions.HTTPError as e:
    print(f"HTTP 에러: {e}")
except Exception as e:
    print(f"알 수 없는 오류: {e}")
```

### 3. 성능 최적화
```python
# 실시간 처리시 비동기 전송 고려
import asyncio
import aiohttp

async def async_send_detection(session, data):
    async with session.post(api_url, json=data) as response:
        return await response.json()

# 배치 처리시 적절한 크기로 분할
def send_large_batch(detection_list, batch_size=100):
    for i in range(0, len(detection_list), batch_size):
        batch = detection_list[i:i + batch_size]
        send_batch_results(batch, cctv_id)
```

## 🧪 테스트 방법

### 1. 테스트 스크립트 실행
```bash
python storage_api_test.py
```

### 2. 개별 API 테스트
```python
from storage_api_test import DetectionStorageTester

tester = DetectionStorageTester("http://localhost:8000")

# 서버 연결 테스트
tester.test_server_connection()

# 샘플 데이터로 개별 API 테스트
sample_detection = tester.create_sample_detection("test.jpg", 0.85)
tester.test_individual_storage_api(sample_detection, "test_cam")
```