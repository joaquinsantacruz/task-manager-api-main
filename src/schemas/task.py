from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator
from src.models.task import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

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
                    'owner_id': data.owner_id,
                    'created_at': data.created_at,
                    'updated_at': data.updated_at,
                    'owner_email': data.owner.email
                }
                return result
        return data