from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from src.api import deps
from src.core.constants import DEFAULT_PAGE_SIZE
from src.models.comment import Comment
from src.models.user import User
from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from src.services.comment import CommentService

router = APIRouter()


@router.get("/{task_id}/comments", response_model=List[CommentResponse])
async def get_task_comments(
    task_id: int,
    comment_service: Annotated[CommentService, Depends(deps.get_comment_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
) -> List[Comment]:
    """
    Get all comments for a task.
    Only task owner or users with OWNER role can view comments.
    """
    return await comment_service.get_task_comments(
        task_id=task_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: int,
    comment_in: CommentCreate,
    comment_service: Annotated[CommentService, Depends(deps.get_comment_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Comment:
    """
    Create a comment on a task.
    Only task owner or users with OWNER role can comment.
    """
    return await comment_service.create_comment(
        task_id=task_id,
        comment_in=comment_in,
        current_user=current_user
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    comment_service: Annotated[CommentService, Depends(deps.get_comment_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Comment:
    """
    Update a comment.
    Only the comment author can edit it.
    """
    return await comment_service.update_comment(
        comment_id=comment_id,
        comment_in=comment_in,
        current_user=current_user
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    comment_service: Annotated[CommentService, Depends(deps.get_comment_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Delete a comment.
    Only the comment author or users with OWNER role can delete it.
    """
    await comment_service.delete_comment(
        comment_id=comment_id,
        current_user=current_user
    )
