from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import security
from src.core.config import settings
from src.core.logger import get_logger
from src.db.session import get_db
from src.repositories.user import UserRepository
from src.schemas.token import Token
from src.core.errors import ERROR_INCORRECT_EMAIL_OR_PASSWORD, ERROR_INACTIVE_USER

logger = get_logger(__name__)
router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    logger.info(f"Login attempt for email: {form_data.username}")
    
    user = await UserRepository.get_by_email(db, email=form_data.username)

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INCORRECT_EMAIL_OR_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"Inactive user login attempt: {user.id} ({form_data.username})")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_INACTIVE_USER)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user {user.id} ({user.email})")
    return Token(access_token=access_token, token_type="bearer")