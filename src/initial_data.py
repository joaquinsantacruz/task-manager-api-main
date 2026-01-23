import asyncio
import logging
from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.user import User, UserRole
from src.core.security import get_password_hash

# Configuración básica de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_first_user():
    logger.info("Creando usuario inicial")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "admin@admin.com"))
        user = result.scalar_one_or_none()
        
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