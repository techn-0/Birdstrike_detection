# 🚀 조류 탐지 API 퀵가이드

## ⚡ 5분 만에 시작하기

<img width="321" height="373" alt="image" src="https://github.com/user-attachments/assets/a88e57a8-45a7-43f6-9938-0a8fdb0d2c56" />
프론트 엔드에 이와 같은 cctv 를 먼저 등록해 주세요


### 1. 서버 실행 ✅
```bash
# 백엔드 (터미널 1)
cd backend && python -m uvicorn app.main:app --reload --port 8000

# 프론트엔드 (터미널 2)  
cd frontend && npm start
```

### 2. 테스트 실행 ✅
```bash
cd test
python csv_detection_test.py
```

### 3. 결과 확인 ✅
브라우저: `http://localhost:3000`

---

## 📝 CSV 형식 (필수 필드만)
```csv
image_name,confidence,x1,y1,x2,y2,width,height,center_x,center_y
D02_20210628090856_0000714_crop_000.png,0.272,508.83,534.93,524.51,543.12,15.68,8.19,516.67,539.02
```

## 🏷️ CCTV ID 규칙
- `D02_20210628*` → `AIRPORT_CAM_D02_A`
- `D02_20210721*` → `AIRPORT_CAM_D02_B`

## 🔴 위험도 자동 분류
- **조류 미탐지**: green (정상 상태)
- **1개 + 신뢰도 < 30%**: yellow (모니터링 대상)
- **1개 + 신뢰도 ≥ 30%**: orange (주의 필요)
- **2개 이상 탐지**: red (즉시 경보)

## 🔗 핵심 API
```python
# 1. 이미지 업로드
POST /upload/image
files = {'file': ('image.png', file_data, 'image/png')}

# 2. 탐지 결과 전송
POST /detect/result
{
  "cctv_id": "AIRPORT_CAM_D02_A",
  "bbox": [x, y, width, height],
  "pos": [center_x, center_y],
  "risk": "green",
  "frame_url": "/frames/uuid.png",
  "bird_count": 1
}

# 3. 내역 조회
GET /detect/history/{cctv_id}
```

## 🆘 문제해결
- **연결 실패**: 서버 실행 확인
- **업로드 실패**: 이미지 파일 경로 확인  
- **CSV 실패**: `test/` 디렉토리에서 실행

---
📖 **자세한 내용**: `README_DETECTION_API.md` 참조
