import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum as SqEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base


class NotificationType(str, enum.Enum):
    DUE_SOON = "due_soon"      # Task due in the next 24 hours
    OVERDUE = "overdue"        # Overdue task
    DUE_TODAY = "due_today"    # Task due today


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(500), nullable=False)
    notification_type = Column(SqEnum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("src.models.user.User", back_populates="notifications")
    task = relationship("src.models.task.Task", back_populates="notifications")

    def __repr__(self):
        return f"<Notification id={self.id} type={self.notification_type} user_id={self.user_id}>"
