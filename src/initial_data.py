import asyncio
import logging
from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.user import User, UserRole
from src.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_first_user():
    logger.info("Creando usuario inicial")
    
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(User).where(User.email == "admin@admin.com")
        )
        user = result.one_or_none()
        
        if user:
            logger.info("User 'admin@admin.com' ya existe. Saltando creación.")
        else:
            new_user = User(
                email="admin@admin.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.OWNER,
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            logger.info("Superusuario creado: admin@admin.com / admin123")

if __name__ == "__main__":
    asyncio.run(create_first_user())