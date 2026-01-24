from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    """Schema para crear un comentario en una tarea."""
    pass


class CommentUpdate(BaseModel):
    """Schema para actualizar un comentario."""
    content: str


class CommentResponse(CommentBase):
    """Schema para la respuesta de un comentario."""
    id: int
    task_id: int
    author_id: int
    author_email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
