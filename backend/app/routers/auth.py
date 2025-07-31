from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_pw, verify_pw, create_access_token
from app.dependencies import get_current_user
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["authentication"])

# 임시 사용자 저장소 (실제로는 MongoDB 사용)
fake_users_db: Dict[str, Dict[str, Any]] = {}


@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """사용자 회원가입"""
    try:
        # 중복 사용자명 확인
        if user_data.username in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 중복 이메일 확인
        for existing_user in fake_users_db.values():
            if existing_user["email"] == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # 새 사용자 생성
        hashed_password = hash_pw(user_data.password)
        user_dict = {
            "name": user_data.name,
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "role": user_data.role,
            "created_at": datetime.utcnow()
        }
        
        # 사용자 저장
        fake_users_db[user_data.username] = user_dict
        
        # 응답용 사용자 정보 (패스워드 제외)
        return UserResponse(**user_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/login")
async def login(response: Response, user_credentials: UserLogin):
    """사용자 로그인"""
    # 사용자 확인
    user = fake_users_db.get(user_credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # 패스워드 검증
    if not verify_pw(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(
        username=user["username"],
        role=user["role"]
    )
    
    # HttpOnly 쿠키로 토큰 설정 (24시간)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=24 * 60 * 60,  # 24시간 (초 단위)
        secure=False,  # 개발환경에서는 False, 프로덕션에서는 True
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "user": UserResponse(**user),
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(response: Response):
    """사용자 로그아웃"""
    # 쿠키 삭제
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user


@router.get("/test-admin")
async def test_admin_endpoint(request: Request):
    """관리자 계정 생성 테스트용 엔드포인트"""
    admin_user = {
        "name": "Admin User",
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": hash_pw("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow()
    }
    
    fake_users_db["admin"] = admin_user
    
    regular_user = {
        "name": "Test User",
        "username": "user",
        "email": "user@example.com",
        "hashed_password": hash_pw("user123"),
        "role": "user",
        "created_at": datetime.utcnow()
    }
    
    fake_users_db["user"] = regular_user
    
    return {
        "message": "Test users created",
        "users": {
            "admin": {"username": "admin", "password": "admin123", "role": "admin"},
            "user": {"username": "user", "password": "user123", "role": "user"}
        }
    }
