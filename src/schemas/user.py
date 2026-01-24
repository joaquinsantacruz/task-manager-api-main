from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from src.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.MEMBER

class UserCreate(UserBase):
    password: str

class UserCreateByOwner(BaseModel):
    """Schema para que un owner cree nuevos usuarios"""
    email: EmailStr
    password: str
    role: UserRole

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)