from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from src.api import deps
from src.core.constants import DEFAULT_PAGE_SIZE
from src.core.permissions import require_owner_role
from src.models.notification import Notification
from src.models.user import User
from src.schemas.notification import (
    NotificationResponse,
    UnreadCountResponse,
    NotificationGenerationResponse
)
from src.services.notification import NotificationService

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    notification_service: Annotated[NotificationService, Depends(deps.get_notification_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    unread_only: bool = False,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
) -> List[Notification]:
    """
    Get all notifications for the current user.
    
    Parameters:
    - unread_only: If True, only returns unread notifications
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    return await notification_service.get_user_notifications(
        current_user=current_user,
        unread_only=unread_only,
        skip=skip,
        limit=limit
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    notification_service: Annotated[NotificationService, Depends(deps.get_notification_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> UnreadCountResponse:
    """
    Get the count of unread notifications for the current user.
    """
    count = await notification_service.count_unread_notifications(
        current_user=current_user
    )
    return UnreadCountResponse(unread_count=count)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    notification_service: Annotated[NotificationService, Depends(deps.get_notification_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Notification:
    """
    Mark a notification as read.
    """
    return await notification_service.mark_notification_as_read(
        notification_id=notification_id,
        current_user=current_user
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    notification_service: Annotated[NotificationService, Depends(deps.get_notification_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Delete a notification.
    """
    await notification_service.delete_notification(
        notification_id=notification_id,
        current_user=current_user
    )


@router.post("/check-due-dates", response_model=NotificationGenerationResponse)
async def check_due_dates(
    notification_service: Annotated[NotificationService, Depends(deps.get_notification_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> NotificationGenerationResponse:
    """
    Generate notifications for tasks with upcoming or overdue dates.
    Only users with OWNER role can execute this function.
    
    This function reviews all tasks and generates notifications for:
    - Tasks due today
    - Tasks due in the next 24 hours
    - Overdue and incomplete tasks
    
    In production, this should run automatically with a scheduler.
    """
    require_owner_role(current_user)
    
    notifications_created = await notification_service.generate_due_date_notifications()
    
    return NotificationGenerationResponse(
        message="Notifications generated successfully",
        notifications_created=notifications_created,
        total=sum(notifications_created.values())
    )
