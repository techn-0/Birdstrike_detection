# ws_manager.py - 간소화된 WebSocket 관리자
from typing import List
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, data: dict):
        if not self.connections:
            return
        
        safe_data = jsonable_encoder(data)
        for connection in self.connections[:]:  # 복사본으로 반복
            try:
                await connection.send_json(safe_data)
            except Exception:
                # 연결이 끊어진 경우 목록에서 제거
                self.disconnect(connection)

# 전역 관리자 인스턴스
manager = ConnectionManager()
