"""
Integration tests for comment endpoints.

This module contains comprehensive integration tests for the comment API endpoints.
Tests are organized by endpoint and follow the Arrange-Act-Assert (AAA) pattern.

Test Structure:
- TestGetTaskComments: Tests for GET /api/v1/tasks/{task_id}/comments
- TestCreateComment: Tests for POST /api/v1/tasks/{task_id}/comments
- TestUpdateComment: Tests for PUT /api/v1/tasks/comments/{comment_id}
- TestDeleteComment: Tests for DELETE /api/v1/tasks/comments/{comment_id}
- TestCommentIntegrationScenarios: Complex multi-step workflows

Each test class follows SOLID principles:
- Single Responsibility: Each test validates one specific behavior
- Open/Closed: Tests are designed to be extended without modification
- Interface Segregation: Tests use only the fixtures they need
- Dependency Inversion: Tests depend on fixtures (abstractions) not concrete implementations

Note: Authentication tests are already covered in other test files,
so we focus on comment-specific functionality and permission models.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from tests.factories import TaskFactory, CommentFactory, UserFactory


# ============================================================================
# GET /api/v1/tasks/{task_id}/comments - List Comments
# ============================================================================

class TestGetTaskComments:
    """
    Tests for the GET /api/v1/tasks/{task_id}/comments endpoint.
    
    This endpoint returns all comments for a specific task.
    Only the task owner or users with OWNER role can view comments.
    """
    
    async def test_get_task_comments_success_as_task_owner(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that task owner can view all comments on their task.
        
        Validates:
        - Status code is 200
        - Returns all comments for the task
        - Comments include author email
        - Comments are properly formatted
        """
        # Arrange: Create task and comments
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member,
            title="Task with comments"
        )
        
        comments = await CommentFactory.create_multiple_comments(
            db_session=db_session,
            task=task,
            author=test_user_member,
            count=3
        )
        
        # Act: Get task comments
        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify comment structure
        for comment_data in data:
            assert "id" in comment_data
            assert "content" in comment_data
            assert "task_id" in comment_data
            assert comment_data["task_id"] == task.id
            assert "author_id" in comment_data
            assert "author_email" in comment_data
            assert comment_data["author_email"] == test_user_member.email
            assert "created_at" in comment_data
    
    async def test_get_task_comments_success_as_owner_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that users with OWNER role can view any task's comments.
        
        Validates:
        - OWNER users can view comments on tasks they don't own
        - Status code is 200
        """
        # Arrange: Create task owned by member, with comments
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member,
            title="Member's task"
        )
        
        await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=test_user_member,
            content="Member's comment"
        )
        
        # Act: Owner tries to view comments
        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_owner
        )
        
        # Assert: Verify owner can see comments
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Member's comment"
    
    async def test_get_task_comments_forbidden_for_non_owner(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that non-owners cannot view comments on tasks they don't own.
        
        Validates:
        - Status code is 403 when trying to view another user's task comments
        - Members cannot access other members' task comments
        """
        # Arrange: Create task owned by another user
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="other@test.com"
        )
        
        other_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=other_user,
            title="Other user's task"
        )
        
        await CommentFactory.create_comment(
            db_session=db_session,
            task=other_task,
            author=other_user
        )
        
        # Act: Try to view comments as non-owner member
        response = await client.get(
            f"/api/v1/tasks/{other_task.id}/comments",
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_get_task_comments_not_found_for_invalid_task(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that requesting comments for non-existent task returns 404.
        
        Validates:
        - Status code is 404 for invalid task ID
        """
        # Act: Try to get comments for non-existent task
        response = await client.get(
            "/api/v1/tasks/99999/comments",
            headers=auth_headers_member
        )
        
        # Assert: Verify not found response
        assert response.status_code == 404
    
    async def test_get_task_comments_pagination(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test pagination parameters (skip and limit).
        
        Validates:
        - skip parameter works correctly
        - limit parameter works correctly
        """
        # Arrange: Create task with many comments
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        await CommentFactory.create_multiple_comments(
            db_session=db_session,
            task=task,
            author=test_user_member,
            count=10
        )
        
        # Act: Request with pagination
        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments?skip=2&limit=3",
            headers=auth_headers_member
        )
        
        # Assert: Verify pagination
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3  # Should respect limit
    
    async def test_get_task_comments_returns_empty_list_when_no_comments(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that requesting comments for task without comments returns empty list.
        
        Validates:
        - Status code is 200
        - Returns empty list for tasks without comments
        """
        # Arrange: Create task without comments
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        # Act: Get comments
        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        
        # Assert: Verify empty list
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_get_task_comments_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to get comments without authentication
        response = await client.get("/api/v1/tasks/1/comments")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# POST /api/v1/tasks/{task_id}/comments - Create Comment
# ============================================================================

class TestCreateComment:
    """
    Tests for the POST /api/v1/tasks/{task_id}/comments endpoint.
    
    This endpoint creates a new comment on a task.
    Only the task owner or users with OWNER role can comment.
    """
    
    async def test_create_comment_success_as_task_owner(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that task owner can create a comment on their task.
        
        Validates:
        - Status code is 201
        - Comment is created with correct data
        - Response includes author email
        """
        # Arrange: Create task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment_data = {
            "content": "This is a test comment"
        }
        
        # Act: Create comment
        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json=comment_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == comment_data["content"]
        assert data["task_id"] == task.id
        assert data["author_id"] == test_user_member.id
        assert data["author_email"] == test_user_member.email
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_comment_success_as_owner_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that users with OWNER role can comment on any task.
        
        Validates:
        - OWNER users can comment on tasks they don't own
        - Status code is 201
        """
        # Arrange: Create task owned by member
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment_data = {
            "content": "Owner's comment"
        }
        
        # Act: Owner creates comment
        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json=comment_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify owner can comment
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == comment_data["content"]
        assert data["author_id"] == test_user_owner.id
    
    async def test_create_comment_forbidden_for_non_owner(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that non-owners cannot comment on tasks they don't own.
        
        Validates:
        - Status code is 403 when trying to comment on another user's task
        """
        # Arrange: Create task owned by another user
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="other@test.com"
        )
        
        other_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=other_user
        )
        
        comment_data = {
            "content": "Unauthorized comment"
        }
        
        # Act: Try to create comment as non-owner
        response = await client.post(
            f"/api/v1/tasks/{other_task.id}/comments",
            json=comment_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_create_comment_not_found_for_invalid_task(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that creating comment on non-existent task returns 404.
        
        Validates:
        - Status code is 404 for invalid task ID
        """
        # Arrange: Prepare comment data
        comment_data = {
            "content": "Comment on non-existent task"
        }
        
        # Act: Try to create comment on non-existent task
        response = await client.post(
            "/api/v1/tasks/99999/comments",
            json=comment_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify not found response
        assert response.status_code == 404
    
    async def test_create_comment_validates_required_fields(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that content field is required.
        
        Validates:
        - Status code is 422 when content is missing
        """
        # Arrange: Create task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        # Act: Try to create comment without content
        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={},
            headers=auth_headers_member
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422
    
    async def test_create_comment_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Arrange: Prepare comment data
        comment_data = {
            "content": "Test comment"
        }
        
        # Act: Try to create comment without authentication
        response = await client.post(
            "/api/v1/tasks/1/comments",
            json=comment_data
        )
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# PUT /api/v1/tasks/comments/{comment_id} - Update Comment
# ============================================================================

class TestUpdateComment:
    """
    Tests for the PUT /api/v1/tasks/comments/{comment_id} endpoint.
    
    This endpoint updates an existing comment.
    Only the comment author can update their comment.
    """
    
    async def test_update_comment_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that comment author can update their comment.
        
        Validates:
        - Status code is 200
        - Comment content is updated
        - updated_at field is set
        """
        # Arrange: Create task and comment
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment = await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=test_user_member,
            content="Original content"
        )
        
        update_data = {
            "content": "Updated content"
        }
        
        # Act: Update comment
        response = await client.put(
            f"/api/v1/tasks/comments/{comment.id}",
            json=update_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == comment.id
        assert data["content"] == "Updated content"
        assert data["updated_at"] is not None
    
    async def test_update_comment_forbidden_for_non_author(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that non-authors cannot update comments.
        
        Validates:
        - Status code is 403 when trying to update another user's comment
        - Even task owner cannot update comments they didn't author
        """
        # Arrange: Create another user who will be the comment author
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="author@test.com"
        )
        
        # Create task owned by test_user_member
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        # Create comment by other_user
        comment = await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=other_user,
            content="Other user's comment"
        )
        
        update_data = {
            "content": "Trying to update someone else's comment"
        }
        
        # Act: Try to update comment as non-author
        response = await client.put(
            f"/api/v1/tasks/comments/{comment.id}",
            json=update_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_update_comment_not_found(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that updating non-existent comment returns 404.
        
        Validates:
        - Status code is 404 for invalid comment ID
        """
        # Arrange: Prepare update data
        update_data = {
            "content": "Updated content"
        }
        
        # Act: Try to update non-existent comment
        response = await client.put(
            "/api/v1/tasks/comments/99999",
            json=update_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify not found response
        assert response.status_code == 404
    
    async def test_update_comment_validates_required_fields(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that content field is required for updates.
        
        Validates:
        - Status code is 422 when content is missing
        """
        # Arrange: Create task and comment
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment = await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=test_user_member
        )
        
        # Act: Try to update without content
        response = await client.put(
            f"/api/v1/tasks/comments/{comment.id}",
            json={},
            headers=auth_headers_member
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422
    
    async def test_update_comment_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Arrange: Prepare update data
        update_data = {
            "content": "Updated content"
        }
        
        # Act: Try to update without authentication
        response = await client.put(
            "/api/v1/tasks/comments/1",
            json=update_data
        )
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# DELETE /api/v1/tasks/comments/{comment_id} - Delete Comment
# ============================================================================

class TestDeleteComment:
    """
    Tests for the DELETE /api/v1/tasks/comments/{comment_id} endpoint.
    
    This endpoint deletes a comment.
    Only the comment author or users with OWNER role can delete comments.
    """
    
    async def test_delete_comment_success_as_author(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that comment author can delete their comment.
        
        Validates:
        - Status code is 204
        - Comment is deleted from database
        """
        # Arrange: Create task and comment
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment = await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=test_user_member
        )
        
        comment_id = comment.id
        
        # Act: Delete comment
        response = await client.delete(
            f"/api/v1/tasks/comments/{comment_id}",
            headers=auth_headers_member
        )
        
        # Assert: Verify deletion
        assert response.status_code == 204
        
        # Verify comment is gone
        get_response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        comments = get_response.json()
        assert not any(c["id"] == comment_id for c in comments)
    
    async def test_delete_comment_success_as_owner_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that users with OWNER role can delete any comment.
        
        Validates:
        - OWNER users can delete comments they didn't author
        - Status code is 204
        """
        # Arrange: Create task and comment by member
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment = await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=test_user_member
        )
        
        # Act: Owner deletes member's comment
        response = await client.delete(
            f"/api/v1/tasks/comments/{comment.id}",
            headers=auth_headers_owner
        )
        
        # Assert: Verify owner can delete
        assert response.status_code == 204
    
    async def test_delete_comment_forbidden_for_non_author_non_owner(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that non-authors without OWNER role cannot delete comments.
        
        Validates:
        - Status code is 403 when trying to delete another user's comment
        """
        # Arrange: Create another user who will be the comment author
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="author@test.com"
        )
        
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment = await CommentFactory.create_comment(
            db_session=db_session,
            task=task,
            author=other_user
        )
        
        # Act: Try to delete comment as non-author
        response = await client.delete(
            f"/api/v1/tasks/comments/{comment.id}",
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_delete_comment_not_found(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that deleting non-existent comment returns 404.
        
        Validates:
        - Status code is 404 for invalid comment ID
        """
        # Act: Try to delete non-existent comment
        response = await client.delete(
            "/api/v1/tasks/comments/99999",
            headers=auth_headers_member
        )
        
        # Assert: Verify not found response
        assert response.status_code == 404
    
    async def test_delete_comment_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to delete without authentication
        response = await client.delete("/api/v1/tasks/comments/1")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# Integration Scenarios
# ============================================================================

class TestCommentIntegrationScenarios:
    """
    Tests for complex scenarios involving multiple operations.
    
    These tests validate the interaction between different endpoints
    and ensure data consistency across operations.
    """
    
    async def test_comment_lifecycle_complete_flow(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test complete comment workflow: create → read → update → delete.
        
        Validates:
        - Comment can be created
        - Comment appears in list
        - Comment can be updated
        - Comment can be deleted
        - Comment is gone after deletion
        """
        # Arrange: Create task
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member,
            title="Task for comment lifecycle"
        )
        
        # Act 1: Create comment
        create_response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Initial comment"},
            headers=auth_headers_member
        )
        assert create_response.status_code == 201
        comment = create_response.json()
        comment_id = comment["id"]
        
        # Act 2: Verify comment appears in list
        list_response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        assert list_response.status_code == 200
        comments = list_response.json()
        assert len(comments) == 1
        assert comments[0]["content"] == "Initial comment"
        
        # Act 3: Update comment
        update_response = await client.put(
            f"/api/v1/tasks/comments/{comment_id}",
            json={"content": "Updated comment"},
            headers=auth_headers_member
        )
        assert update_response.status_code == 200
        assert update_response.json()["content"] == "Updated comment"
        
        # Act 4: Verify update in list
        list_response2 = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        comments2 = list_response2.json()
        assert comments2[0]["content"] == "Updated comment"
        
        # Act 5: Delete comment
        delete_response = await client.delete(
            f"/api/v1/tasks/comments/{comment_id}",
            headers=auth_headers_member
        )
        assert delete_response.status_code == 204
        
        # Act 6: Verify comment is gone
        list_response3 = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        assert len(list_response3.json()) == 0
    
    async def test_multiple_users_commenting_on_task(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        test_user_owner: User,
        auth_headers_member: dict,
        auth_headers_owner: dict
    ):
        """
        Test that task owner and OWNER role users can both comment.
        
        Validates:
        - Task owner can create comments
        - OWNER users can create comments on any task
        - All comments are visible to task owner
        - Author emails are correctly included
        """
        # Arrange: Create task owned by member
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        # Act 1: Member comments on their task
        member_response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Member's comment"},
            headers=auth_headers_member
        )
        assert member_response.status_code == 201
        
        # Act 2: Owner comments on member's task
        owner_response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Owner's comment"},
            headers=auth_headers_owner
        )
        assert owner_response.status_code == 201
        
        # Act 3: Get all comments
        list_response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        
        # Assert: Verify both comments exist with correct authors
        assert list_response.status_code == 200
        comments = list_response.json()
        assert len(comments) == 2
        
        member_comment = next(c for c in comments if c["author_email"] == test_user_member.email)
        owner_comment = next(c for c in comments if c["author_email"] == test_user_owner.email)
        
        assert member_comment["content"] == "Member's comment"
        assert owner_comment["content"] == "Owner's comment"
    
    async def test_owner_can_moderate_comments(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        test_user_owner: User,
        auth_headers_member: dict,
        auth_headers_owner: dict
    ):
        """
        Test that OWNER role users can delete any comment (moderation).
        
        Validates:
        - OWNER users can delete comments from any user
        - Moderation capability for content management
        """
        # Arrange: Create task and comment by member
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        comment_response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Member's comment to be deleted"},
            headers=auth_headers_member
        )
        comment_id = comment_response.json()["id"]
        
        # Act: Owner deletes member's comment
        delete_response = await client.delete(
            f"/api/v1/tasks/comments/{comment_id}",
            headers=auth_headers_owner
        )
        
        # Assert: Verify successful deletion
        assert delete_response.status_code == 204
        
        # Verify comment is gone
        list_response = await client.get(
            f"/api/v1/tasks/{task.id}/comments",
            headers=auth_headers_member
        )
        assert len(list_response.json()) == 0
    
    async def test_comment_isolation_between_tasks(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that comments are properly isolated to their tasks.
        
        Validates:
        - Comments on one task don't appear on another
        - Each task has its own comment thread
        """
        # Arrange: Create two tasks
        task1 = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member,
            title="Task 1"
        )
        
        task2 = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member,
            title="Task 2"
        )
        
        # Act: Create comments on each task
        await client.post(
            f"/api/v1/tasks/{task1.id}/comments",
            json={"content": "Comment on task 1"},
            headers=auth_headers_member
        )
        
        await client.post(
            f"/api/v1/tasks/{task2.id}/comments",
            json={"content": "Comment on task 2"},
            headers=auth_headers_member
        )
        
        # Assert: Verify comments are isolated
        task1_comments = await client.get(
            f"/api/v1/tasks/{task1.id}/comments",
            headers=auth_headers_member
        )
        task1_data = task1_comments.json()
        assert len(task1_data) == 1
        assert task1_data[0]["content"] == "Comment on task 1"
        
        task2_comments = await client.get(
            f"/api/v1/tasks/{task2.id}/comments",
            headers=auth_headers_member
        )
        task2_data = task2_comments.json()
        assert len(task2_data) == 1
        assert task2_data[0]["content"] == "Comment on task 2"
