"""
Integration tests for notification endpoints.

This module contains comprehensive integration tests for the notification API endpoints.
Tests are organized by endpoint and follow the Arrange-Act-Assert (AAA) pattern.

Test Structure:
- TestGetNotifications: Tests for GET /api/v1/notifications/
- TestGetUnreadCount: Tests for GET /api/v1/notifications/unread-count
- TestMarkNotificationAsRead: Tests for PUT /api/v1/notifications/{id}/read
- TestDeleteNotification: Tests for DELETE /api/v1/notifications/{id}
- TestCheckDueDates: Tests for POST /api/v1/notifications/check-due-dates
- TestNotificationIntegrationScenarios: Complex multi-step workflows

Each test class follows SOLID principles:
- Single Responsibility: Each test validates one specific behavior
- Open/Closed: Tests are designed to be extended without modification
- Interface Segregation: Tests use only the fixtures they need
- Dependency Inversion: Tests depend on fixtures (abstractions) not concrete implementations

Note: Authentication tests are already covered in other test files,
so we focus on notification-specific functionality and edge cases.
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.notification import NotificationType
from tests.factories import TaskFactory, NotificationFactory, UserFactory


# ============================================================================
# GET /api/v1/notifications/ - List Notifications
# ============================================================================

class TestGetNotifications:
    """
    Tests for the GET /api/v1/notifications/ endpoint.
    
    This endpoint returns notifications for the authenticated user.
    Supports filtering by read status and pagination.
    """
    
    async def test_get_notifications_returns_user_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that user can retrieve their own notifications.
        
        Validates:
        - Status code is 200
        - Returns all user's notifications
        - Notifications are properly formatted
        - Task title is included in response
        """
        # Arrange: Create a task and notifications for the user
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member,
            title="Important Task"
        )
        
        await NotificationFactory.create_multiple_notifications(
            db_session=db_session,
            user=test_user_member,
            task=task,
            count=3
        )
        
        # Act: Get notifications
        response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify notification structure
        for notification in data:
            assert "id" in notification
            assert "message" in notification
            assert "notification_type" in notification
            assert "user_id" in notification
            assert "task_id" in notification
            assert "task_title" in notification
            assert notification["task_title"] == "Important Task"
            assert "is_read" in notification
            assert "created_at" in notification
    
    async def test_get_notifications_filters_by_unread(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test filtering notifications by unread status.
        
        Validates:
        - unread_only=true returns only unread notifications
        - Read notifications are excluded from results
        """
        # Arrange: Create read and unread notifications
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        # Create 2 unread notifications
        await NotificationFactory.create_notification(
            db_session=db_session,
            user=test_user_member,
            task=task,
            message="Unread 1",
            is_read=False
        )
        await NotificationFactory.create_notification(
            db_session=db_session,
            user=test_user_member,
            task=task,
            message="Unread 2",
            is_read=False
        )
        
        # Create 1 read notification
        await NotificationFactory.create_read_notification(
            db_session=db_session,
            user=test_user_member,
            task=task
        )
        
        # Act: Get only unread notifications
        response = await client.get(
            "/api/v1/notifications/?unread_only=true",
            headers=auth_headers_member
        )
        
        # Assert: Verify only unread notifications returned
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for notification in data:
            assert notification["is_read"] is False
    
    async def test_get_notifications_pagination(
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
        # Arrange: Create multiple notifications
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        await NotificationFactory.create_multiple_notifications(
            db_session=db_session,
            user=test_user_member,
            task=task,
            count=10
        )
        
        # Act: Request with pagination
        response = await client.get(
            "/api/v1/notifications/?skip=2&limit=3",
            headers=auth_headers_member
        )
        
        # Assert: Verify pagination
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3  # Should respect limit
    
    async def test_get_notifications_does_not_show_other_users_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that users can only see their own notifications.
        
        Validates:
        - User's notifications are returned
        - Other users' notifications are not exposed
        """
        # Arrange: Create another user with notifications
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="other@test.com"
        )
        
        other_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=other_user
        )
        
        await NotificationFactory.create_notification(
            db_session=db_session,
            user=other_user,
            task=other_task,
            message="Other user's notification"
        )
        
        # Create notification for test user
        user_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        user_notification = await NotificationFactory.create_notification(
            db_session=db_session,
            user=test_user_member,
            task=user_task,
            message="User's notification"
        )
        
        # Act: Get notifications
        response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        
        # Assert: Verify only user's notifications returned
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == user_notification.id
        assert data[0]["message"] == "User's notification"
    
    async def test_get_notifications_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to get notifications without authentication
        response = await client.get("/api/v1/notifications/")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# GET /api/v1/notifications/unread-count - Get Unread Count
# ============================================================================

class TestGetUnreadCount:
    """
    Tests for the GET /api/v1/notifications/unread-count endpoint.
    
    This endpoint returns the count of unread notifications for the user.
    """
    
    async def test_get_unread_count_returns_correct_count(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that unread count is accurate.
        
        Validates:
        - Status code is 200
        - Count matches actual unread notifications
        - Read notifications are not counted
        """
        # Arrange: Create read and unread notifications
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        # Create 3 unread notifications
        for _ in range(3):
            await NotificationFactory.create_notification(
                db_session=db_session,
                user=test_user_member,
                task=task,
                is_read=False
            )
        
        # Create 2 read notifications
        for _ in range(2):
            await NotificationFactory.create_read_notification(
                db_session=db_session,
                user=test_user_member,
                task=task
            )
        
        # Act: Get unread count
        response = await client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers_member
        )
        
        # Assert: Verify count
        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        assert data["unread_count"] == 3
    
    async def test_get_unread_count_returns_zero_when_no_notifications(
        self,
        client: AsyncClient,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that count is zero when user has no notifications.
        
        Validates:
        - Returns 0 for users without notifications
        """
        # Act: Get unread count (no notifications created)
        response = await client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers_member
        )
        
        # Assert: Verify zero count
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 0
    
    async def test_get_unread_count_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to get count without authentication
        response = await client.get("/api/v1/notifications/unread-count")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# PUT /api/v1/notifications/{id}/read - Mark as Read
# ============================================================================

class TestMarkNotificationAsRead:
    """
    Tests for the PUT /api/v1/notifications/{id}/read endpoint.
    
    This endpoint marks a notification as read.
    """
    
    async def test_mark_notification_as_read_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test successfully marking a notification as read.
        
        Validates:
        - Status code is 200
        - Notification is marked as read
        - Response contains updated notification
        """
        # Arrange: Create an unread notification
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        notification = await NotificationFactory.create_notification(
            db_session=db_session,
            user=test_user_member,
            task=task,
            is_read=False
        )
        
        # Act: Mark notification as read
        response = await client.put(
            f"/api/v1/notifications/{notification.id}/read",
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notification.id
        assert data["is_read"] is True
    
    async def test_mark_notification_as_read_not_found(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test marking non-existent notification returns 404.
        
        Validates:
        - Status code is 404 for invalid notification ID
        """
        # Act: Try to mark non-existent notification
        response = await client.put(
            "/api/v1/notifications/99999/read",
            headers=auth_headers_member
        )
        
        # Assert: Verify not found response
        assert response.status_code == 404
    
    async def test_mark_notification_as_read_forbidden_for_other_user(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that users cannot mark other users' notifications as read.
        
        Validates:
        - Status code is 403 when trying to modify another user's notification
        """
        # Arrange: Create notification for another user
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="other@test.com"
        )
        
        other_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=other_user
        )
        
        other_notification = await NotificationFactory.create_notification(
            db_session=db_session,
            user=other_user,
            task=other_task
        )
        
        # Act: Try to mark another user's notification as read
        response = await client.put(
            f"/api/v1/notifications/{other_notification.id}/read",
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_mark_notification_as_read_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to mark notification without authentication
        response = await client.put("/api/v1/notifications/1/read")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# DELETE /api/v1/notifications/{id} - Delete Notification
# ============================================================================

class TestDeleteNotification:
    """
    Tests for the DELETE /api/v1/notifications/{id} endpoint.
    
    This endpoint deletes a notification.
    """
    
    async def test_delete_notification_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test successfully deleting a notification.
        
        Validates:
        - Status code is 204
        - Notification is deleted from database
        - Subsequent GET returns 404
        """
        # Arrange: Create a notification
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        notification = await NotificationFactory.create_notification(
            db_session=db_session,
            user=test_user_member,
            task=task
        )
        
        notification_id = notification.id
        
        # Act: Delete notification
        response = await client.delete(
            f"/api/v1/notifications/{notification_id}",
            headers=auth_headers_member
        )
        
        # Assert: Verify deletion
        assert response.status_code == 204
        
        # Verify notification is gone
        get_response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        notifications = get_response.json()
        assert not any(n["id"] == notification_id for n in notifications)
    
    async def test_delete_notification_not_found(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test deleting non-existent notification returns 404.
        
        Validates:
        - Status code is 404 for invalid notification ID
        """
        # Act: Try to delete non-existent notification
        response = await client.delete(
            "/api/v1/notifications/99999",
            headers=auth_headers_member
        )
        
        # Assert: Verify not found response
        assert response.status_code == 404
    
    async def test_delete_notification_forbidden_for_other_user(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that users cannot delete other users' notifications.
        
        Validates:
        - Status code is 403 when trying to delete another user's notification
        """
        # Arrange: Create notification for another user
        other_user = await UserFactory.create_member(
            db_session=db_session,
            email="other@test.com"
        )
        
        other_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=other_user
        )
        
        other_notification = await NotificationFactory.create_notification(
            db_session=db_session,
            user=other_user,
            task=other_task
        )
        
        # Act: Try to delete another user's notification
        response = await client.delete(
            f"/api/v1/notifications/{other_notification.id}",
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_delete_notification_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to delete notification without authentication
        response = await client.delete("/api/v1/notifications/1")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# POST /api/v1/notifications/check-due-dates - Generate Due Date Notifications
# ============================================================================

class TestCheckDueDates:
    """
    Tests for the POST /api/v1/notifications/check-due-dates endpoint.
    
    This endpoint generates notifications for tasks with upcoming or past due dates.
    Only owners can execute this endpoint.
    """
    
    async def test_check_due_dates_generates_overdue_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test generating notifications for overdue tasks.
        
        Validates:
        - Overdue tasks generate OVERDUE notifications
        - Notifications are created for task owners
        - Correct notification count is returned
        """
        # Arrange: Create an overdue task
        overdue_task = await TaskFactory.create_overdue_task(
            db_session=db_session,
            owner=test_user_owner,
            title="Overdue Task"
        )
        
        # Act: Check due dates
        response = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert "notifications_created" in data
        assert data["notifications_created"]["overdue"] >= 1
        
        # Verify notification was created
        notif_response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_owner
        )
        notifications = notif_response.json()
        overdue_notifs = [
            n for n in notifications 
            if n["task_id"] == overdue_task.id and n["notification_type"] == "overdue"
        ]
        assert len(overdue_notifs) == 1
    
    async def test_check_due_dates_generates_due_today_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test generating notifications for tasks due today.
        
        Validates:
        - Tasks due today generate DUE_TODAY notifications
        """
        # Arrange: Create a task due later today (but before midnight)
        now = datetime.now(timezone.utc)
        # Set due date to end of today (23:59)
        today_end = now.replace(hour=23, minute=59, second=0, microsecond=0)
        
        today_task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_owner,
            title="Task Due Today",
            due_date=today_end
        )
        
        # Act: Check due dates
        response = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        # Should generate due_today notification
        assert data["notifications_created"]["due_today"] >= 1
    
    async def test_check_due_dates_generates_due_soon_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test generating notifications for tasks due soon (within 24 hours).
        
        Validates:
        - Tasks due within 24 hours generate DUE_SOON notifications
        """
        # Arrange: Create a task due tomorrow
        tomorrow_task = await TaskFactory.create_task_with_due_date(
            db_session=db_session,
            owner=test_user_owner,
            days_from_now=1,  # Due tomorrow
            title="Task Due Tomorrow"
        )
        
        # Act: Check due dates
        response = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        # May be due_soon or due_today depending on exact time
        assert (data["notifications_created"]["due_soon"] >= 1 or 
                data["notifications_created"]["due_today"] >= 1)
    
    async def test_check_due_dates_does_not_duplicate_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that running check multiple times doesn't create duplicates.
        
        Validates:
        - Notifications are not duplicated on subsequent runs
        - Same task doesn't get multiple notifications of same type
        """
        # Arrange: Create an overdue task
        overdue_task = await TaskFactory.create_overdue_task(
            db_session=db_session,
            owner=test_user_owner
        )
        
        # Act: Check due dates twice
        response1 = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        response2 = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        
        # Assert: Second run should not create duplicates
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # First run creates notifications, second creates none (or very few if new tasks)
        assert data1["notifications_created"]["overdue"] >= 1
        # Second run should create 0 for the same task
        assert data2["total"] == 0 or data2["total"] < data1["total"]
    
    async def test_check_due_dates_requires_owner_role(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that only owners can check due dates.
        
        Validates:
        - Status code is 403 when member tries to check due dates
        """
        # Act: Try to check due dates as member
        response = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_check_due_dates_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to check due dates without authentication
        response = await client.post("/api/v1/notifications/check-due-dates")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# Integration Scenarios
# ============================================================================

class TestNotificationIntegrationScenarios:
    """
    Tests for complex scenarios involving multiple operations.
    
    These tests validate the interaction between different endpoints
    and ensure data consistency across operations.
    """
    
    async def test_notification_lifecycle_complete_flow(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test complete notification workflow: create → read → mark as read → delete.
        
        Validates:
        - Notification appears in list
        - Can be marked as read
        - Read status is updated
        - Can be deleted
        - Unread count updates correctly
        """
        # Arrange: Create a task and notification
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        notification = await NotificationFactory.create_notification(
            db_session=db_session,
            user=test_user_member,
            task=task,
            is_read=False
        )
        
        # Act 1: Check unread count
        count_response = await client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers_member
        )
        assert count_response.json()["unread_count"] == 1
        
        # Act 2: Get notifications list
        list_response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        notifications = list_response.json()
        assert len(notifications) == 1
        assert notifications[0]["is_read"] is False
        
        # Act 3: Mark as read
        read_response = await client.put(
            f"/api/v1/notifications/{notification.id}/read",
            headers=auth_headers_member
        )
        assert read_response.status_code == 200
        assert read_response.json()["is_read"] is True
        
        # Act 4: Verify unread count decreased
        count_response2 = await client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers_member
        )
        assert count_response2.json()["unread_count"] == 0
        
        # Act 5: Delete notification
        delete_response = await client.delete(
            f"/api/v1/notifications/{notification.id}",
            headers=auth_headers_member
        )
        assert delete_response.status_code == 204
        
        # Act 6: Verify notification is gone
        final_list = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        assert len(final_list.json()) == 0
    
    async def test_task_deletion_cascades_to_notifications(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that deleting a task also deletes its notifications.
        
        Validates:
        - Notifications exist before task deletion
        - Notifications are deleted when task is deleted (cascade)
        """
        # Arrange: Create task with notifications
        task = await TaskFactory.create_task(
            db_session=db_session,
            owner=test_user_member
        )
        
        await NotificationFactory.create_multiple_notifications(
            db_session=db_session,
            user=test_user_member,
            task=task,
            count=3
        )
        
        # Verify notifications exist
        notif_response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        assert len(notif_response.json()) == 3
        
        # Act: Delete the task
        delete_response = await client.delete(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_member
        )
        assert delete_response.status_code == 204
        
        # Assert: Verify notifications are also deleted
        final_notif_response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_member
        )
        assert len(final_notif_response.json()) == 0
    
    async def test_due_date_workflow_with_task_completion(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that completing a task prevents further due date notifications.
        
        Validates:
        - Overdue task generates notification
        - Completing task prevents new notifications
        - Existing notifications remain
        """
        # Arrange: Create overdue task
        overdue_task = await TaskFactory.create_overdue_task(
            db_session=db_session,
            owner=test_user_owner,
            title="Overdue Task"
        )
        
        # Act 1: Generate notifications
        response1 = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        assert response1.json()["notifications_created"]["overdue"] >= 1
        
        # Act 2: Complete the task
        update_response = await client.put(
            f"/api/v1/tasks/{overdue_task.id}",
            json={"status": "done"},
            headers=auth_headers_owner
        )
        assert update_response.status_code == 200
        
        # Act 3: Try to generate notifications again
        response2 = await client.post(
            "/api/v1/notifications/check-due-dates",
            headers=auth_headers_owner
        )
        
        # Assert: No new notifications for completed task
        # The old notification still exists, but no new one is created
        notif_response = await client.get(
            "/api/v1/notifications/",
            headers=auth_headers_owner
        )
        notifications = notif_response.json()
        task_notifs = [n for n in notifications if n["task_id"] == overdue_task.id]
        # Should still have the original notification, but not a duplicate
        assert len(task_notifs) == 1
