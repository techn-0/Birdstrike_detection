# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes import detect, cctv
from app.routes import ws_route
from app.routers import auth
from app.storage import init_test_users

import logging
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

app = FastAPI()

# 테스트 사용자 초기화
init_test_users()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 구체적인 프론트엔드 URL 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api")
app.include_router(detect.router)
app.include_router(cctv.router)
app.include_router(ws_route.router)

# 정적 파일(프레임 이미지) 서빙
app.mount("/frames", StaticFiles(directory="app/static/frames"), name="frames")


@app.get("/ping")
async def ping():
    return {"ok": True}
