# 🚁 조류 탐지 시스템 - 외부 모델 테스트 가이드

이 폴더에는 외부 AI 모델에서 조류 탐지 결과를 백엔드 서버로 전송하는 테스트 스크립트들이 포함되어 있습니다.

## 📁 파일 구성

### 1. `simple_test_client.py` - 간단한 테스트
가장 기본적인 테스트 스크립트입니다. AI 모델 개발자가 처음 연동을 확인할 때 사용하세요.

**특징:**
- 최소한의 코드로 구성
- 하드코딩된 테스트 데이터 사용
- 기본적인 연동 확인

### 2. `test_external_model.py` - 고급 시뮬레이터
실제 AI 모델의 동작을 시뮬레이션하는 고급 테스트 도구입니다.

**특징:**
- 실제와 유사한 탐지 결과 생성
- 더미 이미지 생성 및 전송
- 다양한 테스트 시나리오 제공
- 인터랙티브 메뉴

### 3. `csv_test_client.py` - CSV 데이터 전송
실제 CSV 탐지 결과 파일을 사용하여 대량 데이터를 전송합니다.

**특징:**
- 실제 `detection_results.csv` 파일 사용
- 대량 데이터 전송 테스트
- 전송 속도 조절 가능

## 🚀 사용 방법

### 1단계: 백엔드 서버 실행
먼저 조류 탐지 백엔드 서버가 실행되고 있어야 합니다.

```bash
cd d:\Birdstrike_detection\backend
# Docker로 실행하거나
docker-compose up

# 또는 직접 실행
python -m uvicorn app.main:app --reload
```

### 2단계: 테스트 스크립트 실행

#### 간단한 테스트 (추천: 처음 시작하는 경우)
```bash
python simple_test_client.py
```

#### 고급 시뮬레이터 (추천: 다양한 시나리오 테스트)
```bash
# OpenCV 설치 필요
pip install opencv-python

python test_external_model.py
```

#### CSV 데이터 테스트 (추천: 실제 데이터 사용)
```bash
# detection_results.csv 파일을 같은 폴더에 복사 후 실행
python csv_test_client.py
```

## 📋 API 요청 형식

실제 AI 모델에서 사용해야 할 API 요청 형식입니다:

```python
import requests
from datetime import datetime

# 탐지 결과 데이터
detection_data = {
    "cctv_id": "camera_01",           # 카메라 ID
    "bbox": [x1, y1, x2, y2],        # 바운딩 박스 (좌상단, 우하단 좌표)
    "confidence": 0.85,              # 신뢰도 (0.0 ~ 1.0)
    "captured_at": datetime.now().isoformat(),  # 탐지 시간
    "image_name": "bird_001.jpg",    # 이미지 파일명 (옵션)
    "image_data": "base64_string",   # base64 인코딩된 이미지 (옵션)
    "bird_count": 1                  # 탐지된 새 개체 수
}

# API 호출
response = requests.post(
    "http://localhost:8000/detect/result",
    json=detection_data
)

# 응답 확인
if response.status_code == 200:
    result = response.json()
    if result["ok"]:
        print("✅ 전송 성공!")
    else:
        print(f"❌ 서버 에러: {result['error']}")
```

## 🎯 위험도 자동 계산

백엔드에서 `confidence` 값에 따라 위험도가 자동으로 계산됩니다:

| 신뢰도 범위 | 위험도 | 색상 | 설명 |
|-------------|--------|------|------|
| 0.8 ~ 1.0 | `red` | 🔴 | 매우 위험 - 즉시 대응 필요 |
| 0.6 ~ 0.8 | `orange` | 🟠 | 위험 - 주의 깊게 모니터링 |
| 0.4 ~ 0.6 | `yellow` | 🟡 | 경고 - 지속적인 관찰 |
| 0.0 ~ 0.4 | `green` | 🟢 | 낮은 위험 - 일반적인 모니터링 |

## 🔧 문제 해결

### 서버 연결 실패
```
❌ 서버 연결 실패: Connection refused
```
**해결:** 백엔드 서버가 실행되고 있는지 확인하세요.

### HTTP 500 에러
```
❌ HTTP 에러 500: Internal Server Error
```
**해결:** 백엔드 로그를 확인하고, 데이터 형식이 올바른지 확인하세요.

### 이미지 전송 실패
```
❌ 이미지 전송 실패
```
**해결:** 이미지 크기를 확인하고, base64 인코딩이 올바른지 확인하세요.

## 📞 문의사항

테스트 중 문제가 발생하면 백엔드 개발팀에 문의해주세요.

---

**🎯 목표:** 실제 AI 모델과 백엔드 서버 간의 원활한 연동을 위한 완벽한 테스트 환경 제공
