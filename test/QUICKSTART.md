# 🚀 조류 탐지 API 퀵가이드

## ⚡ 5분 만에 시작하기

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
- **0.8~1.0**: 🔴 red (고위험)
- **0.6~0.8**: 🟠 orange (중위험)  
- **0.4~0.6**: 🟡 yellow (저위험)
- **0.0~0.4**: 🟢 green (매우 저위험)

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
