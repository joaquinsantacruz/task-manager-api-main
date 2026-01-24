import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SqEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base

class UserRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    role = Column(SqEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tasks = relationship("src.models.task.Task", back_populates="owner", cascade="all, delete-orphan")
    comments = relationship("src.models.comment.Comment", back_populates="author", cascade="all, delete-orphan")
    notifications = relationship("src.models.notification.Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User email={self.email} role={self.role}>"