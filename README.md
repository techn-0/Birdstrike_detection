# ✈️ BirdWatch 프로토타입 개발 가이드

## 1. 개요

공항 CCTV 영상에서 YOLO 모델이 탐지한 조류 위치를 실시간으로 웹 지도(React + Leaflet)에 시각화합니다. 학습/추론 모델은 외부에서 HTTP POST로 탐지 결과를 전송하고, 백엔드(FastAPI + MongoDB)가 DB 저장 후 WebSocket 으로 프런트에 푸시합니다.

---

## 2. 디렉터리 구조

```
birdwatch/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py              # FastAPI 진입점
│  │  ├─ ws_manager.py        # WebSocket 싱글턴 (ConnectionManager)
│  │  ├─ models.py            # Pydantic Detection 모델
│  │  ├─ db.py                # Motor(MongoDB) 커넥션 헬퍼
│  │  ├─ static/frames/       # 프레임 이미지 서빙 폴더
│  │  └─ routes/
│  │     ├─ detect.py         # /detect/result POST API
│  │     ├─ cctv.py           # (예비) CCTV 메타 API
│  │     └─ ws_route.py       # /ws WebSocket 엔드포인트
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  │  ├─ components/MapView.tsx
│  │  ├─ hooks/useWebSocket.ts
│  │  └─ index.tsx
│  ├─ public/airport_bg.png
│  ├─ .env                    # REACT_APP_API_WS / HTTP
│  └─
├─ docker-compose.yml
└─ README.md

```

---

## 3. 로컬 실행 (Windows + Docker Desktop)

```
# 1) 이미지 빌드 및 컨테이너 기동
> docker compose up --build

# 2) 백엔드 Uvicorn : http://localhost:8000
#    MongoDB        : mongodb://localhost:27017
#    프런트 Dev 서버: http://localhost:3000  (다른 터미널에서)
> cd frontend
> npm install
> npm start

```

### 컨테이너 상태 확인

```
> docker compose ps      # api, mongo Both Up
> docker compose logs -f api  # 실시간 로그

```

---

## 4. 테스트 시나리오

### 4‑1. WebSocket 수동 접속

1. 브라우저 F12 Console 열기

```
window.ws = new WebSocket("ws://localhost:8000/ws");
ws.onopen  = () => console.log("WS OPEN");
ws.onmessage = e => console.log("WS MSG", JSON.parse(e.data));

```

→ `WS OPEN` 로그가 뜨면 연결 OK

### 4‑2. Dummy Detection POST

```
curl -X POST http://localhost:8000/detect/result ^
     -H "Content-Type: application/json" ^
     -d "{\"cctv_id\":\"T1-01\",\"bbox\":[0.3,0.2,0.005,0.005],\"pos\":[0.30,0.20],\"risk\":\"red\",\"captured_at\":\"2025-05-21T01:10:00Z\",\"frame_url\":\"/frames/sample.jpg\"}"

```

```
curl -X POST http://localhost:8000/detect/result -H "Content-Type: application/json" ^
     -d "{\"cctv_id\":\"T1-02\",\"bbox\":[0.55,0.35,0.006,0.006],\"pos\":[0.55,0.35],\"risk\":\"orange\",\"captured_at\":\"2025-05-21T02:00:05Z\",\"frame_url\":\"/frames/sample.jpg\"}"

```

정상 응답 `{"ok":true}` → 브라우저 Console `WS MSG …` → 지도에 빨간 마커 표시.

---

## 5. API 스펙

| 메서드 | 경로 | 바디/쿼리 | 설명 |
| --- | --- | --- | --- |
| GET | `/ping` | – | 사용 중 헬스체크 200 OK |
| POST | `/detect/result` | `Detection` JSON | 탐지 결과 수신 & DB 저장 & WS 브로드캐스트 |
| WS | `/ws` | – | 서버→클라이언트 실시간 push (JSON) |

### Detection 스키마 (Pydantic)

```
{
  "cctv_id": "T1‑01",
  "bbox": [x, y, w, h],       // 0‑1 정규화
  "pos" : [u, v],            // 0‑1 지도 비율좌표
  "risk": "red|orange|yellow|green",
  "captured_at": "2025‑05‑21T01:10:00Z",
  "frame_url": "/frames/sample.jpg"
}

```

---

## 6. 프런트 구성 요약

- **MapView.tsx** : ImageOverlay(airport_bg.png) + Marker + Popup
- **useWebSocket.ts** : `REACT_APP_API_WS` 로 연결, `onmessage` → `setDets`
- **CSS** (`index.css`)

```css
.risk-red    {background:#ff4040;width:24px;height:24px;border-radius:50%;}
.risk-orange {background:#ffb340;width:24px;height:24px;border-radius:50%;}
.risk-yellow {background:#ffd740;width:24px;height:24px;border-radius:50%;}
.risk-green  {background:#40c040;width:24px;height:24px;border-radius:50%;}

```

---

## 7. 문제 해결 팁

| 증상 | 원인·대처 |
| --- | --- |
| WebSocket 연결은 되는데 broadcast len=0 | `/ws` 핸들러가 다른 모듈과 중복 → `ws_route.py` 하나만 남기기 |
| 500 TypeError: datetime not JSON serializable | `jsonable_encoder` 로 변환 후 send_json |
| 마커 너무 작음 or 안 보임 | CSS `.risk-…` 크기 확대, pos 곱셈(세로·가로) 값 확인 |

---

## 8. 다음 할 일(로드맵)

1. CCTV 정적 아이콘 + FOV 다각형 오버레이 구현
2. 마커 클릭 → 우측 패널(프레임 썸네일, 탐지 타임라인)
3. 위험도 자동 계산 백엔드 로직 (RAG, 거리·고도 임계값)
4. Docker compose.prod.yml – 릴리스 빌드 이미지
5. Unit / e2e 테스트 코드 추가

---

> 마지막 업데이트 : 2025‑05‑21
> 

![image.png](attachment:69af306f-17d9-41df-98bd-c972b17cbd74:image.png)

![image.png](attachment:e445a8a6-74ed-4f03-9acf-6083058607a7:image.png)
