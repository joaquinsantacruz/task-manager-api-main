from typing import List, Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.api import deps
from src.models.user import User
from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from src.services.comment import CommentService

router = APIRouter()


@router.get("/{task_id}/comments", response_model=List[CommentResponse])
async def get_task_comments(
    task_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> List[CommentResponse]:
    """
    Obtener todos los comentarios de una tarea.
    Solo el owner de la tarea o usuarios OWNER pueden ver los comentarios.
    """
    return await CommentService.get_task_comments(
        db=db,
        task_id=task_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> CommentResponse:
    """
    Crear un comentario en una tarea.
    Solo el owner de la tarea o usuarios OWNER pueden comentar.
    """
    return await CommentService.create_comment(
        db=db,
        task_id=task_id,
        comment_data=comment_data,
        current_user=current_user
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> CommentResponse:
    """
    Actualizar un comentario.
    Solo el autor del comentario puede editarlo.
    """
    return await CommentService.update_comment(
        db=db,
        comment_id=comment_id,
        comment_data=comment_data,
        current_user=current_user
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Eliminar un comentario.
    Solo el autor del comentario o un OWNER pueden eliminarlo.
    """
    await CommentService.delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )
