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
            detail="Could not validate credentials",
        )
    
    user = await UserRepository.get_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_current_owner(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Verifica que el usuario actual tenga rol de OWNER.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol de OWNER."
        )
    return current_user