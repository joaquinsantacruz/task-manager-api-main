from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.core import security
from src.core.config import settings
from src.db.session import get_db
from src.models.user import User, UserRole
from src.repositories.user import UserRepository
from src.schemas.token import TokenPayload
from src.core.errors import ERROR_INVALID_CREDENTIALS, ERROR_INSUFFICIENT_PERMISSIONS

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_INVALID_CREDENTIALS,
        )
    
    user = await UserRepository.get_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_INVALID_CREDENTIALS
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_INVALID_CREDENTIALS
        )
    
    return user

async def get_current_owner(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Verify that the current user has OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_INSUFFICIENT_PERMISSIONS
        )
    return current_user