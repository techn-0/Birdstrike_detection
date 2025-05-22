from typing import List
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder   # ← 추가

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        print("[WS] connect, total:", len(self.active), "id=", id(self)) # 디버깅용

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        print("[WS] disconnect, total:", len(self.active)) # 디버깅용

    async def broadcast(self, data: dict):
        safe = jsonable_encoder(data)
        print("[WS] broadcast len=", len(self.active))# 디버깅용
        for ws in self.active:
            await ws.send_json(safe)

manager = ConnectionManager()
