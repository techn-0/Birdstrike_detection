from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.models.user import UserResponse, TokenData
from app.core.security import verify_jwt
from app.storage import fake_users_db
import asyncio

# HTTP Bearer 토큰 스키마
security = HTTPBearer(auto_error=False)


def get_token_from_cookie_or_header(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """쿠키 또는 Authorization 헤더에서 토큰 추출"""
    # 1. 쿠키에서 먼저 확인
    token = request.cookies.get("access_token")
    if token:
        return token
    
    # 2. Authorization 헤더에서 확인
    if credentials:
        return credentials.credentials
    
    return None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserResponse:
    """현재 인증된 사용자 정보 반환"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 토큰 추출
    token = get_token_from_cookie_or_header(request, credentials)
    if not token:
        raise credentials_exception
    
    # 토큰 검증
    payload = verify_jwt(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # 사용자 정보 조회 (임시로 fake_users_db 사용)
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    
    return UserResponse(**user)


async def require_admin(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """관리자 권한 필요한 엔드포인트용 의존성"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserResponse]:
    """선택적 사용자 인증 (로그인하지 않아도 접근 가능)"""
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None
