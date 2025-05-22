# detect.py
# from fastapi import APIRouter, WebSocket
from fastapi import APIRouter
from ..db import db
from ..models import Detection
from datetime import datetime
from app.ws_manager import manager


router = APIRouter()
# sockets: list[WebSocket] = []     # 간단 브로드캐스트용

@router.post("/detect/result")
async def ingest(det: Detection):
    col = db[f"detections_{det.captured_at:%Y%m}"]
    await col.insert_one(det.dict())
    print("[WS] broadcast len=", len(manager.active), "id=", id(manager))
    await manager.broadcast(det.dict())       # 실시간 push
    print("broadcast sent", len(manager.active)) # 디버깅용
    return {"ok": True}

# @router.websocket("/ws")
# async def ws_endpoint(ws: WebSocket):
#     await ws.accept()
#     sockets.append(ws)
#     try:
#         while True:
#             await ws.receive_text()   # ping용
#     except:
#         sockets.remove(ws)
