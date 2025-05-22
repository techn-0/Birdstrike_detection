# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import detect, cctv
from app.routes import ws_route

app = FastAPI()

# 라우터 등록
app.include_router(detect.router)
app.include_router(cctv.router)
app.include_router(ws_route.router)

# 정적 파일(프레임 이미지) 서빙
app.mount("/frames", StaticFiles(directory="app/static/frames"), name="frames")

@app.get("/ping")
async def ping():
    return {"ok": True}
