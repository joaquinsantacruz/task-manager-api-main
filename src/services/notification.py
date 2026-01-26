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
from src.core.logger import get_logger

logger = get_logger(__name__)


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
        Retrieve notifications for the authenticated user with pagination support.
        
        This method allows users to fetch their notification history, with the option
        to filter only unread notifications. Notifications are returned in reverse
        chronological order (newest first).
        
        Args:
            db: Async database session for executing queries
            current_user: The authenticated user requesting their notifications
            unread_only: If True, return only unread notifications. If False, return all.
                        Default is False.
            skip: Number of notifications to skip for pagination. Default is 0.
            limit: Maximum number of notifications to return. Default is DEFAULT_PAGE_SIZE.
        
        Returns:
            List[Notification]: List of notification objects matching the criteria.
                               Empty list if no notifications are found.
        
        Note:
            - Users can only access their own notifications
            - Notifications include task-related alerts (due dates, overdue, assignments)
            - Each notification includes type, message, timestamp, and read status
        """
        logger.debug(f"User {current_user.id} fetching notifications (unread_only={unread_only}, skip={skip}, limit={limit})")
        notifications = await NotificationRepository.get_user_notifications(
            db=db,
            user_id=current_user.id,
            unread_only=unread_only,
            skip=skip,
            limit=limit
        )
        logger.debug(f"Retrieved {len(notifications)} notifications for user {current_user.id}")
        return notifications
    
    @staticmethod
    async def count_unread_notifications(
        db: AsyncSession,
        current_user: User
    ) -> int:
        """
        Count the total number of unread notifications for the authenticated user.
        
        This method is typically used to display notification badges or counters
        in the user interface, showing how many new notifications require attention.
        
        Args:
            db: Async database session for executing queries
            current_user: The authenticated user whose unread notifications will be counted
        
        Returns:
            int: Total count of unread notifications. Returns 0 if no unread notifications exist.
        
        Note:
            - Only counts notifications where is_read = False
            - Users can only count their own notifications
            - This is a lightweight query optimized for frequent polling
        """
        return await NotificationRepository.count_unread(db, current_user.id)
    
    @staticmethod
    async def mark_notification_as_read(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> Notification:
        """
        Mark a specific notification as read for the authenticated user.
        
        This method updates the notification's is_read flag to True and records
        the timestamp when the notification was read. Only the notification owner
        can mark their own notifications as read.
        
        Args:
            db: Async database session for executing queries
            notification_id: Unique identifier of the notification to mark as read
            current_user: The authenticated user who owns the notification
        
        Returns:
            Notification: The updated notification object with is_read = True
        
        Raises:
            HTTPException 404: If notification with the given ID doesn't exist
            HTTPException 403: If current user doesn't own the notification
        
        Security:
            - Permission check ensures users can only mark their own notifications
            - Uses centralized permission validation (require_notification_access)
        """
        logger.info(f"User {current_user.id} marking notification {notification_id} as read")
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            logger.warning(f"Notification {notification_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_NOTIFICATION_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_notification_access(current_user, notification)
        
        try:
            updated_notification = await NotificationRepository.mark_as_read(db, notification)
            logger.info(f"Notification {notification_id} marked as read by user {current_user.id}")
            return updated_notification
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> None:
        """
        Permanently delete a notification from the system.
        
        This method removes a notification from the database entirely. Only the
        notification owner can delete their own notifications. This action cannot
        be undone.
        
        Args:
            db: Async database session for executing queries
            notification_id: Unique identifier of the notification to delete
            current_user: The authenticated user who owns the notification
        
        Returns:
            None
        
        Raises:
            HTTPException 404: If notification with the given ID doesn't exist
            HTTPException 403: If current user doesn't own the notification
        
        Security:
            - Permission check ensures users can only delete their own notifications
            - Uses centralized permission validation (require_notification_access)
        
        Note:
            - This is a hard delete operation (not soft delete)
            - Consider marking as read instead if notification history is needed
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            logger.warning(f"Notification {notification_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_NOTIFICATION_NOT_FOUND
            )
        
        # Verify permissions using centralized function
        require_notification_access(current_user, notification)
        
        try:
            logger.info(f"User {current_user.id} deleting notification {notification_id}")
            await NotificationRepository.delete(db, notification)
            logger.info(f"Notification {notification_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_due_date_notifications(db: AsyncSession) -> dict:
        """
        Generate automated notifications for tasks based on their due dates.
        
        This function scans all active (non-completed) tasks and creates appropriate
        notifications based on their due date status. It should be called periodically
        by a scheduled job (e.g., cron, celery beat) or manually triggered via an endpoint.
        
        Notification Logic:
            - Overdue tasks (due_date < now): Creates "overdue" notification
            - Tasks due today (due_date between now and end of today): Creates "due_today" notification  
            - Tasks due soon (due_date in next 24 hours): Creates "due_soon" notification
        
        Args:
            db: Async database session for executing queries
        
        Returns:
            dict: Summary of notifications created with keys:
                - "due_today" (int): Count of due today notifications created
                - "due_soon" (int): Count of due soon notifications created
                - "overdue" (int): Count of overdue notifications created
        
        Behavior:
            - Only processes tasks with status != DONE
            - Prevents duplicate notifications by checking if notification already exists
            - Each task can have only one notification per type
            - All timestamps are handled in UTC timezone
            - Notifications are sent to the task owner (owner_id)
        
        Example Return:
            {"due_today": 3, "due_soon": 5, "overdue": 2}
        
        Note:
            - This is an idempotent operation (safe to run multiple times)
            - Recommended execution frequency: every 1-6 hours
            - Does not delete or update existing notifications
            - Task completion status changes won't remove existing notifications
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
