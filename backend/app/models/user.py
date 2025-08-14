from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class UserBase(BaseModel):
    name: str
    username: str
    email: str  # EmailStr 대신 str 사용
    role: Literal["user", "admin"] = "user"
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v.strip()
    
    @validator('name')
    def name_length(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()
    
    @validator('email')
    def email_format(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.strip()


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserResponse(UserBase):
    id: Optional[str] = None  # ObjectId를 문자열로 처리
    created_at: datetime
    
    class Config:
        arbitrary_types_allowed = True


class UserInDB(UserBase):
    id: Optional[str] = None  # ObjectId를 문자열로 처리
    hashed_password: str
    created_at: datetime
    
    class Config:
        arbitrary_types_allowed = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
