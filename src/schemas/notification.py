from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.models.notification import NotificationType
from src.core.constants import NOTIFICATION_MESSAGE_MAX_LENGTH


class NotificationBase(BaseModel):
    message: str = Field(
        max_length=NOTIFICATION_MESSAGE_MAX_LENGTH,
        description=f"Notification message (max {NOTIFICATION_MESSAGE_MAX_LENGTH} characters)"
    )
    notification_type: NotificationType


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    id: int
    user_id: int
    task_id: int
    task_title: str | None = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationMarkRead(BaseModel):
    """Schema for marking a notification as read."""
    is_read: bool = True
