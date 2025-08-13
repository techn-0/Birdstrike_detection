# ws_route.py - 간소화된 WebSocket 라우트
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..ws_manager import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 대기 (연결 유지용)
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
