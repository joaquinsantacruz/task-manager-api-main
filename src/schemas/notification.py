from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.models.notification import NotificationType


class NotificationBase(BaseModel):
    message: str
    notification_type: NotificationType


class NotificationResponse(NotificationBase):
    """Schema para la respuesta de una notificación."""
    id: int
    user_id: int
    task_id: int
    task_title: str | None = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationMarkRead(BaseModel):
    """Schema para marcar notificación como leída."""
    is_read: bool = True
