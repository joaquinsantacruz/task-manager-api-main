import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SqEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    status = Column(SqEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Clave Foránea
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación Inversa
    owner = relationship("src.models.user.User", back_populates="tasks")
    comments = relationship("src.models.comment.Comment", back_populates="task", cascade="all, delete-orphan")
    notifications = relationship("src.models.notification.Notification", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task id={self.id} title={self.title} status={self.status}>"