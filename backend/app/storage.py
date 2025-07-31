# 임시 메모리 저장소 (실제로는 MongoDB 사용)
from typing import Dict, Any
from datetime import datetime

# 사용자 저장소
fake_users_db: Dict[str, Dict[str, Any]] = {}

# CCTV 저장소  
cctv_storage: Dict[str, Dict[str, Any]] = {}

def init_test_users():
    """테스트 사용자 초기화"""
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
        
        print("Test users initialized: admin/admin123, user/user123")
