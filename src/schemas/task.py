from typing import Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, model_validator, field_validator, Field
from src.models.task import TaskStatus
from src.core.constants import (
    TASK_TITLE_MIN_LENGTH,
    TASK_TITLE_MAX_LENGTH,
    TASK_DESCRIPTION_MAX_LENGTH
)

class TaskBase(BaseModel):
    title: str = Field(
        min_length=TASK_TITLE_MIN_LENGTH,
        max_length=TASK_TITLE_MAX_LENGTH,
        description=f"Task title ({TASK_TITLE_MIN_LENGTH}-{TASK_TITLE_MAX_LENGTH} characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=TASK_DESCRIPTION_MAX_LENGTH,
        description=f"Task description (max {TASK_DESCRIPTION_MAX_LENGTH} characters)"
    )
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date_not_past(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due_date is not in the past."""
        if v is not None:
            # Make both timezone-aware for comparison
            now = datetime.now(timezone.utc)
            due_date = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            
            if due_date < now:
                raise ValueError('Due date cannot be in the past')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=TASK_TITLE_MIN_LENGTH,
        max_length=TASK_TITLE_MAX_LENGTH,
        description=f"Task title ({TASK_TITLE_MIN_LENGTH}-{TASK_TITLE_MAX_LENGTH} characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=TASK_DESCRIPTION_MAX_LENGTH,
        description=f"Task description (max {TASK_DESCRIPTION_MAX_LENGTH} characters)"
    )
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date_not_past(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due_date is not in the past."""
        if v is not None:
            # Make both timezone-aware for comparison
            now = datetime.now(timezone.utc)
            due_date = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            
            if due_date < now:
                raise ValueError('Due date cannot be in the past')
        return v

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def extract_owner_email(cls, data: Any) -> Any:
        """Extrae el email del owner desde la relación cargada."""
        # Si data es un objeto SQLAlchemy (tiene atributos)
        if hasattr(data, 'owner') and data.owner and hasattr(data.owner, 'email'):
            # Si es un dict, actualizamos
            if isinstance(data, dict):
                data['owner_email'] = data.owner.email
            # Si es un objeto, creamos un dict con los valores
            else:
                # Convertir el objeto SQLAlchemy a dict
                result = {
                    'id': data.id,
                    'title': data.title,
                    'description': data.description,
                    'status': data.status,
                    'due_date': data.due_date,
                    'owner_id': data.owner_id,
                    'created_at': data.created_at,
                    'updated_at': data.updated_at,
                    'owner_email': data.owner.email
                }
                return result
        return data