from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate
from src.core.constants import DEFAULT_PAGE_SIZE

class TaskRepository:
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession, id: int
    ) -> Optional[Task]:
        """
        Retrieve a task by its unique identifier with owner relationship loaded.
        
        This method fetches a single task from the database using its ID,
        eagerly loading the associated owner (User) relationship to avoid
        N+1 query problems.
        
        Args:
            db: Async database session for executing queries
            id: Unique identifier of the task to retrieve
        
        Returns:
            Optional[Task]: Task object with owner relationship loaded if found,
                           None if no task exists with the given ID
        
        Note:
            - Uses joinedload for eager loading of owner relationship
            - Returns None rather than raising exception if not found
            - Does not verify task ownership (suitable for OWNER role operations)
        """
        query = select(Task).options(joinedload(Task.owner)).where(Task.id == id)
        result = await db.scalars(query)
        return result.one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, obj_in: TaskCreate, owner_id: int
    ) -> Task:
        """
        Create a new task in the database and assign it to a specific owner.
        
        This method creates a task with the provided data, commits it to the
        database, and returns the fully initialized task object with all
        relationships loaded.
        
        Args:
            db: Async database session for executing queries
            obj_in: TaskCreate schema containing task data (title, description, status, due_date)
            owner_id: ID of the user who will own this task
        
        Returns:
            Task: Newly created task object with:
                - Auto-generated ID
                - All provided fields from obj_in
                - owner_id set to the specified user
                - Owner relationship eagerly loaded
                - Timestamps (created_at, updated_at) auto-populated
        
        Note:
            - Commits transaction immediately
            - Performs an additional query to eager load owner relationship
            - All fields from TaskCreate are included (exclude_unset=False)
        """
        task_data = obj_in.model_dump(exclude_unset=False)
        db_obj = Task(
            **task_data,
            owner_id=owner_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Load the owner relationship explicitly
        result = await db.scalars(
            select(Task)
            .options(joinedload(Task.owner))
            .where(Task.id == db_obj.id)
        )
        return result.one()

    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> List[Task]:
        """
        Retrieve all tasks in the system with pagination support.
        
        This method returns all tasks regardless of ownership, making it suitable
        for OWNER role operations that require system-wide task visibility.
        Each task is returned with its owner relationship eagerly loaded.
        
        Args:
            db: Async database session for executing queries
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of tasks to return (default: DEFAULT_PAGE_SIZE)
        
        Returns:
            List[Task]: List of task objects with owner relationships loaded.
                       Returns empty list if no tasks exist.
        
        Note:
            - No filtering by owner (returns all tasks)
            - Owner relationship is eagerly loaded via joinedload
            - Suitable for admin/owner dashboards
            - Use get_multi_by_owner for user-specific task lists
        """
        query = select(Task).options(joinedload(Task.owner)).offset(skip).limit(limit)
        result = await db.scalars(query)
        return list(result.all())

    @staticmethod
    async def get_multi_by_owner(
        db: AsyncSession, owner_id: int, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE
    ) -> List[Task]:
        """
        Retrieve all tasks owned by a specific user with pagination.
        
        This method filters tasks by owner_id, returning only tasks that belong
        to the specified user. Commonly used for MEMBER role to view their own
        tasks or for OWNER role to view a specific user's tasks.
        
        Args:
            db: Async database session for executing queries
            owner_id: ID of the user whose tasks should be retrieved
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of tasks to return (default: DEFAULT_PAGE_SIZE)
        
        Returns:
            List[Task]: List of tasks owned by the specified user.
                       Returns empty list if user has no tasks.
        
        Note:
            - Filters by owner_id (WHERE owner_id = ?)
            - Owner relationship is eagerly loaded
            - Does not verify if owner_id exists (returns empty list for invalid IDs)
            - Suitable for "My Tasks" views
        """
        query = select(Task).options(joinedload(Task.owner)).where(Task.owner_id == owner_id).offset(skip).limit(limit)
        result = await db.scalars(query)
        return list(result.all())

    @staticmethod
    async def get_by_id_and_owner(
        db: AsyncSession, id: int, owner_id: int
    ) -> Optional[Task]:
        """
        Retrieve a task by ID only if it belongs to the specified owner.
        
        This method performs a strict ownership check, ensuring the task exists
        AND is owned by the specified user. Returns None if either condition fails.
        
        Args:
            db: Async database session for executing queries
            id: Unique identifier of the task to retrieve
            owner_id: ID of the user who must own the task
        
        Returns:
            Optional[Task]: Task object with owner loaded if found and owned by user,
                           None if task doesn't exist or belongs to different user
        
        Note:
            - Performs both existence and ownership validation in single query
            - Cannot distinguish between "not found" and "not owned" (both return None)
            - Suitable for MEMBER role operations requiring ownership validation
            - Owner relationship is eagerly loaded
        """
        query = select(Task).options(joinedload(Task.owner)).where(Task.id == id, Task.owner_id == owner_id)
        result = await db.scalars(query)
        return result.one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession, db_obj: Task, obj_in: TaskUpdate
    ) -> Task:
        """
        Update a task with partial data from TaskUpdate schema.
        
        This method applies only the fields provided in obj_in (exclude_unset=True),
        leaving other fields unchanged. This enables partial updates where users
        can update individual fields without resending all data.
        
        Args:
            db: Async database session for executing queries
            db_obj: Existing task object to update (already fetched from database)
            obj_in: TaskUpdate schema with fields to update (only set fields are applied)
        
        Returns:
            Task: Updated task object with:
                - Modified fields from obj_in
                - Unchanged fields preserved
                - updated_at timestamp automatically refreshed
                - Owner relationship eagerly loaded
        
        Note:
            - Only fields present in obj_in are updated (exclude_unset=True)
            - Commits transaction immediately
            - Performs additional query to reload task with owner relationship
            - Does not validate task ownership (must be checked before calling)
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Load the owner relationship explicitly
        result = await db.scalars(
            select(Task)
            .options(joinedload(Task.owner))
            .where(Task.id == db_obj.id)
        )
        return result.one()

    @staticmethod
    async def delete(db: AsyncSession, db_obj: Task) -> None:
        """
        Permanently delete a task from the database.
        
        This method performs a hard delete, removing the task and all its
        associated data (comments, notifications) from the database.
        
        Args:
            db: Async database session for executing queries
            db_obj: Task object to delete (already fetched from database)
        
        Returns:
            None
        
        Note:
            - This is a hard delete (not soft delete)
            - Cascade delete will remove associated comments and notifications
            - Transaction is committed immediately
            - Does not validate ownership (must be checked before calling)
            - Cannot be undone after commit
        """
        await db.delete(db_obj)
        await db.commit()

    @staticmethod
    async def change_owner(db: AsyncSession, task: Task, new_owner_id: int) -> Task:
        """
        Transfer ownership of a task to a different user.
        
        This method updates the owner_id field of a task, effectively reassigning
        it to a new user. The new owner will gain full control over the task.
        
        Args:
            db: Async database session for executing queries
            task: Task object whose ownership will be changed
            new_owner_id: ID of the user who will become the new owner
        
        Returns:
            Task: Updated task object with:
                - owner_id changed to new_owner_id
                - Owner relationship refreshed with new owner data
                - updated_at timestamp automatically updated
        
        Note:
            - Does not validate if new_owner_id exists (must be checked before calling)
            - Does not notify old or new owner of the change
            - Commits transaction immediately
            - Refreshes owner relationship to load new owner data
            - Only OWNER role should be able to call this (enforced in service layer)
        """
        task.owner_id = new_owner_id
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # Load the owner relationship
        await db.refresh(task, ["owner"])
        
        return task