# ws_route.py
from fastapi import APIRouter, WebSocket
from app.ws_manager import manager     # 싱글턴 한 곳만 import

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    print("[WS] handler hit, id=", id(manager))
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    finally:
        manager.disconnect(ws)
