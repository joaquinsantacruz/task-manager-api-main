from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from src.models.user import UserRole
from src.core.constants import USER_PASSWORD_MIN_LENGTH, USER_PASSWORD_MAX_LENGTH

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.MEMBER

class UserCreate(UserBase):
    password: str = Field(
        min_length=USER_PASSWORD_MIN_LENGTH,
        max_length=USER_PASSWORD_MAX_LENGTH,
        description=f"User password ({USER_PASSWORD_MIN_LENGTH}-{USER_PASSWORD_MAX_LENGTH} characters)"
    )

class UserCreateByOwner(BaseModel):
    """Schema for an owner to create new users"""
    email: EmailStr
    password: str = Field(
        min_length=USER_PASSWORD_MIN_LENGTH,
        max_length=USER_PASSWORD_MAX_LENGTH,
        description=f"User password ({USER_PASSWORD_MIN_LENGTH}-{USER_PASSWORD_MAX_LENGTH} characters)"
    )
    role: UserRole

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)