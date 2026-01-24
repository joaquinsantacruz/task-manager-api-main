from typing import List, Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.api import deps
from src.models.user import User
from src.models.notification import Notification
from src.schemas.notification import NotificationResponse
from src.services.notification import NotificationService

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> List[NotificationResponse]:
    """
    Get all notifications for the current user.
    
    Parameters:
    - unread_only: If True, only returns unread notifications
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    notifications = await NotificationService.get_user_notifications(
        db=db,
        current_user=current_user,
        unread_only=unread_only,
        skip=skip,
        limit=limit
    )
    
    return [
        NotificationResponse(
            id=notif.id,
            message=notif.message,
            notification_type=notif.notification_type,
            user_id=notif.user_id,
            task_id=notif.task_id,
            task_title=notif.task.title if notif.task else None,
            is_read=notif.is_read,
            created_at=notif.created_at
        )
        for notif in notifications
    ]


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> dict:
    """
    Get the count of unread notifications for the current user.
    """
    count = await NotificationService.count_unread_notifications(
        db=db,
        current_user=current_user
    )
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> NotificationResponse:
    """
    Mark a notification as read.
    """
    notification = await NotificationService.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )
    
    return NotificationResponse(
        id=notification.id,
        message=notification.message,
        notification_type=notification.notification_type,
        user_id=notification.user_id,
        task_id=notification.task_id,
        task_title=notification.task.title if notification.task else None,
        is_read=notification.is_read,
        created_at=notification.created_at
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Delete a notification.
    """
    await NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )


@router.post("/check-due-dates", response_model=dict)
async def check_due_dates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_owner)],
) -> dict:
    """
    Generate notifications for tasks with upcoming or overdue dates.
    Only users with OWNER role can execute this function.
    
    This function reviews all tasks and generates notifications for:
    - Tasks due today
    - Tasks due in the next 24 hours
    - Overdue and incomplete tasks
    
    In production, this should run automatically with a scheduler.
    """
    notifications_created = await NotificationService.generate_due_date_notifications(db)
    
    return {
        "message": "Notificaciones generadas exitosamente",
        "notifications_created": notifications_created,
        "total": sum(notifications_created.values())
    }
