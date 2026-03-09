from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from src.api import deps
from src.core.constants import DEFAULT_PAGE_SIZE
from src.models.task import Task
from src.models.user import User
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.schemas.task_owner import ChangeOwnerRequest
from src.services.task import TaskService

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    task_service: Annotated[TaskService, Depends(deps.get_task_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    only_mine: bool = False,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
) -> List[Task]:
    """
    Retrieve own tasks.
    """
    return await task_service.get_tasks_for_user(
        user=current_user,
        skip=skip,
        limit=limit,
        only_mine=only_mine
    )

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    task_service: Annotated[TaskService, Depends(deps.get_task_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Create a new task.
    """
    return await task_service.create_task(
        task_data=task_in,
        current_user=current_user
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: int,
    task_service: Annotated[TaskService, Depends(deps.get_task_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Get a specific task by ID (only if it belongs to you).
    """
    return await task_service.get_task_by_id_for_user(task_id, current_user)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    task_service: Annotated[TaskService, Depends(deps.get_task_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Update own task.
    """
    return await task_service.update_task(
        task_id=task_id, 
        task_in=task_in, 
        current_user=current_user
    )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    task_service: Annotated[TaskService, Depends(deps.get_task_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Delete own task.
    """
    await task_service.delete_task(
        task_id=task_id, 
        current_user=current_user
    )

@router.patch("/{task_id}/owner", response_model=TaskResponse)
async def change_task_owner(
    task_id: int,
    owner_data: ChangeOwnerRequest,
    task_service: Annotated[TaskService, Depends(deps.get_task_service)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Change the owner of a task (OWNER role only).
    """
    return await task_service.change_task_owner(
        task_id=task_id,
        new_owner_id=owner_data.owner_id,
        current_user=current_user
    )
