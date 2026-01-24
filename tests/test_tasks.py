"""
Integration tests for Task endpoints.

This module contains comprehensive integration tests for all task-related
API endpoints. Tests use a real PostgreSQL test database to ensure
end-to-end functionality.

Test Organization:
- Tests are grouped by HTTP method and functionality
- Each test follows AAA pattern: Arrange, Act, Assert
- Tests are independent and can run in any order
- Test names clearly describe the scenario being tested

Following SOLID principles:
- Single Responsibility: Each test focuses on one scenario
- Dependency Inversion: Tests depend on abstractions (fixtures)
- Interface Segregation: Tests use only the fixtures they need
"""
import pytest
from httpx import AsyncClient
from src.models.user import User
from src.models.task import TaskStatus
from tests.factories import TaskFactory, TestDataBuilder


# ============================================================================
# GET /api/v1/tasks - List Tasks
# ============================================================================

class TestListTasks:
    """Test suite for listing tasks endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_tasks_returns_user_tasks(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict,
        db_session
    ):
        """
        Test that listing tasks returns only the authenticated user's tasks.
        
        Verifies:
        - Authenticated user can retrieve their tasks
        - Only tasks belonging to the user are returned
        - Response structure is correct
        """
        # Arrange: Create tasks for the authenticated user
        tasks = await TaskFactory.create_multiple_tasks(
            db_session=db_session,
            owner=test_user_owner,
            count=3
        )
        
        # Act: Request the user's tasks
        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify all tasks belong to the authenticated user
        for task_data in data:
            assert task_data["owner_id"] == test_user_owner.id
            assert "id" in task_data
            assert "title" in task_data
            assert "status" in task_data
    
    @pytest.mark.asyncio
    async def test_list_tasks_empty_for_new_user(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that a new user with no tasks receives an empty list.
        
        Verifies:
        - Empty list is returned for users without tasks
        - No errors occur when user has no tasks
        """
        # Act: Request tasks for user with no tasks
        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_member
        )
        
        # Assert: Verify empty list
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_list_tasks_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that listing tasks requires authentication.
        
        Verifies:
        - Unauthenticated requests are rejected
        - Appropriate error code is returned
        """
        # Act: Request without authentication headers
        response = await client.get("/api/v1/tasks")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_tasks_does_not_show_other_users_tasks(
        self,
        client: AsyncClient,
        test_user_owner: User,
        test_user_member: User,
        auth_headers_member: dict,
        db_session
    ):
        """
        Test that users cannot see other users' tasks.
        
        Verifies:
        - Task isolation between users
        - Privacy and security of task data
        """
        # Arrange: Create tasks for owner user
        await TaskFactory.create_multiple_tasks(
            db_session=db_session,
            owner=test_user_owner,
            count=3
        )
        
        # Act: Request as member user
        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_member
        )
        
        # Assert: Member sees no tasks
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


# ============================================================================
# POST /api/v1/tasks - Create Task
# ============================================================================

class TestCreateTask:
    """Test suite for creating tasks endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test successful task creation with valid data.
        
        Verifies:
        - Task is created with provided data
        - Response includes all expected fields
        - Task is associated with the authenticated user
        """
        # Arrange: Prepare task data
        task_data = {
            "title": "New Test Task",
            "description": "This is a test task description",
            "status": "todo"
        }
        
        # Act: Create task
        response = await client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify creation
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["owner_id"] == test_user_owner.id
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_task_with_due_date(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test creating a task with a due date.
        
        Verifies:
        - Due date is correctly stored
        - Due date is returned in response
        """
        # Arrange: Task data with due date
        task_data = {
            "title": "Task with deadline",
            "description": "This task has a due date",
            "status": "todo",
            "due_date": "2026-12-31T23:59:59Z"
        }
        
        # Act: Create task
        response = await client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify due date
        assert response.status_code == 201
        data = response.json()
        assert "due_date" in data
        assert data["due_date"] is not None
    
    @pytest.mark.asyncio
    async def test_create_task_minimal_data(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test creating a task with only required fields.
        
        Verifies:
        - Optional fields can be omitted
        - Default values are applied correctly
        """
        # Arrange: Minimal task data (only title is required)
        task_data = {
            "title": "Minimal Task"
        }
        
        # Act: Create task
        response = await client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify creation with defaults
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["status"] == "todo"  # Default status
        assert data["description"] is None  # Optional field
    
    @pytest.mark.asyncio
    async def test_create_task_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that creating a task requires authentication.
        
        Verifies:
        - Unauthenticated requests are rejected
        - No task is created without auth
        """
        # Arrange: Task data
        task_data = {"title": "Unauthorized Task"}
        
        # Act: Attempt to create without auth
        response = await client.post(
            "/api/v1/tasks",
            json=task_data
        )
        
        # Assert: Verify rejection
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_task_validates_required_fields(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test that task creation validates required fields.
        
        Verifies:
        - Missing required fields cause validation error
        - Appropriate error message is returned
        """
        # Arrange: Empty data (missing required title)
        task_data = {}
        
        # Act: Attempt to create
        response = await client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_create_task_validates_status_enum(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test that invalid status values are rejected.
        
        Verifies:
        - Status field is validated against allowed values
        - Invalid values cause validation error
        """
        # Arrange: Task with invalid status
        task_data = {
            "title": "Task with invalid status",
            "status": "invalid_status"
        }
        
        # Act: Attempt to create
        response = await client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422


# ============================================================================
# GET /api/v1/tasks/{id} - Get Task by ID
# ============================================================================

class TestGetTask:
    """Test suite for retrieving a single task endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_task_success(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict,
        db_session
    ):
        """
        Test successfully retrieving a task by ID.
        
        Verifies:
        - Task owner can retrieve their task
        - All task details are returned
        """
        # Arrange: Create a task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner,
            title="Specific Task"
        )
        
        # Act: Retrieve the task
        response = await client.get(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "Specific Task"
        assert data["owner_id"] == test_user_owner.id
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test retrieving a non-existent task.
        
        Verifies:
        - 404 error is returned for non-existent task
        - Appropriate error message
        """
        # Act: Request non-existent task
        response = await client.get(
            "/api/v1/tasks/99999",
            headers=auth_headers_owner
        )
        
        # Assert: Verify not found
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_task_forbidden_for_other_user(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_member: dict,
        db_session
    ):
        """
        Test that users cannot access other users' tasks.
        
        Verifies:
        - Task privacy is enforced
        - 403 or 404 error is returned
        """
        # Arrange: Create task for owner
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner
        )
        
        # Act: Try to access as member
        response = await client.get(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_member
        )
        
        # Assert: Verify access denied
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_get_task_requires_authentication(
        self,
        client: AsyncClient,
        test_user_owner: User,
        db_session
    ):
        """
        Test that retrieving a task requires authentication.
        
        Verifies:
        - Unauthenticated requests are rejected
        """
        # Arrange: Create a task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner
        )
        
        # Act: Request without auth
        response = await client.get(f"/api/v1/tasks/{task.id}")
        
        # Assert: Verify rejection
        assert response.status_code == 401


# ============================================================================
# PUT /api/v1/tasks/{id} - Update Task
# ============================================================================

class TestUpdateTask:
    """Test suite for updating tasks endpoint."""
    
    @pytest.mark.asyncio
    async def test_update_task_success(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict,
        db_session
    ):
        """
        Test successfully updating a task.
        
        Verifies:
        - Task owner can update their task
        - Updated fields are reflected in response
        - Unchanged fields remain the same
        """
        # Arrange: Create a task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner,
            title="Original Title",
            status=TaskStatus.TODO
        )
        
        # Prepare update data
        update_data = {
            "title": "Updated Title",
            "status": "in_progress"
        }
        
        # Act: Update the task
        response = await client.put(
            f"/api/v1/tasks/{task.id}",
            json=update_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify update
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
        assert data["id"] == task.id
    
    @pytest.mark.asyncio
    async def test_update_task_partial_update(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict,
        db_session
    ):
        """
        Test partial update of a task (only some fields).
        
        Verifies:
        - Only provided fields are updated
        - Other fields remain unchanged
        """
        # Arrange: Create a task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner,
            title="Original Title",
            description="Original Description",
            status=TaskStatus.TODO
        )
        
        # Update only status
        update_data = {"status": "done"}
        
        # Act: Update
        response = await client.put(
            f"/api/v1/tasks/{task.id}",
            json=update_data,
            headers=auth_headers_owner
        )
        
        # Assert: Status updated, other fields unchanged
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"
        assert data["title"] == "Original Title"
        assert data["description"] == "Original Description"
    
    @pytest.mark.asyncio
    async def test_update_task_forbidden_for_other_user(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_member: dict,
        db_session
    ):
        """
        Test that users cannot update other users' tasks.
        
        Verifies:
        - Update permission is enforced
        - 403 or 404 error is returned
        """
        # Arrange: Create task for owner
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner
        )
        
        # Act: Try to update as member
        response = await client.put(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Hacked Title"},
            headers=auth_headers_member
        )
        
        # Assert: Verify access denied
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test updating a non-existent task.
        
        Verifies:
        - 404 error is returned
        """
        # Act: Update non-existent task
        response = await client.put(
            "/api/v1/tasks/99999",
            json={"title": "New Title"},
            headers=auth_headers_owner
        )
        
        # Assert: Verify not found
        assert response.status_code == 404


# ============================================================================
# DELETE /api/v1/tasks/{id} - Delete Task
# ============================================================================

class TestDeleteTask:
    """Test suite for deleting tasks endpoint."""
    
    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict,
        db_session
    ):
        """
        Test successfully deleting a task.
        
        Verifies:
        - Task owner can delete their task
        - Task is actually removed from database
        - Subsequent requests return 404
        """
        # Arrange: Create a task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner
        )
        task_id = task.id
        
        # Act: Delete the task
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers_owner
        )
        
        # Assert: Verify deletion
        assert response.status_code == 204
        
        # Verify task no longer exists
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers_owner
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_forbidden_for_other_user(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_member: dict,
        db_session
    ):
        """
        Test that users cannot delete other users' tasks.
        
        Verifies:
        - Delete permission is enforced
        - Task remains in database
        """
        # Arrange: Create task for owner
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner
        )
        
        # Act: Try to delete as member
        response = await client.delete(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_member
        )
        
        # Assert: Verify access denied
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test deleting a non-existent task.
        
        Verifies:
        - 404 error is returned
        """
        # Act: Delete non-existent task
        response = await client.delete(
            "/api/v1/tasks/99999",
            headers=auth_headers_owner
        )
        
        # Assert: Verify not found
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_cascades_to_comments(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict,
        db_session
    ):
        """
        Test that deleting a task also deletes associated comments.
        
        Verifies:
        - Cascade deletion works correctly
        - Related data is cleaned up
        """
        # Arrange: Create task with comments
        from tests.factories import CommentFactory
        
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner
        )
        
        await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=test_user_owner
        )
        
        # Act: Delete the task
        response = await client.delete(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_owner
        )
        
        # Assert: Task and comments deleted
        assert response.status_code == 204
        
        # Verify comments endpoint returns 404
        comments_response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_owner
        )
        assert comments_response.status_code == 404


# ============================================================================
# Complex Scenarios
# ============================================================================

class TestComplexTaskScenarios:
    """Test suite for complex multi-step task scenarios."""
    
    @pytest.mark.asyncio
    async def test_task_lifecycle_complete_flow(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test complete task lifecycle: create -> update -> complete -> delete.
        
        Verifies:
        - Full workflow operates correctly
        - State transitions are valid
        """
        # Step 1: Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Lifecycle Test Task", "status": "todo"},
            headers=auth_headers_owner
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Step 2: Start working on it
        update_response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers_owner
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "in_progress"
        
        # Step 3: Complete it
        complete_response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"status": "done"},
            headers=auth_headers_owner
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "done"
        
        # Step 4: Delete it
        delete_response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers_owner
        )
        assert delete_response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_multiple_users_isolated_tasks(
        self,
        client: AsyncClient,
        test_user_owner: User,
        test_user_member: User,
        auth_headers_owner: dict,
        auth_headers_member: dict,
        db_session
    ):
        """
        Test that multiple users have completely isolated task lists.
        
        Verifies:
        - Task isolation between users
        - Each user sees only their own tasks
        """
        # Arrange: Create tasks for both users
        await TaskFactory.create_multiple_tasks(
            db_session=db_session,
            owner=test_user_owner,
            count=3
        )
        
        await TaskFactory.create_multiple_tasks(
            db_session=db_session,
            owner=test_user_member,
            count=2
        )
        
        # Act & Assert: Owner sees ALL 5 tasks (owner role sees all tasks by default)
        owner_response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_owner
        )
        assert owner_response.status_code == 200
        assert len(owner_response.json()) == 5  # Owner sees all tasks
        
        # Act & Assert: Member sees only their 2 tasks
        member_response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_member
        )
        assert member_response.status_code == 200
        assert len(member_response.json()) == 2  # Member sees only their tasks
        assert member_response.status_code == 200
        assert len(member_response.json()) == 2
