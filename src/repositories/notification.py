from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.models.notification import Notification
from src.core.constants import DEFAULT_PAGE_SIZE


class NotificationRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, notification_id: int) -> Optional[Notification]:
        """Gets a notification by its ID, including the task."""
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
        limit: int = DEFAULT_PAGE_SIZE
    ) -> List[Notification]:
        """Gets notifications for a user."""
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
        """Counts unread notifications for a user."""
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
        """Creates a new notification."""
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
        
        # Load the task relationship
        result = await db.scalars(
            select(Notification)
            .options(joinedload(Notification.task))
            .where(Notification.id == db_notification.id)
        )
        return result.one()
    
    @staticmethod
    async def mark_as_read(db: AsyncSession, notification: Notification) -> Notification:
        """Marks a notification as read."""
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def delete(db: AsyncSession, notification: Notification) -> None:
        """Deletes a notification."""
        await db.delete(notification)
        await db.commit()
    
    @staticmethod
    async def exists_for_task_and_type(
        db: AsyncSession,
        task_id: int,
        notification_type: str
    ) -> bool:
        """Checks if a notification of the specified type already exists for the task."""
        result = await db.execute(
            select(func.count(Notification.id))
            .where(Notification.task_id == task_id)
            .where(Notification.notification_type == notification_type)
            .where(Notification.is_read == False)
        )
        count = result.scalar_one()
        return count > 0
