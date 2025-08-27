# API 요약

## 기본 정보
- 서버 진입점: `backend/app/main.py`
- DB: MongoDB 연결 (env `MONGO_URI`, 기본 `mongodb://localhost:27017`), DB명 `birdwatch` (`backend/app/db.py`)
- Swagger UI: http://localhost:8000/docs (서버 기본 실행 가정)
- 정적 파일: `/frames/<filename>` → `app/static/frames`
- 인증: JWT (cookie `access_token` 우선, 없으면 Authorization Bearer header). JWT 생성/검증: `backend/app/core/security.py`
- WebSocket 엔드포인트: `/ws` (`backend/app/routes/ws_route.py`)

## API 명세 표

| API 이름              | 요청 URL                     | 요청 방식 | 요청 헤더                          | 요청 본문                                                                 | 응답 코드 | 응답 데이터                                                                 | 설명                                   |
|-----------------------|------------------------------|-----------|------------------------------------|---------------------------------------------------------------------------|-----------|-----------------------------------------------------------------------------|----------------------------------------|
| 헬스체크              | /ping                        | GET       | 없음                               | 없음                                                                      | 200       | `{ "ok": true }`                                                          | 서버 상태 확인                          |
| 사용자 생성           | /api/auth/signup            | POST      | `Content-Type: application/json`  | `{ "username": "string", "password": "string", "email": "string" }` | 200       | `UserResponse` 또는 에러                                                   | 사용자 계정 생성                       |
| 로그인                | /api/auth/login             | POST      | `Content-Type: application/json`  | `{ "username": "string", "password": "string" }`                    | 200       | `{ "user": "object", "access_token": "string" }`                     | JWT 발급 및 쿠키 설정                  |
| 로그아웃              | /api/auth/logout            | POST      | 없음                               | 없음                                                                      | 200       | 없음                                                                        | 쿠키 삭제로 로그아웃                   |
| 현재 사용자 정보 조회 | /api/auth/me                | GET       | `Authorization: Bearer <token>`   | 없음                                                                      | 200       | `UserResponse`                                                              | 현재 인증된 사용자 정보 반환           |
| 단일 감지 결과 처리   | /detect                     | POST      | `Content-Type: application/json`  | `Detection` JSON                                                          | 200       | `{ "ok": true, "error": "string" }`                                    | 단일 감지 결과 저장 및 처리            |
| 배치 감지 결과 처리   | /detect/batch               | POST      | `Content-Type: application/json`  | `DetectionBatch` JSON                                                     | 200       | `{ "ok": true, "error": "string" }`                                    | 다수의 감지 결과를 한 번에 처리         |
| 감지 히스토리 조회    | /detect/history/{cctv_id}   | GET       | 없음                               | 없음                                                                      | 200       | 감지 결과 리스트                                                            | 특정 CCTV의 감지 히스토리 반환         |
| 이미지 업로드         | /upload/image               | POST      | `Content-Type: multipart/form-data` | 파일 (`UploadFile`)                                                       | 200       | `{ "ok": true, "filename": "string", "url": "string" }`            | 이미지 파일 업로드                     |
| 감지 및 이미지 업로드 | /detect/with_image          | POST      | `Content-Type: multipart/form-data` | 파일 및 감지 데이터                                                       | 200       | `{ "ok": true, "error": "string" }`                                    | 이미지 업로드 후 감지 결과 처리         |

## 헬스체크
- GET /ping
  - 응답: `{ "ok": true }`
  - 파일: `backend/app/main.py`
  - 인증: 없음

  #### 사용 예
  ```cmd
  curl http://localhost:8000/ping
  ```

## 인증 (prefix: `/api/auth`)
관련 파일: `backend/app/routers/auth.py`, 인증 의존성: `backend/app/dependencies.py`, JWT: `backend/app/core/security.py`

- POST /api/auth/signup
  - 설명: 사용자 생성
  - 입력: JSON (`UserCreate` — username, password, email, name, role 등)
  - 출력: `UserResponse` 또는 에러
  - 인증: 없음

- POST /api/auth/login
  - 설명: 로그인, JWT 발급 및 HttpOnly 쿠키 `access_token` 설정(24h)
  - 입력: JSON (`UserLogin`)
  - 출력: 로그인 메시지, `user`, `access_token`
  - 쿠키: `access_token` (httponly, max_age=24h)
  - 인증: 없음

  #### 사용 예
  ```cmd
  curl -c cookies.txt -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" http://localhost:8000/api/auth/login
  curl -b cookies.txt http://localhost:8000/api/auth/me
  ```

- POST /api/auth/logout
  - 설명: 쿠키 삭제로 로그아웃
  - 인증: 없음

- GET /api/auth/me
  - 설명: 현재 인증된 사용자 정보 반환
  - 출력: `UserResponse`
  - 인증: 필요 (`get_current_user` 사용 — cookie 또는 Bearer)

  #### 사용 예
  ```cmd
  curl -H "Authorization: Bearer <token>" http://localhost:8000/api/auth/me
  ```

- GET /api/auth/test-admin
  - 설명: 테스트용 admin/user 생성 (MongoDB 실패 시 메모리 fallback)
  - 인증: 없음

## 감지(Detect) 관련 엔드포인트
관련 파일: `backend/app/routes/detect.py`, 모델: `backend/app/models.py`, `backend/app/models/cctv.py`, 서비스: `backend/app/services/detection_service.py`

- POST /detect
  - 설명: 단일 감지 결과 처리
  - 입력: JSON `Detection` (주요 필드: `cctv_id`, `bbox` [x,y,w,h], `pos` [u,v], `risk`("red"|"orange"|"yellow"|"green"), `captured_at`, `frame_url`, `bird_count`)
  - 출력: `Result` { ok: bool, error?: str }
  - 인증: 없음
  - 동작: `DetectionService.process_detection` 호출 (DB 저장/브로드캐스트 등)

  #### 사용 예
  ```cmd
  curl -H "Content-Type: application/json" -d "{\"cctv_id\":\"cam1\",\"bbox\":[0,0,100,100],\"pos\":[50,50],\"risk\":\"green\",\"captured_at\":\"2025-08-26T12:00:00\"}" http://localhost:8000/detect
  ```

- POST /detect/result
  - 설명: `/detect`의 alias (내부적으로 동일 처리)

- POST /detect/batch
  - 설명: CSV 형식(또는 다수의 엔트리) 배치 처리
  - 입력: JSON `DetectionBatch` (list of `DetectionCSV`, `cctv_id`)
  - 출력: `Result`
  - 인증: 없음

- GET /detect/history/{cctv_id}
  - 설명: 특정 CCTV의 감지 히스토리 조회
  - 출력: 문서 리스트 (MongoDB의 `detections_*` 컬렉션에서 `cctv_id` 필터)
  - 인증: 없음
  - 반환 전처리: `_id` -> str, `captured_at` -> ISO 문자열, 시간 역순 정렬

- POST /upload/image
  - 설명: 이미지 업로드 (multipart/form-data)
  - 입력: 파일 (`UploadFile`)
  - 파일 확장자 허용: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`
  - 저장: `app/static/frames/<uuid>.<ext>`
  - 출력: `{ ok, filename, original_filename, url, size }`
  - 인증: 없음

  #### 사용 예
  ```cmd
  curl -F "file=@C:\full\path\to\image.jpg" http://localhost:8000/upload/image
  ```

- POST /detect/with_image
  - 설명: 이미지 업로드 후 감지 결과 전송 (파일 + 폼 필드)
  - 입력: multipart (file, cctv_id, bbox (JSON string), pos (JSON string), risk, bird_count)
  - 동작: 내부에서 `/upload/image` 호출 -> Detection 생성 -> 처리
  - 출력: `Result`
  - 인증: 없음

## CSV 결과 저장 및 처리
### CSV 결과 저장 테스트 (`csv_detection_test.py`)
`csv_detection_test.py`는 CSV 파일(`detection_results.csv`)에 저장된 탐지 결과를 MongoDB에 저장하고, 업로드된 이미지와 함께 프론트엔드에서 확인할 수 있도록 테스트하는 스크립트입니다. 주요 과정은 다음과 같습니다:

1. **CSV 파일 로드**:
   - `load_csv_detections` 메서드를 통해 CSV 파일에서 탐지 데이터를 읽어옵니다.
   - 각 행은 탐지 결과로 변환됩니다.

2. **이미지 업로드**:
   - `upload_image` 메서드를 사용하여 이미지 파일을 `/upload/image` 엔드포인트로 업로드합니다.
   - 업로드된 이미지의 URL이 반환됩니다.

3. **탐지 데이터 변환**:
   - `csv_to_detection_format` 메서드를 통해 CSV 데이터를 API에서 요구하는 JSON 형식으로 변환합니다.
   - 변환된 데이터에는 `cctv_id`, `bbox`, `pos`, `risk`, `captured_at`, `frame_url`, `bird_count` 필드가 포함됩니다.

4. **탐지 결과 전송**:
   - 변환된 JSON 데이터를 `/detect` 엔드포인트로 전송합니다.
   - `send_detection_result` 메서드를 사용하여 각 탐지 결과를 서버에 저장합니다.

5. **결과 확인**:
   - `get_detection_history` 메서드를 통해 특정 CCTV의 탐지 히스토리를 조회하여 저장된 결과를 확인합니다.

### CSV 처리 흐름
1. `detection_results.csv` 파일에서 데이터를 읽습니다.
2. 각 데이터에 대해:
   - 이미지 파일을 업로드하고 URL을 획득합니다.
   - 데이터를 JSON 형식으로 변환합니다.
   - 변환된 데이터를 `/detect` 엔드포인트로 전송합니다.
3. 모든 데이터가 처리된 후, 결과를 요약하여 출력합니다.


이 방법은 대량의 데이터를 처리할 때 유용하며, `csv_detection_test.py`의 개별 전송 방식보다 효율적입니다.

## CCTV 메타 관리
관련 파일: `backend/app/routes/cctv.py`, 권한 의존성: `require_admin` (`backend/app/dependencies.py`)

- POST /cctv/meta
  - 설명: CCTV 메타 생성/수정
  - 입력: JSON meta (최소 `id`)
  - 인증: 관리자 필요 (`require_admin`)
  - 동작: MongoDB `db.cctv.update_one(..., upsert=True)` 시도, 실패 시 메모리 `cctv_storage`에 저장

- GET /cctv/meta
  - 설명: CCTV 목록 조회 (DB 또는 메모리 fallback)
  - 인증: 없음

- DELETE /cctv/meta/{cctv_id}
  - 설명: CCTV 삭제
  - 인증: 관리자 필요
  - 동작: DB 삭제 시도, 실패 시 메모리에서 제거

## WebSocket
- ws://<host>:<port>/ws
  - 파일: `backend/app/routes/ws_route.py`, 매니저: `backend/app/ws_manager.py`
  - 동작: 연결 수락 후 서버-측 브로드캐스트를 받을 수 있음. 클라이언트는 서버가 전송하는 메시지를 수신.
  - 사용처: 실시간 감지 알림 전송
