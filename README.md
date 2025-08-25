# 🚁 BirdWatch - 공항 조류 탐지 시스템

## 📋 프로젝트 개요

**BirdWatch**는 공항 안전을 위한 실시간 조류 탐지 및 모니터링 시스템입니다. YOLO 기반 조류 탐지 모델의 결과를 받아 웹 인터페이스에서 실시간으로 시각화하고, 위험도에 따른 경보 시스템을 제공합니다.

### 🎯 주요 기능

- **실시간 조류 탐지**: YOLO 모델 결과를 즉시 수신 및 처리
- **웹 기반 모니터링**: React + Leaflet 기반 지도 인터페이스
- **위험도 분류**: 신뢰도 기반 4단계 위험도 자동 분류
- **WebSocket 통신**: 실시간 탐지 결과 푸시
- **사용자 인증**: JWT 기반 로그인 시스템
- **배치 처리**: 대량 탐지 결과 일괄 처리 지원
- **데이터 저장**: MongoDB 기반 탐지 이력 관리

### 🏗️ 시스템 아키텍처

```
[탐지 모델] --HTTP POST--> [FastAPI 백엔드] --WebSocket--> [React 프론트엔드]
                              |
                              v
                         [MongoDB 데이터베이스]
```

---

## 🗂️ 프로젝트 구조

```
Birdstrike_detection/
├── backend/                     # FastAPI 백엔드 서버
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 애플리케이션 진입점
│   │   ├── models.py           # Pydantic 데이터 모델
│   │   ├── db.py               # MongoDB 연결 관리
│   │   ├── storage.py          # 데이터 저장소 초기화
│   │   ├── ws_manager.py       # WebSocket 연결 관리
│   │   ├── dependencies.py     # 의존성 주입
│   │   ├── core/
│   │   │   └── security.py     # JWT 인증 로직
│   │   ├── models/
│   │   │   ├── user.py         # 사용자 모델
│   │   │   └── cctv.py         # CCTV 메타데이터 모델
│   │   ├── routes/
│   │   │   ├── detect.py       # 탐지 관련 API 엔드포인트
│   │   │   ├── cctv.py         # CCTV 관리 API
│   │   │   └── ws_route.py     # WebSocket 엔드포인트
│   │   ├── routers/
│   │   │   └── auth.py         # 인증 관련 API
│   │   ├── services/
│   │   │   ├── detection_service.py  # 탐지 서비스 로직
│   │   │   ├── user_service.py       # 사용자 서비스
│   │   │   └── file_storage.py       # 파일 저장 서비스
│   │   └── static/
│   │       └── frames/         # 탐지 이미지 저장소
│   ├── requirements.txt        # Python 의존성
│   └── Dockerfile             # 백엔드 Docker 설정
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.tsx     # 지도 컴포넌트
│   │   │   ├── Header.tsx      # 헤더 컴포넌트
│   │   │   ├── SidePanel.tsx   # 사이드 패널
│   │   │   ├── LoginModal.tsx  # 로그인 모달
│   │   │   └── DetectionModal.tsx # 탐지 상세 모달
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx # 인증 컨텍스트
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts # WebSocket 훅
│   │   ├── api/                # API 통신 모듈
│   │   ├── types/              # TypeScript 타입 정의
│   │   ├── App.tsx             # 메인 앱 컴포넌트
│   │   ├── index.tsx          # React 엔트리포인트
│   │   └── index.css          # 글로벌 스타일
│   ├── public/
│   │   ├── airport_bg.png     # 공항 배경 이미지
│   │   └── index.html
│   └── package.json           # Node.js 의존성
├── test/                      # 테스트 및 샘플 데이터
│   ├── csv_detection_test.py      # CSV 기반 탐지 테스트
│   ├── detection_api_example.py   # 탐지 API 예제
│   ├── detection_results.csv      # 샘플 탐지 결과 데이터
│   ├── QUICKSTART.md              # 빠른 시작 가이드
│   ├── README_DETECTION_API.md    # 탐지 API 설명서
│   ├── __pycache__/               # 파이썬 캐시
│   ├── detection_image/           # 테스트 이미지
│   │   ├── D02_20210628090856_0000714_crop_000.png
│   │   ├── D02_20210628090856_0008028_crop_005.png
│   │   ├── D02_20210721142744_0001120_crop_007.png
│   │   ├── D02_20210721142744_0001121_crop_002.png
│   │   ├── D02_20210721142744_0009136_crop_004.png
│   │   ├── D02_20210721142744_0009499_crop_007.png
│   │   └── ...
│   └── test/
│       └── OLD/                    # 이전 테스트 데이터
├── _data/
│   └── mongo/                 # MongoDB 데이터 영구 저장소
├── birdwatch-auth/            # 독립 인증 서비스 (선택사항)
├── docker-compose.yml         # Docker Compose 설정
├── cleanup_files.bat          # Windows 정리 스크립트
├── cleanup_files.sh           # Linux/Mac 정리 스크립트
└── README.md                  # 이 파일
```

---

## 🚀 빠른 시작

### 1. 환경 요구사항

- **Docker & Docker Compose**: 컨테이너 실행
- **Node.js 16+**: 프론트엔드 개발
- **Python 3.8+**: 백엔드 개발
- **MongoDB**: 데이터베이스 (Docker로 자동 설치)

### 2. 시스템 실행

#### 방법 1: Docker Compose 사용 (권장)

```bash
# 1. 리포지토리 클론
git clone <repository-url>
cd Birdstrike_detection

# 2. Docker Compose로 백엔드 + MongoDB 실행
docker-compose up --build

# 3. 프론트엔드 개발 서버 실행 (새 터미널)
cd frontend
npm install
npm start
```

#### 방법 2: 개별 실행

```bash
# 1. MongoDB 실행
docker run -d -p 27017:27017 --name mongo mongo:6

# 2. 백엔드 실행
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. 프론트엔드 실행
cd frontend
npm install
npm start
```

### 3. 접속 확인

- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **프론트엔드**: http://localhost:3000
- **MongoDB**: mongodb://localhost:27017 (또는 27018 if Docker)

---

## 🔧 API 사용법

### 📊 주요 엔드포인트

| 메서드 | 경로 | 설명 | 권한 |
|--------|------|------|------|
| `GET` | `/ping` | 헬스체크 | 🔓 공개 |
| `POST` | `/detect/result` | 개별 탐지 결과 저장 | 🔓 공개 |
| `POST` | `/detect/batch` | 배치 탐지 결과 저장 | 🔓 공개 |
| `GET` | `/detect/history/{cctv_id}` | 탐지 내역 조회 | 🔓 공개 |
| `POST` | `/api/register` | 사용자 회원가입 | 🔓 공개 |
| `POST` | `/api/login` | 사용자 로그인 | 🔓 공개 |
| `GET` | `/api/me` | 사용자 정보 조회 | 🔒 인증 필요 |
| `WS` | `/ws` | 실시간 탐지 결과 스트림 | 🔓 공개 |

### 📝 탐지 결과 전송 예시

#### 개별 탐지 결과 전송
```bash
curl -X POST http://localhost:8000/detect/result \
  -H "Content-Type: application/json" \
  -d '{
    "cctv_id": "airport_cam_01",
    "bbox": [0.3, 0.2, 0.1, 0.1],
    "pos": [0.35, 0.25],
    "risk": "red",
    "captured_at": "2025-08-15T12:34:56Z",
    "frame_url": "/frames/sample.jpg",
    "bird_count": 1
  }'
```

#### 배치 탐지 결과 전송
```bash
curl -X POST http://localhost:8000/detect/batch \
  -H "Content-Type: application/json" \
  -d '{
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
    ],
    "cctv_id": "airport_cam_01",
    "captured_at": "2025-08-15T12:34:56Z"
  }'
```

### 🎨 위험도 분류 시스템

탐지 신뢰도에 따른 자동 위험도 분류:

| 위험도 | 색상 | 신뢰도 범위 | 의미 |
|--------|------|-------------|------|
| 🔴 **red** | 빨강 | 0.8 이상 | 즉시 경보 필요 |
| 🟠 **orange** | 주황 | 0.6 - 0.8 | 주의 필요 |
| 🟡 **yellow** | 노랑 | 0.4 - 0.6 | 모니터링 대상 |
| 🟢 **green** | 초록 | 0.4 미만 | 참고용 |

---

## 🧪 테스트

### 1. API 테스트 실행

```bash
cd test
python storage_api_test.py
```

이 스크립트는 다음을 테스트합니다:
- ✅ 서버 연결 상태
- 🔍 개별 탐지 결과 저장
- 📦 배치 탐지 결과 저장
- 📊 탐지 내역 조회
- 🔄 순차 전송 처리

### 2. WebSocket 연결 테스트

브라우저 개발자 도구에서:

```javascript
// WebSocket 연결
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => console.log("✅ WebSocket 연결됨");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("📡 실시간 탐지:", data);
};
```

### 3. 테스트 데이터

`test/detection_results.csv` 파일에 샘플 탐지 데이터가 포함되어 있습니다. 이를 사용하여 배치 처리와 개별 전송을 테스트할 수 있습니다.

---

## 🔐 인증 시스템

### JWT 기반 인증

1. **회원가입**: `POST /api/register`
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "password123"
   }
   ```

2. **로그인**: `POST /api/login`
   ```json
   {
     "username": "testuser",
     "password": "password123"
   }
   ```

3. **토큰 사용**: 응답받은 `access_token`을 Authorization 헤더에 포함
   ```
   Authorization: Bearer <access_token>
   ```

---

## 🐳 Docker 설정

### docker-compose.yml 구성

```yaml
services:
  mongo:
    image: mongo:6
    ports:
      - "27018:27017"
    volumes:
      - ./_data/mongo:/data/db

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGO_URI=mongodb://mongo:27017
    volumes:
      - ./backend:/code
    depends_on:
      - mongo
```

### 유용한 Docker 명령어

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 실시간 확인
docker-compose logs -f api

# 컨테이너 재시작
docker-compose restart api

# 데이터베이스 초기화
docker-compose down
sudo rm -rf _data/mongo/*
docker-compose up
```

---

## 🔧 개발 가이드

### 백엔드 개발

```bash
cd backend

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드 개발

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start

# 빌드
npm run build
```

### 환경 변수 설정

#### 백엔드 (.env)
```bash
MONGO_URI=mongodb://localhost:27017
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
```

#### 프론트엔드 (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

---

## 📈 모니터링 및 로깅

### 로그 확인

```bash
# Docker 로그
docker-compose logs -f api

# 파일 로그 (백엔드)
tail -f backend/app.log
```

### 성능 모니터링

- **API 응답시간**: FastAPI 자동 메트릭
- **WebSocket 연결**: 연결 수 및 상태 모니터링
- **데이터베이스**: MongoDB 쿼리 성능

---

## 🔍 문제 해결

### 일반적인 문제

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| 포트 충돌 | 8000/3000 포트 사용 중 | `netstat -ano \| findstr :8000` 후 프로세스 종료 |
| MongoDB 연결 실패 | 서비스 미실행 | `docker-compose up mongo` |
| WebSocket 연결 끊김 | 네트워크 불안정 | 자동 재연결 로직 구현됨 |
| CORS 에러 | 도메인 정책 | `backend/app/main.py`에서 CORS 설정 확인 |

### 데이터베이스 관리

```bash
# MongoDB 셸 접속
docker exec -it <mongo-container-id> mongosh

# 데이터베이스 확인
use birdwatch
db.detections.find().limit(5)

# 데이터 초기화
db.detections.deleteMany({})
```

### 성능 최적화

1. **배치 처리**: 대량 데이터는 `/detect/batch` 사용
2. **인덱싱**: MongoDB에 적절한 인덱스 설정
3. **캐싱**: Redis 등 캐시 레이어 추가 고려
4. **압축**: 이미지 압축 및 CDN 사용

---

## 🚀 배포 가이드

### 프로덕션 배포

1. **환경 변수 설정**
   ```bash
   export MONGO_URI=mongodb://production-mongo:27017
   export JWT_SECRET_KEY=production-secret-key
   ```

2. **Docker 이미지 빌드**
   ```bash
   docker build -t birdwatch-api ./backend
   docker build -t birdwatch-frontend ./frontend
   ```

3. **컨테이너 실행**
   ```bash
   docker run -d -p 8000:8000 birdwatch-api
   docker run -d -p 80:80 birdwatch-frontend
   ```

### CI/CD 파이프라인

GitHub Actions 예시:

```yaml
name: Deploy BirdWatch
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 추가 문서

- **[API 통합 가이드](test/API_INTEGRATION_GUIDE.md)**: 탐지 모델 통합 방법
- **[FastAPI 문서](http://localhost:8000/docs)**: 실시간 API 문서
- **[프론트엔드 README](frontend/README.md)**: React 개발 가이드

---

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성
