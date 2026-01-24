"""
Integration tests for user endpoints.

This module contains comprehensive integration tests for the user API endpoints.
Tests are organized by endpoint and follow the Arrange-Act-Assert (AAA) pattern.

Test Structure:
- TestGetCurrentUser: Tests for GET /api/v1/users/me
- TestListUsers: Tests for GET /api/v1/users/
- TestCreateUser: Tests for POST /api/v1/users/

Each test class follows SOLID principles:
- Single Responsibility: Each test validates one specific behavior
- Open/Closed: Tests are designed to be extended without modification
- Interface Segregation: Tests use only the fixtures they need
- Dependency Inversion: Tests depend on fixtures (abstractions) not concrete implementations

Note: Authentication and basic user creation tests are already covered in task tests,
so we focus on user-specific functionality and edge cases not covered there.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserRole
from tests.factories import UserFactory


# ============================================================================
# GET /api/v1/users/me - Get Current User
# ============================================================================

class TestGetCurrentUser:
    """
    Tests for the GET /api/v1/users/me endpoint.
    
    This endpoint returns information about the currently authenticated user.
    """
    
    async def test_get_current_user_success_as_owner(
        self,
        client: AsyncClient,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that an authenticated owner can get their own information.
        
        Validates:
        - Status code is 200
        - Response contains correct user data
        - Password is not exposed
        """
        # Arrange: User and headers are provided by fixtures
        
        # Act: Get current user information
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_owner.email
        assert data["id"] == test_user_owner.id
        assert data["role"] == UserRole.OWNER.value
        assert data["is_active"] is True
        assert "created_at" in data
        # Ensure password is not exposed
        assert "password" not in data
        assert "hashed_password" not in data
    
    async def test_get_current_user_success_as_member(
        self,
        client: AsyncClient,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that an authenticated member can get their own information.
        
        Validates:
        - Status code is 200
        - Response contains correct member user data
        """
        # Act: Get current user information
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_member.email
        assert data["id"] == test_user_member.id
        assert data["role"] == UserRole.MEMBER.value
        assert data["is_active"] is True
    
    async def test_get_current_user_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to get current user without authentication
        response = await client.get("/api/v1/users/me")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401
        assert "detail" in response.json()
    
    async def test_get_current_user_with_invalid_token(
        self,
        client: AsyncClient
    ):
        """
        Test that invalid tokens are rejected.
        
        Validates:
        - Status code is 403 with invalid token (could not validate credentials)
        """
        # Arrange: Create invalid authorization header
        invalid_headers = {"Authorization": "Bearer invalid_token_xyz123"}
        
        # Act: Try to get current user with invalid token
        response = await client.get(
            "/api/v1/users/me",
            headers=invalid_headers
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403


# ============================================================================
# GET /api/v1/users/ - List Users
# ============================================================================

class TestListUsers:
    """
    Tests for the GET /api/v1/users/ endpoint.
    
    This endpoint returns a list of users. Behavior differs based on user role:
    - OWNER: Can see all users
    - MEMBER: Can only see themselves
    """
    
    async def test_list_users_as_owner_returns_all_users(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that an owner can see all users.
        
        Validates:
        - Status code is 200
        - Response contains all active users
        - Users are properly formatted
        """
        # Arrange: Create additional users
        await UserFactory.create_multiple_users(
            db_session=db_session,
            count=3,
            role=UserRole.MEMBER
        )
        
        # Act: List users as owner
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have owner + 3 members + test_user_member from conftest = 5 users
        assert len(data) >= 4
        
        # Verify all users have required fields
        for user in data:
            assert "id" in user
            assert "email" in user
            assert "role" in user
            assert "is_active" in user
            assert "created_at" in user
            assert "password" not in user
    
    async def test_list_users_as_member_returns_only_self(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_member: User,
        auth_headers_member: dict
    ):
        """
        Test that a member can only see themselves.
        
        Validates:
        - Status code is 200
        - Response contains only the member's own user
        - Other users are not exposed
        """
        # Arrange: Create additional users that member should NOT see
        await UserFactory.create_multiple_users(
            db_session=db_session,
            count=3,
            role=UserRole.MEMBER
        )
        
        # Act: List users as member
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers_member
        )
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Member should only see themselves
        assert len(data) == 1
        assert data[0]["id"] == test_user_member.id
        assert data[0]["email"] == test_user_member.email
    
    async def test_list_users_excludes_inactive_users(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that inactive users are excluded from the list.
        
        Validates:
        - Inactive users don't appear in results
        - Active users are still returned
        """
        # Arrange: Create active and inactive users
        active_user = await UserFactory.create_member(
            db_session=db_session,
            email="active@test.com"
        )
        await UserFactory.create_inactive_user(
            db_session=db_session,
            email="inactive@test.com"
        )
        
        # Act: List users as owner
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers_owner
        )
        
        # Assert: Verify inactive user is not in results
        assert response.status_code == 200
        data = response.json()
        emails = [user["email"] for user in data]
        assert active_user.email in emails
        assert "inactive@test.com" not in emails
    
    async def test_list_users_pagination(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test pagination parameters (skip and limit).
        
        Validates:
        - skip parameter works correctly
        - limit parameter works correctly
        - Results are properly limited
        """
        # Arrange: Create multiple users
        await UserFactory.create_multiple_users(
            db_session=db_session,
            count=10,
            email_prefix="pagination"
        )
        
        # Act: Request with pagination
        response = await client.get(
            "/api/v1/users/?skip=2&limit=3",
            headers=auth_headers_owner
        )
        
        # Assert: Verify pagination
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3  # Should respect limit
    
    async def test_list_users_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Act: Try to list users without authentication
        response = await client.get("/api/v1/users/")
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401


# ============================================================================
# POST /api/v1/users/ - Create User
# ============================================================================

class TestCreateUser:
    """
    Tests for the POST /api/v1/users/ endpoint.
    
    This endpoint allows owners to create new users.
    Only users with OWNER role can create new users.
    """
    
    async def test_create_user_success_as_owner(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers_owner: dict
    ):
        """
        Test that an owner can successfully create a new user.
        
        Validates:
        - Status code is 201
        - User is created with correct data
        - Password is hashed (not returned in response)
        - User can be retrieved from database
        """
        # Arrange: Prepare user data
        user_data = {
            "email": "newuser@test.com",
            "password": "securepassword123",
            "role": "member"
        }
        
        # Act: Create user as owner
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        
        # Verify user exists in database
        from src.repositories.user import UserRepository
        created_user = await UserRepository.get_by_email(
            db=db_session,
            email=user_data["email"]
        )
        assert created_user is not None
        assert created_user.email == user_data["email"]
        # Verify password was hashed
        assert created_user.hashed_password != user_data["password"]
    
    async def test_create_user_with_owner_role(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test that an owner can create another owner.
        
        Validates:
        - Owner can create users with OWNER role
        - Created user has correct role
        """
        # Arrange: Prepare owner user data
        user_data = {
            "email": "newowner@test.com",
            "password": "securepassword123",
            "role": "owner"
        }
        
        # Act: Create owner user
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == UserRole.OWNER.value
    
    async def test_create_user_duplicate_email_fails(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers_owner: dict
    ):
        """
        Test that creating a user with existing email fails.
        
        Validates:
        - Status code is 400 for duplicate email
        - Appropriate error message is returned
        """
        # Arrange: Create a user first
        existing_user = await UserFactory.create_member(
            db_session=db_session,
            email="existing@test.com"
        )
        
        # Act: Try to create user with same email
        user_data = {
            "email": existing_user.email,
            "password": "password123",
            "role": "member"
        }
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "email" in response.json()["detail"].lower()
    
    async def test_create_user_requires_owner_role(
        self,
        client: AsyncClient,
        auth_headers_member: dict
    ):
        """
        Test that only owners can create users.
        
        Validates:
        - Status code is 403 when member tries to create user
        - Members cannot create new users
        """
        # Arrange: Prepare user data
        user_data = {
            "email": "unauthorized@test.com",
            "password": "password123",
            "role": "member"
        }
        
        # Act: Try to create user as member
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_member
        )
        
        # Assert: Verify forbidden response
        assert response.status_code == 403
    
    async def test_create_user_requires_authentication(
        self,
        client: AsyncClient
    ):
        """
        Test that the endpoint requires authentication.
        
        Validates:
        - Status code is 401 when no token is provided
        """
        # Arrange: Prepare user data
        user_data = {
            "email": "noauth@test.com",
            "password": "password123",
            "role": "member"
        }
        
        # Act: Try to create user without authentication
        response = await client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        # Assert: Verify unauthorized response
        assert response.status_code == 401
    
    async def test_create_user_validates_email_format(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test that invalid email format is rejected.
        
        Validates:
        - Status code is 422 for invalid email
        - Validation error message is returned
        """
        # Arrange: Prepare data with invalid email
        user_data = {
            "email": "not-an-email",
            "password": "password123",
            "role": "member"
        }
        
        # Act: Try to create user with invalid email
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422
        assert "detail" in response.json()
    
    async def test_create_user_validates_required_fields(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test that required fields are validated.
        
        Validates:
        - Email is required
        - Password is required
        - Role is required
        """
        # Arrange: Prepare incomplete data
        incomplete_data = {
            "email": "test@test.com"
            # Missing password and role
        }
        
        # Act: Try to create user with missing fields
        response = await client.post(
            "/api/v1/users/",
            json=incomplete_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422
    
    async def test_create_user_validates_role_enum(
        self,
        client: AsyncClient,
        auth_headers_owner: dict
    ):
        """
        Test that role must be a valid enum value.
        
        Validates:
        - Invalid role values are rejected
        - Status code is 422 for invalid role
        """
        # Arrange: Prepare data with invalid role
        user_data = {
            "email": "test@test.com",
            "password": "password123",
            "role": "invalid_role"
        }
        
        # Act: Try to create user with invalid role
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_owner
        )
        
        # Assert: Verify validation error
        assert response.status_code == 422


# ============================================================================
# Integration Scenarios
# ============================================================================

class TestUserIntegrationScenarios:
    """
    Tests for complex scenarios involving multiple operations.
    
    These tests validate the interaction between different endpoints
    and ensure data consistency across operations.
    """
    
    async def test_owner_creates_member_who_can_access_api(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers_owner: dict
    ):
        """
        Test complete flow: owner creates member, member can authenticate and access API.
        
        Validates:
        - Owner creates new member successfully
        - New member can log in
        - New member can access their own data
        - New member cannot see other users
        """
        # Arrange: Prepare new member data
        new_member_data = {
            "email": "newmember@test.com",
            "password": "memberpass123",
            "role": "member"
        }
        
        # Act 1: Owner creates new member
        create_response = await client.post(
            "/api/v1/users/",
            json=new_member_data,
            headers=auth_headers_owner
        )
        assert create_response.status_code == 201
        
        # Act 2: New member logs in
        login_response = await client.post(
            "/api/v1/login/access-token",
            data={
                "username": new_member_data["email"],
                "password": new_member_data["password"]
            }
        )
        assert login_response.status_code == 200
        member_token = login_response.json()["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}
        
        # Act 3: Member accesses /users/me
        me_response = await client.get(
            "/api/v1/users/me",
            headers=member_headers
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == new_member_data["email"]
        
        # Act 4: Member tries to list all users (should only see self)
        users_response = await client.get(
            "/api/v1/users/",
            headers=member_headers
        )
        assert users_response.status_code == 200
        users_list = users_response.json()
        assert len(users_list) == 1
        assert users_list[0]["email"] == new_member_data["email"]
    
    async def test_multiple_owners_can_manage_users(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user_owner: User,
        auth_headers_owner: dict
    ):
        """
        Test that multiple owners can independently manage users.
        
        Validates:
        - First owner creates second owner
        - Second owner can create members
        - Both owners can see all users
        """
        # Act 1: First owner creates second owner
        second_owner_data = {
            "email": "owner2@test.com",
            "password": "ownerpass123",
            "role": "owner"
        }
        create_response = await client.post(
            "/api/v1/users/",
            json=second_owner_data,
            headers=auth_headers_owner
        )
        assert create_response.status_code == 201
        
        # Act 2: Second owner logs in
        login_response = await client.post(
            "/api/v1/login/access-token",
            data={
                "username": second_owner_data["email"],
                "password": second_owner_data["password"]
            }
        )
        assert login_response.status_code == 200
        second_owner_token = login_response.json()["access_token"]
        second_owner_headers = {"Authorization": f"Bearer {second_owner_token}"}
        
        # Act 3: Second owner creates a member
        member_data = {
            "email": "member.by.owner2@test.com",
            "password": "memberpass123",
            "role": "member"
        }
        member_response = await client.post(
            "/api/v1/users/",
            json=member_data,
            headers=second_owner_headers
        )
        assert member_response.status_code == 201
        
        # Act 4: Both owners can see all users
        first_owner_users = await client.get(
            "/api/v1/users/",
            headers=auth_headers_owner
        )
        second_owner_users = await client.get(
            "/api/v1/users/",
            headers=second_owner_headers
        )
        
        # Assert: Both see the same users
        assert first_owner_users.status_code == 200
        assert second_owner_users.status_code == 200
        first_emails = {u["email"] for u in first_owner_users.json()}
        second_emails = {u["email"] for u in second_owner_users.json()}
        assert first_emails == second_emails
        assert member_data["email"] in first_emails
