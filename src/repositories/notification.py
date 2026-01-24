from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.models.notification import Notification


class NotificationRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, notification_id: int) -> Optional[Notification]:
        """Obtiene una notificación por su ID, incluyendo task."""
        result = await db.scalars(
            select(Notification)
            .options(joinedload(Notification.task))
            .where(Notification.id == notification_id)
        )
        return result.one_or_none()
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession, 
        user_id: int, 
        unread_only: bool = False,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """Obtiene las notificaciones de un usuario."""
        query = (
            select(Notification)
            .options(joinedload(Notification.task))
            .where(Notification.user_id == user_id)
        )
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.scalars(query)
        return list(result.all())
    
    @staticmethod
    async def count_unread(db: AsyncSession, user_id: int) -> int:
        """Cuenta las notificaciones no leídas de un usuario."""
        result = await db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )
        return result.scalar_one()
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        task_id: int,
        notification_type: str,
        message: str
    ) -> Notification:
        """Crea una nueva notificación."""
        db_notification = Notification(
            user_id=user_id,
            task_id=task_id,
            notification_type=notification_type,
            message=message,
            is_read=False
        )
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)
        
        # Cargar la relación del task
        result = await db.scalars(
            select(Notification)
            .options(joinedload(Notification.task))
            .where(Notification.id == db_notification.id)
        )
        return result.one()
    
    @staticmethod
    async def mark_as_read(db: AsyncSession, notification: Notification) -> Notification:
        """Marca una notificación como leída."""
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def delete(db: AsyncSession, notification: Notification) -> None:
        """Elimina una notificación."""
        await db.delete(notification)
        await db.commit()
    
    @staticmethod
    async def exists_for_task_and_type(
        db: AsyncSession,
        task_id: int,
        notification_type: str
    ) -> bool:
        """Verifica si ya existe una notificación del tipo especificado para la tarea."""
        result = await db.execute(
            select(func.count(Notification.id))
            .where(Notification.task_id == task_id)
            .where(Notification.notification_type == notification_type)
            .where(Notification.is_read == False)
        )
        count = result.scalar_one()
        return count > 0
