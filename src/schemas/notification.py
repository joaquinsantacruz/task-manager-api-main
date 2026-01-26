from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
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
    task_title: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def extract_task_title(cls, data: Any) -> Any:
        """Extract the task title from the loaded relationship."""
        if hasattr(data, 'task') and data.task and hasattr(data.task, 'title'):
            if isinstance(data, dict):
                data['task_title'] = data.task.title
            else:
                result = {
                    'id': data.id,
                    'message': data.message,
                    'notification_type': data.notification_type,
                    'user_id': data.user_id,
                    'task_id': data.task_id,
                    'task_title': data.task.title,
                    'is_read': data.is_read,
                    'created_at': data.created_at
                }
                return result
        return data


class NotificationMarkRead(BaseModel):
    """Schema for marking a notification as read."""
    is_read: bool = True


class UnreadCountResponse(BaseModel):
    """Schema for unread notification count response."""
    unread_count: int


class NotificationGenerationResponse(BaseModel):
    """Schema for notification generation response."""
    message: str
    notifications_created: dict[str, int]
    total: int
