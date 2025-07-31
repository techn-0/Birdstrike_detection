# MongoDB 연동 사용자 서비스
from motor.motor_asyncio import AsyncIOMotorClient
from app.db import db
from app.models.user import UserCreate, UserResponse
from app.core.security import hash_pw
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId

class UserService:
    """사용자 관리 서비스"""
    
    @staticmethod
    async def create_user(user_data: UserCreate) -> Optional[str]:
        """사용자를 MongoDB에 저장"""
        try:
            # 중복 확인
            existing_user = await db.users.find_one({
                "$or": [
                    {"username": user_data.username},
                    {"email": user_data.email}
                ]
            })
            
            if existing_user:
                if existing_user["username"] == user_data.username:
                    raise ValueError("Username already registered")
                if existing_user["email"] == user_data.email:
                    raise ValueError("Email already registered")
            
            # 새 사용자 생성
            user_dict = {
                "name": user_data.name,
                "username": user_data.username,
                "email": user_data.email,
                "hashed_password": hash_pw(user_data.password),
                "role": user_data.role,
                "created_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user_dict)
            print(f"User created in MongoDB: {user_data.username}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"MongoDB user creation error: {e}")
            return None

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """사용자명으로 사용자 조회"""
        try:
            user = await db.users.find_one({"username": username})
            if user:
                user["id"] = str(user["_id"])  # ObjectId를 문자열로 변환
                del user["_id"]
            return user
        except Exception as e:
            print(f"MongoDB user lookup error: {e}")
            return None

    @staticmethod
    async def get_all_users() -> list:
        """모든 사용자 조회 (관리 목적)"""
        try:
            cursor = db.users.find({})
            users = []
            async for user in cursor:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["hashed_password"]  # 비밀번호는 제외
                users.append(user)
            return users
        except Exception as e:
            print(f"MongoDB users lookup error: {e}")
            return []

    @staticmethod
    async def init_test_users():
        """테스트 사용자 초기화 (MongoDB에)"""
        try:
            # 이미 사용자가 있는지 확인
            existing_count = await db.users.count_documents({})
            if existing_count > 0:
                print(f"Users already exist in MongoDB: {existing_count} users")
                return
            
            # 테스트 사용자 생성
            admin_user = {
                "name": "Admin User",
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": hash_pw("admin123"),
                "role": "admin",
                "created_at": datetime.utcnow()
            }
            
            regular_user = {
                "name": "Test User",
                "username": "user",
                "email": "user@example.com",
                "hashed_password": hash_pw("user123"),
                "role": "user",
                "created_at": datetime.utcnow()
            }
            
            await db.users.insert_many([admin_user, regular_user])
            print("Test users initialized in MongoDB: admin/admin123, user/user123")
            
        except Exception as e:
            print(f"MongoDB test user initialization error: {e}")
