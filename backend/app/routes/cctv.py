# app/routes/cctv.py
from fastapi import APIRouter
from ..db import db
from ..models import CctvMeta

router = APIRouter()


@router.post("/cctv/meta")
async def upsert(meta: dict):
    await db.cctv.update_one({"_id": meta["id"]},
                             {"$set": meta}, upsert=True)
    return {"ok": True}

#  CCTV 목록 조회 API
@router.get("/cctv/meta")
async def list_cctv():
    docs = await db.cctv.find().to_list(100)
    for d in docs:
        d["id"] = d["_id"]
        del d["_id"]
    return docs

# CCTV 삭제
@router.delete("/cctv/meta/{cctv_id}")
async def delete_cctv(cctv_id: str):
    result = await db.cctv.delete_one({"_id": cctv_id})
    if result.deleted_count == 0:
        return {"ok": False, "error": "Not found"}
    return {"ok": True}
