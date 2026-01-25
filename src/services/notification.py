from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.notification import Notification, NotificationType
from src.models.task import Task, TaskStatus
from src.models.user import User
from src.repositories.notification import NotificationRepository
from src.core.permissions import require_notification_access
from src.core.constants import DEFAULT_PAGE_SIZE
from src.core.errors import ERROR_NOTIFICATION_NOT_FOUND


class NotificationService:
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        current_user: User,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_SIZE
    ) -> List[Notification]:
        """
        Gets notifications for a user.
        """
        return await NotificationRepository.get_user_notifications(
            db=db,
            user_id=current_user.id,
            unread_only=unread_only,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    async def count_unread_notifications(
        db: AsyncSession,
        current_user: User
    ) -> int:
        """
        Counts unread notifications for a user.
        """
        return await NotificationRepository.count_unread(db, current_user.id)
    
    @staticmethod
    async def mark_notification_as_read(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> Notification:
        """
        Mark a notification as read.
        Only the notification owner can mark it as read.
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_NOTIFICATION_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_notification_access(current_user, notification)
        
        return await NotificationRepository.mark_as_read(db, notification)
    
    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> None:
        """
        Delete a notification.
        Only the notification owner can delete it.
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_NOTIFICATION_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_notification_access(current_user, notification)
        
        await NotificationRepository.delete(db, notification)
    
    @staticmethod
    async def generate_due_date_notifications(db: AsyncSession) -> dict:
        """
        Generates notifications for tasks with approaching or overdue due dates.
        This function should be called periodically (e.g., every hour or via a manual endpoint).
        
        Logic:
        - Tasks due today → "due_today" notification
        - Tasks due in the next 24 hours → "due_soon" notification
        - Overdue and incomplete tasks → "overdue" notification
        """
        now = datetime.now(timezone.utc)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        tomorrow_end = today_end + timedelta(days=1)
        
        notifications_created = {
            "due_today": 0,
            "due_soon": 0,
            "overdue": 0
        }
        
        # Get all tasks with due_date that are not completed
        result = await db.scalars(
            select(Task)
            .options(joinedload(Task.owner))
            .where(Task.due_date.isnot(None))
            .where(Task.status != TaskStatus.DONE)
        )
        tasks = list(result.all())
        
        for task in tasks:

            task_due_date = task.due_date
            if task_due_date.tzinfo is None:
                task_due_date = task_due_date.replace(tzinfo=timezone.utc)
            
            # Overdue task
            if task_due_date < now:
                # Check if an overdue notification already exists
                exists = await NotificationRepository.exists_for_task_and_type(
                    db, task.id, NotificationType.OVERDUE
                )
                if not exists:
                    await NotificationRepository.create(
                        db=db,
                        user_id=task.owner_id,
                        task_id=task.id,
                        notification_type=NotificationType.OVERDUE,
                        message=f"Task '{task.title}' is overdue"
                    )
                    notifications_created["overdue"] += 1
            
            # Task due today
            elif now <= task_due_date <= today_end:
                exists = await NotificationRepository.exists_for_task_and_type(
                    db, task.id, NotificationType.DUE_TODAY
                )
                if not exists:
                    await NotificationRepository.create(
                        db=db,
                        user_id=task.owner_id,
                        task_id=task.id,
                        notification_type=NotificationType.DUE_TODAY,
                        message=f"Task '{task.title}' is due today"
                    )
                    notifications_created["due_today"] += 1
            
            # Task due in the next 24 hours
            elif today_end < task_due_date <= tomorrow_end:
                exists = await NotificationRepository.exists_for_task_and_type(
                    db, task.id, NotificationType.DUE_SOON
                )
                if not exists:
                    await NotificationRepository.create(
                        db=db,
                        user_id=task.owner_id,
                        task_id=task.id,
                        notification_type=NotificationType.DUE_SOON,
                        message=f"Task '{task.title}' is due soon"
                    )
                    notifications_created["due_soon"] += 1
        
        return notifications_created
