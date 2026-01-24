from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.api import deps
from src.models.user import User, UserRole
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.schemas.task_owner import ChangeOwnerRequest
from src.repositories.task import TaskRepository
from src.repositories.user import UserRepository
from src.services.task import TaskService
from src.core.constants import DEFAULT_PAGE_SIZE

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    only_mine: bool = False,
) -> List[Task]:
    """
    Retrieve own tasks.
    """
    return await TaskService.get_tasks_for_user(
        db=db,
        user=current_user,
        skip=skip,
        limit=limit,
        only_mine=only_mine
    )

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
    task_in: TaskCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Create a new task.
    """
    return await TaskService.create_task(
        db=db,
        task_data=task_in,
        current_user=current_user
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Get a specific task by ID (only if it belongs to you).
    """
    task = await TaskRepository.get_by_id_and_owner(
        db=db, id=task_id, owner_id=current_user.id
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
    task_in: TaskUpdate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Update own task.
    """
    task = await TaskService.get_task_for_action(db, task_id, current_user)
    
    task = await TaskRepository.update(db=db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
):
    """
    Delete own task.
    """
    task = await TaskService.get_task_for_action(db, task_id, current_user)
    
    await TaskRepository.delete(db=db, db_obj=task)

@router.patch("/{task_id}/owner", response_model=TaskResponse)
async def change_task_owner(
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
    owner_data: ChangeOwnerRequest,
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Change the owner of a task (OWNER role only).
    """
    return await TaskService.change_task_owner(
        db=db,
        task_id=task_id,
        new_owner_id=owner_data.owner_id,
        current_user=current_user
    )
