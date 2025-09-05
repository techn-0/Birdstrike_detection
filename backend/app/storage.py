# storage.py - 간소화된 저장소 관리
from typing import Dict, Any
from datetime import datetime

# 메모리 저장소 (MongoDB fallback용)
cctv_storage: Dict[str, Dict[str, Any]] = {}

async def init_storage():
    """
    저장소 초기화
    
    MongoDB 우선 시도 → 실패시 메모리 저장소로 fallback
    """
    try:
        from app.services.user_service import UserService
        await UserService.init_test_users()
        print("MongoDB 사용자 저장소 초기화 완료")
    except Exception as e:
        print(f"MongoDB 초기화 실패: {e}")
        _init_memory_users()  # MongoDB 실패시 안전장치 활성화

def _init_memory_users():
    """
    메모리 저장소에 테스트 사용자 생성
    
    ⚠️ 이 함수는 MongoDB 연결 실패시에만 호출되는 fallback 함수입니다.
    - MongoDB 서버 다운
    - Docker 컨테이너 문제
    - 네트워크 연결 실패
    등의 상황에서 시스템이 완전히 중단되는 것을 방지하는 안전장치입니다.
    
    정상 상황에서는 호출되지 않으므로 제거하지 마세요!
    """
    from app.core.security import hash_pw
    from app.storage import fake_users_db
    
    if not fake_users_db:
        fake_users_db["admin"] = {
            "name": "Admin User",
            "username": "admin", 
            "email": "admin@example.com",
            "hashed_password": hash_pw("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        
        fake_users_db["user"] = {
            "name": "Test User",
            "username": "user",
            "email": "user@example.com", 
            "hashed_password": hash_pw("user123"),
            "role": "user",
            "created_at": datetime.utcnow()
        }
        
        print("메모리 테스트 사용자 생성됨: admin/admin123, user/user123")

# 사용자 메모리 저장소 (MongoDB fallback용 - 정상시에는 비어있음)
fake_users_db: Dict[str, Dict[str, Any]] = {}
