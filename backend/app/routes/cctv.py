# app/routes/cctv.py
from fastapi import APIRouter, Depends
from ..db import db
from ..models import CctvMeta
from app.dependencies import get_current_user, require_admin, get_current_user_optional
from app.models.user import UserResponse
from app.storage import cctv_storage
from typing import Optional

router = APIRouter()


@router.post("/cctv/meta")
async def upsert(meta: dict, current_user: UserResponse = Depends(require_admin)):
    """CCTV 메타데이터 추가/수정 (관리자 전용)"""
    try:
        # MongoDB 사용 시도
        await db.cctv.update_one({"_id": meta["id"]},
                                 {"$set": meta}, upsert=True)
        print(f"CCTV saved to MongoDB: {meta['id']}")
        return {"ok": True}
    except Exception as e:
        print(f"MongoDB error: {e}")
        # MongoDB 실패 시 메모리 저장소 사용
        cctv_id = meta.get("id")
        if cctv_id:
            cctv_storage[cctv_id] = meta
            print(f"CCTV saved to memory: {cctv_id}")
        return {"ok": True, "note": "Stored in memory (MongoDB unavailable)"}


#  CCTV 목록 조회 API (모든 사용자 접근 가능)
@router.get("/cctv/meta")
async def list_cctv():
    """CCTV 목록 조회 (인증 불필요)"""
    try:
        # MongoDB 사용 시도
        docs = await db.cctv.find().to_list(100)
        for d in docs:
            d["id"] = d["_id"]
            del d["_id"]
        return docs
    except Exception as e:
        print(f"MongoDB error: {e}")
        # MongoDB 실패 시 메모리 저장소 사용
        cctv_list = []
        for cctv_id, cctv_data in cctv_storage.items():
            cctv_copy = cctv_data.copy()
            cctv_copy["id"] = cctv_id
            cctv_list.append(cctv_copy)
        return cctv_list


# CCTV 삭제 (관리자 전용)
@router.delete("/cctv/meta/{cctv_id}")
async def delete_cctv(cctv_id: str, current_user: UserResponse = Depends(require_admin)):
    """CCTV 삭제 (관리자 전용)"""
    try:
        # MongoDB 사용 시도
        result = await db.cctv.delete_one({"_id": cctv_id})
        if result.deleted_count == 0:
            return {"ok": False, "error": "Not found"}
        return {"ok": True}
    except Exception as e:
        # MongoDB 실패 시 메모리 저장소 사용
        if cctv_id in cctv_storage:
            del cctv_storage[cctv_id]
            return {"ok": True, "note": "Deleted from memory (MongoDB unavailable)"}
        else:
            return {"ok": False, "error": "Not found"}
