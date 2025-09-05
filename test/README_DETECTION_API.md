# 🔍 조류 탐지 결과 전송 API 가이드

## 📋 개요
이 문서는 조류 탐지 모델 팀이 탐지 결과를 백엔드 서버로 전송하는 방법을 설명합니다.  
CSV 형태의 탐지 결과와 이미지를 함께 전송하여 프론트엔드에서 실시간으로 확인할 수 있습니다.

## 🎯 대상 독자
- 조류 탐지 AI 모델 개발팀
- 탐지 결과 전송 담당자
- API 통합 개발자

## 📁 프로젝트 구조
```
test/
├── detection_results.csv      # 탐지 결과 CSV 파일
├── detection_image/           # 탐지된 이미지 파일들
│   ├── D02_20210628090856_0000714_crop_000.png
│   ├── D02_20210721142744_0001120_crop_007.png
│   └── ...
├── csv_detection_test.py      # 테스트 실행 스크립트
└── README_DETECTION_API.md    # 이 문서
```

## 🚀 빠른 시작

### 1. 환경 준비
```bash
# 1. 백엔드 서버 실행 (포트 8000)
# 2. 프론트엔드 실행 (포트 3000)
# 3. 테스트 디렉토리로 이동
cd test
```

### 2. 테스트 실행
```bash
# 전체 CSV 데이터를 DB로 전송
python csv_detection_test.py
```

### 3. 결과 확인
- 브라우저에서 `http://localhost:3000` 접속
- CCTV 목록에서 탐지 결과 확인

## 📊 CSV 데이터 형식

### detection_results.csv 구조
```csv
image_index,image_path,image_name,object_id,class_name,class_id,x1,y1,x2,y2,confidence,width,height,center_x,center_y
0,path/to/image.png,D02_20210628090856_0000714_crop_000.png,0,bird,0,508.83,534.93,524.51,543.12,0.272,15.68,8.19,516.67,539.02
```

### 필수 필드 설명
| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `image_name` | string | 이미지 파일명 | `D02_20210628090856_0000714_crop_000.png` |
| `confidence` | float | 탐지 신뢰도 (0.0~1.0) | `0.272` |
| `x1, y1` | float | 바운딩박스 좌상단 좌표 | `508.83, 534.93` |
| `x2, y2` | float | 바운딩박스 우하단 좌표 | `524.51, 543.12` |
| `width, height` | float | 바운딩박스 크기 | `15.68, 8.19` |
| `center_x, center_y` | float | 객체 중심점 좌표 | `516.67, 539.02` |

## 🏷️ CCTV ID 매핑 규칙

현재 테스트에서 사용하는 CCTV ID 매핑:

```python
def extract_cctv_id_from_image_name(image_name: str) -> str:
    if "20210628" in image_name:
        return "AIRPORT_CAM_D02_A"  # 2021년 6월 28일 데이터
    elif "20210721" in image_name:
        return "AIRPORT_CAM_D02_B"  # 2021년 7월 21일 데이터
    else:
        return "AIRPORT_CAM_D02_DEFAULT"  # 기본값
```

### 📝 CCTV ID 추가 방법
새로운 카메라를 추가하려면:

1. **이미지 파일명 패턴 확인**
   ```
   D03_20210801120000_0001234_crop_001.png  # D03 카메라, 8월 1일
   ```

2. **매핑 함수 수정**
   ```python
   def extract_cctv_id_from_image_name(self, image_name: str) -> str:
       if "20210628" in image_name:
           return "AIRPORT_CAM_D02_A"
       elif "20210721" in image_name:
           return "AIRPORT_CAM_D02_B"
       elif "D03_" in image_name and "20210801" in image_name:
           return "AIRPORT_CAM_D03_A"  # 새로운 카메라 추가
       else:
           return "AIRPORT_CAM_D02_DEFAULT"
   ```

## 🔗 API 엔드포인트

### 1. 개별 탐지 결과 전송
**POST** `/detect/result`

실시간으로 탐지 결과를 하나씩 전송할 때 사용

```python
import requests

detection_data = {
    "cctv_id": "AIRPORT_CAM_D02_A",
    "bbox": [508.83, 534.93, 15.68, 8.19],  # [x, y, width, height]
    "pos": [516.67, 539.02],                # [center_x, center_y]
    "risk": "green",                        # 신뢰도 기반 위험도
    "captured_at": "2025-08-25T07:00:00Z",  # ISO 8601 형식
    "frame_url": "/frames/uploaded_image.png",
    "bird_count": 1
}

response = requests.post(
    "http://localhost:8000/detect/result",
    json=detection_data
)
```

### 2. 배치 탐지 결과 전송
**POST** `/detect/batch`

여러 탐지 결과를 한 번에 전송할 때 사용

```python
batch_data = {
    "detections": [
        {
            "image_name": "D02_20210628090856_0000714_crop_000.png",
            "confidence": 0.272,
            "x1": 508.83, "y1": 534.93,
            "x2": 524.51, "y2": 543.12,
            "width": 15.68, "height": 8.19,
            "center_x": 516.67, "center_y": 539.02,
            # ... 더 많은 필드
        }
    ],
    "cctv_id": "AIRPORT_CAM_D02_A",
    "captured_at": "2025-08-25T07:00:00Z"
}

response = requests.post(
    "http://localhost:8000/detect/batch",
    json=batch_data
)
```

### 3. 이미지 업로드
**POST** `/upload/image`

탐지된 이미지를 서버에 업로드

```python
with open("detection_image.png", "rb") as f:
    files = {"file": ("image.png", f, "image/png")}
    response = requests.post(
        "http://localhost:8000/upload/image",
        files=files
    )
    
# 응답에서 이미지 URL 추출
if response.status_code == 200:
    result = response.json()
    image_url = result["url"]  # "/frames/uuid-generated-name.png"
```

### 4. 탐지 내역 조회
**GET** `/detect/history/{cctv_id}`

특정 CCTV의 탐지 기록 조회

```python
response = requests.get(
    "http://localhost:8000/detect/history/AIRPORT_CAM_D02_A"
)
detections = response.json()
```

## ⚠️ 위험도 자동 분류

신뢰도(confidence)에 따라 위험도가 자동으로 설정됩니다:

| 신뢰도 범위 | 위험도 | 색상 | 의미 |
|-------------|--------|------|------|
| 0.8 ~ 1.0 | `red` | 🔴 | 고위험 (즉시 경보) |
| 0.6 ~ 0.8 | `orange` | 🟠 | 중위험 (주의 필요) |
| 0.4 ~ 0.6 | `yellow` | 🟡 | 저위험 (모니터링) |
| 0.0 ~ 0.4 | `green` | 🟢 | 매우 저위험 (참고용) |

```python
def get_risk_level(confidence: float) -> str:
    if confidence >= 0.8:
        return "red"
    elif confidence >= 0.6:
        return "orange"
    elif confidence >= 0.4:
        return "yellow"
    else:
        return "green"
```

## 🔧 실제 모델 통합 예시

### Python 코드 예시
```python
import requests
from datetime import datetime, timezone
from pathlib import Path

class BirdDetectionAPI:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
    
    def send_detection(self, image_path, bbox, confidence, cctv_id):
        """탐지 결과 전송"""
        # 1. 이미지 업로드
        frame_url = self.upload_image(image_path)
        if not frame_url:
            return False
        
        # 2. 위험도 계산
        risk = self.calculate_risk(confidence)
        
        # 3. 탐지 결과 데이터 구성
        detection_data = {
            "cctv_id": cctv_id,
            "bbox": bbox,  # [x, y, width, height]
            "pos": [bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2],  # 중심점
            "risk": risk,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": frame_url,
            "bird_count": 1
        }
        
        # 4. API 호출
        response = requests.post(
            f"{self.server_url}/detect/result",
            json=detection_data
        )
        
        return response.status_code == 200
    
    def upload_image(self, image_path):
        """이미지 업로드"""
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/png')}
            response = requests.post(
                f"{self.server_url}/upload/image",
                files=files
            )
        
        if response.status_code == 200:
            return response.json()["url"]
        return None
    
    def calculate_risk(self, confidence):
        """신뢰도 기반 위험도 계산"""
        if confidence >= 0.8:
            return "red"
        elif confidence >= 0.6:
            return "orange"
        elif confidence >= 0.4:
            return "yellow"
        else:
            return "green"

# 사용 예시
api = BirdDetectionAPI()

# 탐지 결과 전송
success = api.send_detection(
    image_path="detected_bird.png",
    bbox=[100, 150, 50, 30],  # [x, y, width, height]
    confidence=0.85,
    cctv_id="AIRPORT_CAM_D02_A"
)

if success:
    print("✅ 탐지 결과 전송 성공")
else:
    print("❌ 탐지 결과 전송 실패")
```

## 📱 프론트엔드 확인 방법

### 1. 웹 인터페이스 접속
- URL: `http://localhost:3000`
- 오른쪽 사이드패널에서 CCTV 목록 확인

### 2. 탐지 결과 확인
1. **CCTV 목록**에서 원하는 카메라 클릭
2. **탐지 내역 모달**에서 다음 정보 확인:
   - 탐지 시간
   - 위험도 (색상으로 표시)
   - 탐지된 조류 수
   - 탐지 이미지

### 3. 지도에서 실시간 확인
- 지도상의 CCTV 마커 색상이 최근 탐지 위험도를 반영
- 탐지 발생 시 해당 위치에 위험도 마커 표시

## 🚨 문제해결

### 자주 발생하는 오류

#### 1. 서버 연결 실패
```
❌ 서버 연결 오류: Connection refused
```
**해결방법:**
- 백엔드 서버가 실행 중인지 확인
- 포트 8000이 사용 가능한지 확인

#### 2. 이미지 업로드 실패
```
❌ 이미지 업로드 실패: 422 - Field required
```
**해결방법:**
- 이미지 파일 경로 확인
- 파일 권한 확인
- 지원되는 이미지 형식: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`

#### 3. CSV 파일 로딩 실패
```
❌ CSV 파일을 찾을 수 없습니다
```
**해결방법:**
- `detection_results.csv` 파일이 `test/` 디렉토리에 있는지 확인
- 파일 인코딩이 UTF-8인지 확인

### 로그 확인
```bash
# 백엔드 로그 확인
# 터미널에서 uvicorn 실행 시 실시간 로그 확인 가능

# 프론트엔드 로그 확인
# 브라우저 개발자도구 > Console 탭에서 확인
```