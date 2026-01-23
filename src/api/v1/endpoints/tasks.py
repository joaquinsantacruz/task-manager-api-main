from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.api import deps
from src.models.user import User
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.repositories.task import TaskRepository

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> List[Task]:
    """
    Recuperar tareas propias.
    """
    tasks = await TaskRepository.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return tasks

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
    task_in: TaskCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Crear una nueva tarea.
    """
    task = await TaskRepository.create(
        db=db, obj_in=task_in, owner_id=current_user.id
    )
    return task

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Task:
    """
    Obtener una tarea específica por ID (solo si te pertenece).
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
    Actualizar una tarea propia.
    """
    task = await TaskRepository.get_by_id_and_owner(
        db=db, id=task_id, owner_id=current_user.id
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
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
    Eliminar una tarea propia.
    """
    task = await TaskRepository.get_by_id_and_owner(
        db=db, id=task_id, owner_id=current_user.id
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await TaskRepository.delete(db=db, db_obj=task)