from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.core.constants import COMMENT_CONTENT_MIN_LENGTH, COMMENT_CONTENT_MAX_LENGTH


class CommentBase(BaseModel):
    content: str = Field(
        min_length=COMMENT_CONTENT_MIN_LENGTH,
        max_length=COMMENT_CONTENT_MAX_LENGTH,
        description=f"Comment content ({COMMENT_CONTENT_MIN_LENGTH}-{COMMENT_CONTENT_MAX_LENGTH} characters)"
    )


class CommentCreate(CommentBase):
    """Schema para crear un comentario en una tarea."""
    pass


class CommentUpdate(BaseModel):
    """Schema para actualizar un comentario."""
    content: str = Field(
        min_length=COMMENT_CONTENT_MIN_LENGTH,
        max_length=COMMENT_CONTENT_MAX_LENGTH,
        description=f"Comment content ({COMMENT_CONTENT_MIN_LENGTH}-{COMMENT_CONTENT_MAX_LENGTH} characters)"
    )


class CommentResponse(CommentBase):
    """Schema para la respuesta de un comentario."""
    id: int
    task_id: int
    author_id: int
    author_email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
