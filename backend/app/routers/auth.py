from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_pw, verify_pw, create_access_token
from app.dependencies import get_current_user
from app.storage import fake_users_db
from app.services.user_service import UserService
from app.db import db
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """사용자 회원가입 (MongoDB 우선, 실패시 메모리)"""
    try:
        # MongoDB 우선 시도
        existing_user = await UserService.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # MongoDB에 사용자 생성
        new_user = await UserService.create_user(user_data)
        return UserResponse(**new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        # 메모리 저장소로 fallback
        print(f"MongoDB signup failed: {e}, using memory storage")
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
        except Exception as mem_error:
            print(f"Memory signup error: {mem_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(mem_error)}"
            )


@router.post("/login")
async def login(response: Response, user_credentials: UserLogin):
    """사용자 로그인 (MongoDB 우선, 실패시 메모리)"""
    try:
        # MongoDB 우선 시도
        user = await UserService.get_user_by_username(user_credentials.username)
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
            samesite="lax",
            path="/"  # 모든 경로에서 쿠키 사용 가능
        )
        
        return {
            "message": "Login successful",
            "user": UserResponse(**user),
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # 메모리 저장소로 fallback
        print(f"MongoDB login failed: {e}, using memory storage")
        
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
            samesite="lax",
            path="/"  # 모든 경로에서 쿠키 사용 가능
        )
        
        return {
            "message": "Login successful (memory)",
            "user": UserResponse(**user),
            "access_token": access_token,
            "token_type": "bearer"
        }


@router.post("/logout")
async def logout(response: Response, current_user: UserResponse = Depends(get_current_user)):
    """사용자 로그아웃 및 탐지 결과 삭제"""
    try:
        # 1. 쿠키 삭제
        response.delete_cookie(key="access_token", path="/")
        
        # 2. MongoDB에서 모든 탐지 결과 컬렉션 삭제
        try:
            # 모든 컬렉션 이름 조회
            all_collections = await db.list_collection_names()
            detection_cols = [name for name in all_collections if name.startswith("detections_")]
            
            # 각 탐지 컬렉션 삭제
            for col_name in detection_cols:
                await db.drop_collection(col_name)
                print(f"Deleted detection collection: {col_name}")
            
            return {
                "message": "Logout successful - All detection data cleared",
                "deleted_collections": detection_cols
            }
            
        except Exception as e:
            print(f"Failed to clear detection data from MongoDB: {e}")
            # 탐지 데이터 삭제에 실패해도 로그아웃은 성공으로 처리
            return {
                "message": "Logout successful - Warning: Detection data may not be cleared",
                "error": str(e)
            }
            
    except Exception as e:
        # 로그아웃 실패 시에도 쿠키는 삭제 시도
        response.delete_cookie(key="access_token", path="/")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout error: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user


@router.get("/test-admin")
async def test_admin_endpoint(request: Request):
    """관리자 계정 생성 테스트용 엔드포인트 (MongoDB 우선)"""
    try:
        # MongoDB 초기화 시도
        await UserService.init_test_users()
        
        return {
            "message": "Test users created in MongoDB",
            "users": {
                "admin": {"username": "admin", "password": "admin123", "role": "admin"},
                "user": {"username": "user", "password": "user123", "role": "user"}
            }
        }
    except Exception as e:
        # 메모리 저장소로 fallback
        print(f"MongoDB test users failed: {e}, using memory storage")
        
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
            "message": "Test users created in memory",
            "users": {
                "admin": {"username": "admin", "password": "admin123", "role": "admin"},
                "user": {"username": "user", "password": "user123", "role": "user"}
            }
        }
