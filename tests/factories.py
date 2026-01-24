"""
Test data factories.

This module provides factory functions for creating test data.
Follows the Factory Pattern to encapsulate object creation logic
and the Builder Pattern for flexible object construction.

These factories make tests more readable and maintainable by:
1. Centralizing test data creation
2. Providing sensible defaults
3. Allowing customization when needed
4. Reducing code duplication across tests
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task, TaskStatus
from src.models.user import User
from src.models.comment import Comment


class TaskFactory:
    """
    Factory for creating Task instances in tests.
    
    Provides a clean interface for creating tasks with sensible defaults
    while allowing customization. Follows the Single Responsibility
    Principle - only responsible for task creation.
    """
    
    @staticmethod
    async def create_task(
        db_session: AsyncSession,
        owner: User,
        title: str = "Test Task",
        description: Optional[str] = "Test task description",
        status: TaskStatus = TaskStatus.TODO,
        due_date: Optional[datetime] = None,
        **kwargs
    ) -> Task:
        """
        Create a task with the given parameters.
        
        This factory method provides a flexible way to create tasks
        for testing. All parameters have defaults but can be overridden.
        
        Args:
            db_session: Database session to use
            owner: User who owns the task
            title: Task title (default: "Test Task")
            description: Task description (default: "Test task description")
            status: Task status (default: TaskStatus.TODO)
            due_date: Optional due date for the task
            **kwargs: Additional fields to set on the task
            
        Returns:
            Task: The created task instance
            
        Example:
            task = await TaskFactory.create_task(
                db_session=db,
                owner=user,
                title="My custom task",
                status=TaskStatus.IN_PROGRESS
            )
        """
        task = Task(
            title=title,
            description=description,
            status=status,
            owner_id=owner.id,
            due_date=due_date,
            **kwargs
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)
        return task
    
    @staticmethod
    async def create_task_with_due_date(
        db_session: AsyncSession,
        owner: User,
        days_from_now: int = 1,
        **kwargs
    ) -> Task:
        """
        Create a task with a due date set to a specific number of days from now.
        
        Convenience method for creating tasks with due dates,
        useful for testing notification features.
        
        Args:
            db_session: Database session to use
            owner: User who owns the task
            days_from_now: Number of days from now for the due date
            **kwargs: Additional fields to pass to create_task
            
        Returns:
            Task: The created task with a due date
            
        Example:
            # Create a task due tomorrow
            task = await TaskFactory.create_task_with_due_date(
                db_session=db,
                owner=user,
                days_from_now=1
            )
        """
        due_date = datetime.now(timezone.utc) + timedelta(days=days_from_now)
        return await TaskFactory.create_task(
            db_session=db_session,
            owner=owner,
            due_date=due_date,
            **kwargs
        )
    
    @staticmethod
    async def create_overdue_task(
        db_session: AsyncSession,
        owner: User,
        **kwargs
    ) -> Task:
        """
        Create a task that is already overdue.
        
        Convenience method for testing overdue task scenarios.
        
        Args:
            db_session: Database session to use
            owner: User who owns the task
            **kwargs: Additional fields to pass to create_task
            
        Returns:
            Task: The created overdue task
        """
        due_date = datetime.now(timezone.utc) - timedelta(days=1)
        return await TaskFactory.create_task(
            db_session=db_session,
            owner=owner,
            due_date=due_date,
            status=TaskStatus.TODO,  # Not done but overdue
            **kwargs
        )
    
    @staticmethod
    async def create_multiple_tasks(
        db_session: AsyncSession,
        owner: User,
        count: int = 3,
        **kwargs
    ) -> list[Task]:
        """
        Create multiple tasks at once.
        
        Useful for testing pagination, filtering, and bulk operations.
        
        Args:
            db_session: Database session to use
            owner: User who owns the tasks
            count: Number of tasks to create
            **kwargs: Additional fields to pass to each task
            
        Returns:
            list[Task]: List of created tasks
            
        Example:
            tasks = await TaskFactory.create_multiple_tasks(
                db_session=db,
                owner=user,
                count=5,
                status=TaskStatus.TODO
            )
        """
        tasks = []
        for i in range(count):
            task = await TaskFactory.create_task(
                db_session=db_session,
                owner=owner,
                title=f"Test Task {i+1}",
                description=f"Description for task {i+1}",
                **kwargs
            )
            tasks.append(task)
        return tasks


class CommentFactory:
    """
    Factory for creating Comment instances in tests.
    
    Provides methods for creating comments on tasks with sensible defaults.
    """
    
    @staticmethod
    async def create_comment(
        db_session: AsyncSession,
        task: Task,
        author: User,
        content: str = "Test comment",
        **kwargs
    ) -> Comment:
        """
        Create a comment on a task.
        
        Args:
            db_session: Database session to use
            task: Task to comment on
            author: User who wrote the comment
            content: Comment content
            **kwargs: Additional fields to set on the comment
            
        Returns:
            Comment: The created comment instance
        """
        comment = Comment(
            content=content,
            task_id=task.id,
            author_id=author.id,
            **kwargs
        )
        db_session.add(comment)
        await db_session.commit()
        await db_session.refresh(comment)
        return comment
    
    @staticmethod
    async def create_multiple_comments(
        db_session: AsyncSession,
        task: Task,
        author: User,
        count: int = 3
    ) -> list[Comment]:
        """
        Create multiple comments on a task.
        
        Args:
            db_session: Database session to use
            task: Task to comment on
            author: User who wrote the comments
            count: Number of comments to create
            
        Returns:
            list[Comment]: List of created comments
        """
        comments = []
        for i in range(count):
            comment = await CommentFactory.create_comment(
                db_session=db_session,
                task=task,
                author=author,
                content=f"Test comment {i+1}"
            )
            comments.append(comment)
        return comments


class TestDataBuilder:
    """
    Builder class for creating complex test scenarios.
    
    Uses the Builder Pattern to construct test data setups that
    involve multiple related entities. This makes tests more
    expressive and easier to maintain.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the builder with a database session.
        
        Args:
            db_session: Database session to use for creating data
        """
        self.db_session = db_session
        self.tasks: list[Task] = []
        self.comments: list[Comment] = []
    
    async def with_tasks_for_user(
        self,
        owner: User,
        count: int = 3,
        **kwargs
    ) -> "TestDataBuilder":
        """
        Add tasks for a specific user to the test data.
        
        Args:
            owner: User who owns the tasks
            count: Number of tasks to create
            **kwargs: Additional fields for the tasks
            
        Returns:
            TestDataBuilder: Self for method chaining
        """
        tasks = await TaskFactory.create_multiple_tasks(
            db_session=self.db_session,
            owner=owner,
            count=count,
            **kwargs
        )
        self.tasks.extend(tasks)
        return self
    
    async def with_comments_on_task(
        self,
        task: Task,
        author: User,
        count: int = 2
    ) -> "TestDataBuilder":
        """
        Add comments to a specific task.
        
        Args:
            task: Task to add comments to
            author: Author of the comments
            count: Number of comments to create
            
        Returns:
            TestDataBuilder: Self for method chaining
        """
        comments = await CommentFactory.create_multiple_comments(
            db_session=self.db_session,
            task=task,
            author=author,
            count=count
        )
        self.comments.extend(comments)
        return self
    
    def build(self) -> dict:
        """
        Build and return the test data.
        
        Returns:
            dict: Dictionary containing all created test data
        """
        return {
            "tasks": self.tasks,
            "comments": self.comments
        }
