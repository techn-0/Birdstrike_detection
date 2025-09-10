# app/main.py - 간소화된 메인 애플리케이션
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import detect, cctv, ws_route, photo_slides
from .routers import auth
from .storage import init_storage
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)

app = FastAPI(title="Birdstrike Detection API")

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    await init_storage()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api")
app.include_router(detect.router)
app.include_router(cctv.router)
app.include_router(ws_route.router)
app.include_router(photo_slides.router, prefix="/api")

# 정적 파일 서빙
app.mount("/frames", StaticFiles(directory="app/static/frames"), name="frames")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/ping")
async def health_check():
    return {"ok": True}
