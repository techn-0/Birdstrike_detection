# MongoDB와 메모리 저장소 혼합 사용
from typing import Dict, Any
from datetime import datetime

# CCTV 저장소 (메모리 - MongoDB 실패 시 fallback)
cctv_storage: Dict[str, Dict[str, Any]] = {}

# 사용자는 MongoDB 우선, 실패 시 메모리 fallback
fake_users_db: Dict[str, Dict[str, Any]] = {}

async def init_storage():
    """저장소 초기화 - MongoDB 우선, 실패 시 메모리"""
    try:
        # MongoDB 사용자 초기화 시도
        from app.services.user_service import UserService
        await UserService.init_test_users()
        print("Using MongoDB for user storage")
    except Exception as e:
        print(f"MongoDB initialization failed: {e}")
        print("Falling back to memory storage for users")
        # 메모리 저장소로 fallback
        init_memory_users()

def init_memory_users():
    """메모리 저장소에 테스트 사용자 초기화"""
    from app.core.security import hash_pw
    
    if not fake_users_db:  # 빈 경우에만 초기화
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
        
        fake_users_db["admin"] = admin_user
        fake_users_db["user"] = regular_user
        
        print("Test users initialized in memory: admin/admin123, user/user123")
