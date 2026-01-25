from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.core.constants import COMMENT_CONTENT_MIN_LENGTH, COMMENT_CONTENT_MAX_LENGTH


class CommentBase(BaseModel):
    content: str = Field(
        min_length=COMMENT_CONTENT_MIN_LENGTH,
        max_length=COMMENT_CONTENT_MAX_LENGTH,
        description=f"Comment content ({COMMENT_CONTENT_MIN_LENGTH}-{COMMENT_CONTENT_MAX_LENGTH} characters)"
    )


class CommentCreate(CommentBase):
    """Schema for creating a comment on a task."""
    pass


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: str = Field(
        min_length=COMMENT_CONTENT_MIN_LENGTH,
        max_length=COMMENT_CONTENT_MAX_LENGTH,
        description=f"Comment content ({COMMENT_CONTENT_MIN_LENGTH}-{COMMENT_CONTENT_MAX_LENGTH} characters)"
    )


class CommentResponse(CommentBase):
    """Schema for comment response."""
    id: int
    task_id: int
    author_id: int
    author_email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def extract_author_email(cls, data: Any) -> Any:
        """Extract the author's email from the loaded relationship."""
        if hasattr(data, 'author') and data.author and hasattr(data.author, 'email'):
            if isinstance(data, dict):
                data['author_email'] = data.author.email
            else:
                result = {
                    'id': data.id,
                    'content': data.content,
                    'task_id': data.task_id,
                    'author_id': data.author_id,
                    'author_email': data.author.email,
                    'created_at': data.created_at,
                    'updated_at': data.updated_at
                }
                return result
        return data
