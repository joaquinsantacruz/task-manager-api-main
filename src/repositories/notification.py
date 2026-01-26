from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.models.notification import Notification
from src.core.constants import DEFAULT_PAGE_SIZE


class NotificationRepository:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, notification_id: int) -> Optional[Notification]:
        """
        Retrieve a notification by its unique identifier with task relationship loaded.
        
        This method fetches a single notification and eagerly loads its associated
        task to avoid N+1 query problems.
        
        Args:
            db: Async database session for executing queries
            notification_id: Unique identifier of the notification to retrieve
        
        Returns:
            Optional[Notification]: Notification object with task relationship loaded if found,
                                   None if no notification exists with the given ID
        
        Note:
            - Eagerly loads task relationship via joinedload
            - Does not load user relationship (only task)
            - Returns None rather than raising exception if not found
            - Does not verify notification ownership
        """
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
        """
        Retrieve notifications for a specific user with optional filtering and pagination.
        
        This method returns notifications belonging to a user, ordered by creation
        date (newest first). Can optionally filter to show only unread notifications.
        
        Args:
            db: Async database session for executing queries
            user_id: ID of the user whose notifications to retrieve
            unread_only: If True, return only unread notifications (is_read = False).
                        If False, return all notifications. Default is False.
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of notifications to return (default: DEFAULT_PAGE_SIZE)
        
        Returns:
            List[Notification]: List of notification objects with task relationships loaded,
                               ordered by created_at DESC (newest first).
                               Returns empty list if user has no notifications.
        
        Note:
            - Results are ordered by created_at in descending order (newest first)
            - Task relationship is eagerly loaded for each notification
            - Filtering by unread_only is applied at database level (efficient)
            - User relationship is NOT loaded (only task)
        """
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
        """
        Count the total number of unread notifications for a specific user.
        
        This is a lightweight query that returns only the count without fetching
        the notification objects themselves, making it ideal for badge counters
        and real-time polling.
        
        Args:
            db: Async database session for executing queries
            user_id: ID of the user whose unread notifications should be counted
        
        Returns:
            int: Total count of unread notifications (is_read = False).
                Returns 0 if user has no unread notifications.
        
        Note:
            - Performs COUNT query (does not load notification objects)
            - Only counts notifications where is_read = False
            - Efficient for frequent polling (notification badges)
            - Does not include notification details (just the count)
        """
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
        """
        Create a new notification for a user about a task event.
        
        This method creates a notification in the database with is_read set to False,
        commits it, and returns the fully loaded notification object.
        
        Args:
            db: Async database session for executing queries
            user_id: ID of the user who will receive this notification
            task_id: ID of the task this notification is about
            notification_type: Type of notification (e.g., "due_today", "overdue", "due_soon")
            message: Human-readable notification message
        
        Returns:
            Notification: Newly created notification object with:
                - Auto-generated ID
                - is_read set to False
                - created_at timestamp auto-populated
                - Task relationship eagerly loaded
        
        Note:
            - Commits transaction immediately
            - All new notifications are created as unread (is_read = False)
            - Performs additional query to eager load task relationship
            - Does not validate if user_id or task_id exist (foreign key constraints apply)
        """
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
        """
        Mark a notification as read by setting is_read to True.
        
        This method updates the notification's read status and commits the change
        to the database immediately.
        
        Args:
            db: Async database session for executing queries
            notification: Notification object to mark as read
        
        Returns:
            Notification: Updated notification object with is_read = True
        
        Note:
            - Sets is_read = True regardless of current value (idempotent)
            - Commits transaction immediately
            - Does not record timestamp of when notification was read
            - Does not validate notification ownership (must be checked before calling)
        """
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def delete(db: AsyncSession, notification: Notification) -> None:
        """
        Permanently delete a notification from the database.
        
        This method performs a hard delete, completely removing the notification
        from the system.
        
        Args:
            db: Async database session for executing queries
            notification: Notification object to delete
        
        Returns:
            None
        
        Note:
            - This is a hard delete (not soft delete)
            - Commits transaction immediately
            - Cannot be undone after commit
            - Does not validate notification ownership (must be checked before calling)
        """
        await db.delete(notification)
        await db.commit()
    
    @staticmethod
    async def exists_for_task_and_type(
        db: AsyncSession,
        task_id: int,
        notification_type: str
    ) -> bool:
        """
        Check if an unread notification of a specific type already exists for a task.
        
        This method prevents duplicate notifications by checking if an unread
        notification of the same type already exists for the given task.
        
        Args:
            db: Async database session for executing queries
            task_id: ID of the task to check
            notification_type: Type of notification to check for (e.g., "overdue", "due_today")
        
        Returns:
            bool: True if at least one unread notification of this type exists for the task,
                 False if no such notification exists or all are marked as read
        
        Note:
            - Only checks unread notifications (is_read = False)
            - Used to prevent duplicate notifications in scheduled jobs
            - Performs efficient COUNT query (doesn't load notification objects)
            - Returns False if count is 0, True if count > 0
            - Read notifications are ignored (allows creating new notifications if user already read previous ones)
        """
        result = await db.execute(
            select(func.count(Notification.id))
            .where(Notification.task_id == task_id)
            .where(Notification.notification_type == notification_type)
            .where(Notification.is_read == False)
        )
        count = result.scalar_one()
        return count > 0
