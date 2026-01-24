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
    Get all comments for a task.
    Only task owner or users with OWNER role can view comments.
    """
    comments = await CommentService.get_task_comments(
        db=db,
        task_id=task_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    
    return [
        CommentResponse(
            id=comment.id,
            content=comment.content,
            task_id=comment.task_id,
            author_id=comment.author_id,
            author_email=comment.author.email if comment.author else None,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        for comment in comments
    ]


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> CommentResponse:
    """
    Create a comment on a task.
    Only task owner or users with OWNER role can comment.
    """
    comment = await CommentService.create_comment(
        db=db,
        task_id=task_id,
        comment_data=comment_data,
        current_user=current_user
    )
    
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        task_id=comment.task_id,
        author_id=comment.author_id,
        author_email=comment.author.email if comment.author else None,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> CommentResponse:
    """
    Update a comment.
    Only the comment author can edit it.
    """
    comment = await CommentService.update_comment(
        db=db,
        comment_id=comment_id,
        comment_data=comment_data,
        current_user=current_user
    )
    
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        task_id=comment.task_id,
        author_id=comment.author_id,
        author_email=comment.author.email if comment.author else None,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Delete a comment.
    Only the comment author or users with OWNER role can delete it.
    """
    await CommentService.delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )
