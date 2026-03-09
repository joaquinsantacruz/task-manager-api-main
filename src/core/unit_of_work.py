from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user import UserRepository
from src.repositories.task import TaskRepository
from src.repositories.comment import CommentRepository
from src.repositories.notification import NotificationRepository


class UnitOfWork:
    """
    Unit of Work pattern to manage transactions and repository access.
    This ensures that all repository operations within a single request
    share the same database session and can be committed or rolled back
    as a single atomic transaction.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(self.session)
        self.tasks = TaskRepository(self.session)
        self.comments = CommentRepository(self.session)
        self.notifications = NotificationRepository(self.session)

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()

    async def flush(self):
        """Flush pending changes to the database without committing."""
        await self.session.flush()
