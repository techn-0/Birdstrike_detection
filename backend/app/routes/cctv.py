# app/routes/cctv.py - 간소화된 CCTV API
from fastapi import APIRouter, Depends
from ..db import db
from ..dependencies import require_admin
from ..models.user import UserResponse
from ..models.cctv import CctvMeta
from ..storage import cctv_storage

router = APIRouter()

@router.post("/cctv/meta")
async def create_cctv(meta: CctvMeta, current_user: UserResponse = Depends(require_admin)):
    """CCTV 메타데이터 생성/수정 (관리자 전용)"""
    try:
        meta_dict = meta.model_dump()
        await db.cctv.update_one(
            {"_id": meta.id}, 
            {"$set": meta_dict}, 
            upsert=True
        )
        return {"ok": True}
    except Exception:
        # MongoDB 실패 시 메모리 저장소 사용
        cctv_storage[meta.id] = meta.model_dump()
        return {"ok": True}

@router.get("/cctv/meta")
async def list_cctv():
    """CCTV 목록 조회"""
    try:
        docs = await db.cctv.find().to_list(100)
        for doc in docs:
            doc["id"] = doc["_id"]
            del doc["_id"]
        return docs
    except Exception:
        # MongoDB 실패 시 메모리 저장소 사용
        return [{"id": k, **v} for k, v in cctv_storage.items()]

@router.delete("/cctv/meta/{cctv_id}")
async def delete_cctv(cctv_id: str, current_user: UserResponse = Depends(require_admin)):
    """CCTV 삭제 (관리자 전용)"""
    try:
        result = await db.cctv.delete_one({"_id": cctv_id})
        return {"ok": result.deleted_count > 0}
    except Exception:
        # MongoDB 실패 시 메모리 저장소 사용
        if cctv_id in cctv_storage:
            del cctv_storage[cctv_id]
            return {"ok": True}
        return {"ok": False}
