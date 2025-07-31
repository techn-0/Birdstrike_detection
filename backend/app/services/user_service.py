# 예시: MongoDB 연동 사용자 서비스
from motor.motor_asyncio import AsyncIOMotorClient
from app.db import db

async def create_user_in_db(user_data: dict):
    """사용자를 MongoDB에 저장"""
    result = await db.users.insert_one(user_data)
    return result.inserted_id

async def get_user_from_db(username: str):
    """MongoDB에서 사용자 조회"""
    return await db.users.find_one({"username": username})

async def update_user_in_db(username: str, update_data: dict):
    """MongoDB에서 사용자 정보 업데이트"""
    await db.users.update_one(
        {"username": username}, 
        {"$set": update_data}
    )
