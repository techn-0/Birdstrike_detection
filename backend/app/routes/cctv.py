# app/routes/cctv.py
from fastapi import APIRouter
from ..db import db          # 또는 from app.db import db

router = APIRouter()         # ← 이 줄이 반드시 필요

@router.post("/cctv/meta")
async def upsert(meta: dict):
    await db.cctv.update_one({"_id": meta["id"]},
                             {"$set": meta}, upsert=True)
    return {"ok": True}
