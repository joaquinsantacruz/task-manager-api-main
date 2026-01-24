from typing import List, Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.api import deps
from src.models.user import User
from src.schemas.notification import NotificationResponse
from src.services.notification import NotificationService

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> List[NotificationResponse]:
    """
    Obtener todas las notificaciones del usuario actual.
    
    Parámetros:
    - unread_only: Si es True, solo devuelve notificaciones no leídas
    - skip: Número de registros a saltar (paginación)
    - limit: Número máximo de registros a devolver
    """
    return await NotificationService.get_user_notifications(
        db=db,
        current_user=current_user,
        unread_only=unread_only,
        skip=skip,
        limit=limit
    )


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> dict:
    """
    Obtener el número de notificaciones no leídas del usuario actual.
    """
    count = await NotificationService.count_unread_notifications(
        db=db,
        current_user=current_user
    )
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> NotificationResponse:
    """
    Marcar una notificación como leída.
    """
    return await NotificationService.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> None:
    """
    Eliminar una notificación.
    """
    await NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )


@router.post("/check-due-dates", response_model=dict)
async def check_due_dates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_owner)],
) -> dict:
    """
    Generar notificaciones para tareas con fechas de vencimiento.
    Solo usuarios OWNER pueden ejecutar esta función.
    
    Esta función revisa todas las tareas y genera notificaciones para:
    - Tareas que vencen hoy
    - Tareas que vencen en las próximas 24 horas
    - Tareas vencidas y no completadas
    
    En producción, esto debería ejecutarse automáticamente con un scheduler.
    """
    notifications_created = await NotificationService.generate_due_date_notifications(db)
    
    return {
        "message": "Notificaciones generadas exitosamente",
        "notifications_created": notifications_created,
        "total": sum(notifications_created.values())
    }
