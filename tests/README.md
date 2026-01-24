# Testing Guide

This directory contains integration tests for the Task Manager API using pytest and a real PostgreSQL test database.

## Architecture

The test suite follows SOLID principles and clean architecture:

### Structure
```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── test_config.py        # Test-specific settings
├── factories.py          # Factory classes for creating test data
├── test_tasks.py         # Integration tests for task endpoints
├── test_users.py         # Integration tests for user endpoints
├── test_notifications.py # Integration tests for notification endpoints
└── README.md            # This file
```

### Key Components

#### 1. **Test Configuration** (`test_config.py`)
- Manages test-specific settings
- Uses a separate test database to ensure isolation
- Can be configured via `.env.test` file

#### 2. **Fixtures** (`conftest.py`)
Provides reusable test components following dependency injection:
- `test_engine`: Database engine for the entire test session
- `test_db_setup`: Creates/drops database schema per test
- `db_session`: Database session for each test (ensures isolation)
- `client`: HTTP client for making API requests
- `test_user_owner` / `test_user_member`: Pre-configured test users
- `owner_token` / `member_token`: JWT tokens for authentication
- `auth_headers_owner` / `auth_headers_member`: Ready-to-use auth headers

#### 3. **Factories** (`factories.py`)
Factory classes for creating test data:
- `TaskFactory`: Create tasks with various configurations
- `CommentFactory`: Create comments on tasks
- `UserFactory`: Create users with different roles and states
- `NotificationFactory`: Create notifications with different types and states
- `TestDataBuilder`: Build complex test scenarios with multiple entities

#### 4. **Test Suites**

**Task Tests** (`test_tasks.py`):
Comprehensive integration tests organized by endpoint:
- `TestListTasks`: GET /api/v1/tasks
- `TestCreateTask`: POST /api/v1/tasks
- `TestGetTask`: GET /api/v1/tasks/{id}
- `TestUpdateTask`: PUT /api/v1/tasks/{id}
- `TestDeleteTask`: DELETE /api/v1/tasks/{id}
- `TestComplexTaskScenarios`: Multi-step workflows

**User Tests** (`test_users.py`):
Integration tests for user management endpoints:
- `TestGetCurrentUser`: GET /api/v1/users/me
- `TestListUsers`: GET /api/v1/users/ (role-based access)
- `TestCreateUser`: POST /api/v1/users/ (owner-only)
- `TestUserIntegrationScenarios`: Complete user lifecycle flows

**Notification Tests** (`test_notifications.py`):
Integration tests for notification endpoints:
- `TestGetNotifications`: GET /api/v1/notifications/ (filtering, pagination)
- `TestGetUnreadCount`: GET /api/v1/notifications/unread-count
- `TestMarkNotificationAsRead`: PUT /api/v1/notifications/{id}/read
- `TestDeleteNotification`: DELETE /api/v1/notifications/{id}
- `TestCheckDueDates`: POST /api/v1/notifications/check-due-dates (owner-only)
- `TestNotificationIntegrationScenarios`: Complex notification workflows

**Comment Tests** (`test_comments.py`):
Integration tests for comment endpoints:
- `TestGetTaskComments`: GET /api/v1/tasks/{task_id}/comments (owner and OWNER role access)
- `TestCreateComment`: POST /api/v1/tasks/{task_id}/comments (owner and OWNER role access)
- `TestUpdateComment`: PUT /api/v1/tasks/comments/{comment_id} (author-only)
- `TestDeleteComment`: DELETE /api/v1/tasks/comments/{comment_id} (author and OWNER role)
- `TestCommentIntegrationScenarios`: Complex comment workflows and moderation

## Setup

### 1. Install Dependencies
```bash
# Install test dependencies
uv pip install -e ".[dev]"
```

### 2. Create Test Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create test database
CREATE DATABASE taskmanager_test;

# Grant permissions to your user
GRANT ALL PRIVILEGES ON DATABASE taskmanager_test TO taskmanager;
```

### 3. Configure Test Environment (Optional)
Create a `.env.test` file to override default test settings:
```env
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/taskmanager_test
SECRET_KEY=your-test-secret-key
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_tasks.py
```

### Run Specific Test Class
```bash
pytest tests/test_tasks.py::TestCreateTask
```

### Run Specific Test
```bash
pytest tests/test_tasks.py::TestCreateTask::test_create_task_success
```

### Run with Coverage Report
```bash
pytest --cov=src --cov-report=html
```

### Run Tests in Parallel (requires pytest-xdist)
```bash
pytest -n auto
```

## Test Patterns

### AAA Pattern
All tests follow the Arrange-Act-Assert pattern:
```python
async def test_example(client, auth_headers):
    # Arrange: Set up test data
    task_data = {"title": "Test Task"}
    
    # Act: Perform the action
    response = await client.post("/api/v1/tasks", json=task_data, headers=auth_headers)
    
    # Assert: Verify the outcome
    assert response.status_code == 201
```

### Using Factories
```python
# Create a task using TaskFactory
async def test_with_task_factory(db_session, test_user_owner):
    task = await TaskFactory.create_task(
        db_session=db_session,
        owner=test_user_owner,
        title="Custom Title"
    )
    assert task.id is not None
    assert task.title == "Custom Title"

# Create a user using UserFactory
async def test_with_user_factory(db_session):
    user = await UserFactory.create_member(
        db_session=db_session,
        email="test@example.com"
    )
    assert user.role == UserRole.MEMBER
    
    # Create multiple users at once
    users = await UserFactory.create_multiple_users(
        db_session=db_session,
        count=5
    )
    assert len(users) == 5
```

### Building Complex Scenarios
```python
async def test_complex_scenario(db_session, test_user_owner):
    # Use TestDataBuilder for complex setups
    builder = TestDataBuilder(db_session)
    
    data = await (
        builder
        .with_tasks_for_user(test_user_owner, count=5)
        .build()
    )
    
    assert len(data["tasks"]) == 5
```

## Best Practices

### 1. Test Isolation
- Each test gets a fresh database (via `test_db_setup` fixture)
- Tests can run in any order
- No shared state between tests

### 2. Meaningful Test Names
- Test names describe the scenario: `test_create_task_requires_authentication`
- Class names group related tests: `TestCreateTask`

### 3. Clear Assertions
- Assert specific values, not just existence
- Include descriptive failure messages when needed
- Test both success and failure cases

### 4. Documentation
- Each test has a docstring explaining what it tests
- Inline comments for complex logic
- Group related tests in classes

### 5. Performance
- Session-scoped fixtures for expensive operations (database engine)
- Function-scoped fixtures for isolation (database session)
- Use factories to reduce boilerplate

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose up -d db`
- Verify database exists: `psql -U postgres -c "\l"`
- Check connection string in test_config.py

### Test Failures
- Run with `-v` for verbose output
- Use `-s` to see print statements
- Check test database state: Database is reset between tests

### Import Errors
- Ensure you're running from project root
- Install in development mode: `uv pip install -e ".[dev]"`

## Contributing

When adding new tests:
1. Follow the existing structure and patterns
2. Use appropriate fixtures instead of duplicating setup
3. Add docstrings explaining what the test verifies
4. Ensure tests are independent and isolated
5. Update this README if adding new test files or patterns

## Next Steps

Consider adding tests for:
- Task assignment and ownership transfer
- Permission edge cases
- Performance/load testing
- End-to-end user workflows
