from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.notification import Notification, NotificationType
from src.models.task import Task, TaskStatus
from src.models.user import User
from src.repositories.notification import NotificationRepository
from src.core.permissions import require_notification_access


class NotificationService:
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        current_user: User,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """
        Obtiene las notificaciones de un usuario.
        """
        return await NotificationRepository.get_user_notifications(
            db=db,
            user_id=current_user.id,
            unread_only=unread_only,
            skip=skip,
            limit=limit
        )
    
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
    ) -> Notification:
        """
        Mark a notification as read.
        Only the notification owner can mark it as read.
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify permissions using centralized function
        require_notification_access(current_user, notification)
        
        return await NotificationRepository.mark_as_read(db, notification)
    
    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: int,
        current_user: User
    ) -> None:
        """
        Delete a notification.
        Only the notification owner can delete it.
        """
        notification = await NotificationRepository.get_by_id(db, notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify permissions using centralized function
        require_notification_access(current_user, notification)
        
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
