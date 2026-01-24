from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.notification import NotificationType
from src.models.task import Task, TaskStatus
from src.models.user import User
from src.schemas.notification import NotificationResponse
from src.repositories.notification import NotificationRepository


class NotificationService:
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        current_user: User,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[NotificationResponse]:
        """
        Obtiene las notificaciones de un usuario.
        """
        notifications = await NotificationRepository.get_user_notifications(
            db=db,
            user_id=current_user.id,
            unread_only=unread_only,
            skip=skip,
            limit=limit
        )
        
        return [
            NotificationResponse(
                id=notif.id,
                message=notif.message,
                notification_type=notif.notification_type,
                user_id=notif.user_id,
                task_id=notif.task_id,
                task_title=notif.task.title if notif.task else None,
                is_read=notif.is_read,
                created_at=notif.created_at
            )
            for notif in notifications
        ]
    
    @staticmethod
    async def count_unread_notifications(
        db: AsyncSession,
        current_user: User
    ) -> int:
        """
        Cuenta las notificaciones no leídas de un usuario.
        """
        return await NotificationRepository.count_unread(db, current_user.id)
    
    @staticmethod
    async def mark_notification_as_read(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> NotificationResponse:
        """
        Marca una notificación como leída.
        Solo el propietario de la notificación puede marcarla como leída.
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
        
        # Verificar que la notificación pertenece al usuario actual
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar esta notificación"
            )
        
        updated_notification = await NotificationRepository.mark_as_read(db, notification)
        
        return NotificationResponse(
            id=updated_notification.id,
            message=updated_notification.message,
            notification_type=updated_notification.notification_type,
            user_id=updated_notification.user_id,
            task_id=updated_notification.task_id,
            task_title=updated_notification.task.title if updated_notification.task else None,
            is_read=updated_notification.is_read,
            created_at=updated_notification.created_at
        )
    
    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> None:
        """
        Elimina una notificación.
        Solo el propietario de la notificación puede eliminarla.
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
        
        # Verificar que la notificación pertenece al usuario actual
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar esta notificación"
            )
        
        await NotificationRepository.delete(db, notification)
    
    @staticmethod
    async def generate_due_date_notifications(db: AsyncSession) -> dict:
        """
        Genera notificaciones para tareas con fechas de vencimiento próximas o vencidas.
        Esta función debe ser llamada periódicamente (ej: cada hora o mediante un endpoint manual).
        
        Lógica:
        - Tareas que vencen hoy → notificación "due_today"
        - Tareas que vencen en las próximas 24 horas → notificación "due_soon"
        - Tareas vencidas y no completadas → notificación "overdue"
        """
        now = datetime.now(timezone.utc)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        tomorrow_end = today_end + timedelta(days=1)
        
        notifications_created = {
            "due_today": 0,
            "due_soon": 0,
            "overdue": 0
        }
        
        # Obtener todas las tareas con due_date que no están completadas
        result = await db.scalars(
            select(Task)
            .options(joinedload(Task.owner))
            .where(Task.due_date.isnot(None))
            .where(Task.status != TaskStatus.DONE)
        )
        tasks = list(result.all())
        
        for task in tasks:
            # Asegurar que due_date es timezone-aware
            task_due_date = task.due_date
            if task_due_date.tzinfo is None:
                task_due_date = task_due_date.replace(tzinfo=timezone.utc)
            
            # Tarea vencida
            if task_due_date < now:
                # Verificar si ya existe una notificación de overdue
                exists = await NotificationRepository.exists_for_task_and_type(
                    db, task.id, NotificationType.OVERDUE
                )
                if not exists:
                    await NotificationRepository.create(
                        db=db,
                        user_id=task.owner_id,
                        task_id=task.id,
                        notification_type=NotificationType.OVERDUE,
                        message=f"La tarea '{task.title}' está vencida"
                    )
                    notifications_created["overdue"] += 1
            
            # Tarea vence hoy
            elif now <= task_due_date <= today_end:
                exists = await NotificationRepository.exists_for_task_and_type(
                    db, task.id, NotificationType.DUE_TODAY
                )
                if not exists:
                    await NotificationRepository.create(
                        db=db,
                        user_id=task.owner_id,
                        task_id=task.id,
                        notification_type=NotificationType.DUE_TODAY,
                        message=f"La tarea '{task.title}' vence hoy"
                    )
                    notifications_created["due_today"] += 1
            
            # Tarea vence en las próximas 24 horas
            elif today_end < task_due_date <= tomorrow_end:
                exists = await NotificationRepository.exists_for_task_and_type(
                    db, task.id, NotificationType.DUE_SOON
                )
                if not exists:
                    await NotificationRepository.create(
                        db=db,
                        user_id=task.owner_id,
                        task_id=task.id,
                        notification_type=NotificationType.DUE_SOON,
                        message=f"La tarea '{task.title}' vence pronto"
                    )
                    notifications_created["due_soon"] += 1
        
        return notifications_created
