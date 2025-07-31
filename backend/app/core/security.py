import os
from datetime import datetime, timedelta
from typing import Any, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# 패스워드 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pw(password: str) -> str:
    """패스워드 해시화"""
    return pwd_context.hash(password)


def verify_pw(plain_password: str, hashed_password: str) -> bool:
    """패스워드 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """JWT 토큰 생성 (기본 24시간 만료)"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt(token: str) -> Union[dict, None]:
    """JWT 토큰 검증 및 페이로드 반환"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def create_access_token(username: str, role: str) -> str:
    """액세스 토큰 생성"""
    data = {
        "sub": username,
        "role": role,
        "type": "access"
    }
    return create_jwt(data)
