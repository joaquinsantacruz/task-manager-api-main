# Task Manager API - Complete Documentation

> A full-stack task management application built with FastAPI and React, featuring role-based access control, real-time notifications, and comprehensive task collaboration tools.

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/joaquinsantacruz/task-manager-api-main/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/joaquinsantacruz/task-manager-api-main/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/joaquinsantacruz/task-manager-api-main/badge.svg?branch=main)](https://coveralls.io/github/joaquinsantacruz/task-manager-api-main?branch=main)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?style=flat&logo=React&logoColor=white)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-3178C6.svg?style=flat&logo=TypeScript&logoColor=white)](https://www.typescriptlang.org/)

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Design Patterns](#design-patterns)
- [SOLID Principles Application](#solid-principles-application)
- [Security Decisions](#security-decisions)
- [Database Design](#database-design)
- [Logging System](#logging-system)
- [Troubleshooting](#troubleshooting)
- [Areas for Improvement](#areas-for-improvement)
- [Known Issues](#known-issues)
- [Additional Resources](#additional-resources)

---

## Overview

### What is This Project?

Task Manager API is a modern, full-stack application designed for efficient task management and team collaboration. It provides:

- **Robust RESTful API** built with FastAPI
- **Responsive React frontend** with TypeScript
- **Role-Based Access Control (RBAC)** with Owner and Member roles
- **Real-time notifications** for due date tracking
- **Task commenting** for team collaboration
- **Comprehensive task lifecycle management**

### User Roles

| Role | Permissions |
|------|-------------|
| **OWNER** | Full administrative access to all tasks and users |
| **MEMBER** | Access to personal tasks with limited permissions |

### Features

#### Core Functionality
- **Task Management**: Create, read, update, and delete tasks with status tracking
- **Role-Based Access Control (RBAC)**: Owner and Member roles with granular permissions
- **User Authentication**: JWT-based authentication with secure token handling
- **Task Comments**: Collaborative commenting system on tasks
- **Smart Notifications**: Automated due date notifications (overdue, due today, due soon)
- **Task Assignment**: Owners can reassign tasks to other users
- **Due Date Management**: Set and track task deadlines with visual indicators

#### Technical Features
- 🔒 **Security**: Argon2 password hashing, JWT tokens, CORS protection
- 📊 **Comprehensive Logging**: Backend and frontend logging with file rotation
- 🧪 **Test Coverage**: 98 test cases with pytest
- 🚀 **CI/CD Pipeline**: Automated testing and coverage reporting with CircleCI
- 🔄 **Real-time Updates**: Automatic notification polling
- 📄 **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- 🐳 **Docker Support**: Containerized deployment with Docker Compose

### Tech Stack

#### Backend
- **Framework**: FastAPI 0.115.6
- **Language**: Python 3.13
- **Database**: PostgreSQL 16 with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT with python-jose
- **Password Hashing**: Argon2
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Package Manager**: uv

#### Frontend
- **Framework**: React 18.3.1
- **Language**: TypeScript 5.6.2
- **Build Tool**: Vite 6.0.3
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS

#### DevOps & Tools
- **CI/CD**: CircleCI
- **Code Coverage**: Coveralls
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git
- **API Testing**: Swagger UI

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
docker-compose up -d
```

Everything is handled automatically:
- PostgreSQL database starts
- Migrations run automatically
- Sample data is seeded
- Backend API starts
- Frontend starts

### Option 2: Local Development

```bash
# Full setup (backend + frontend + database)
./setup-dev.sh

# Start the app
source .venv/bin/activate
uvicorn src.main:app --reload

# In another terminal:
cd frontend && npm run dev
```

The script will:
- Install `uv` (Python package manager) if needed
- Create a Python 3.13 virtual environment
- Install backend dependencies
- Install frontend dependencies (npm)
- Create the `.env` file
- Setup the database and run migrations

### Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost | React user interface |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Database | localhost:5432 | PostgreSQL |

### Default Credentials

**Owner user:**
- Email: `admin@admin.com`
- Password: `admin123`

**Member user:**
- Email: `john.doe@example.com`
- Password: `password123`

### Stop the Application

```bash
docker-compose down
```

To also remove data volumes:

```bash
docker-compose down -v
```

---

## Project Structure

```
task-manager-api/
├── src/                          # Backend source code
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/        # API endpoints
│   ├── core/                     # Core configurations
│   │   ├── config.py            # Settings
│   │   ├── security.py          # Auth utilities
│   │   ├── logger.py            # Logging setup
│   │   └── permissions.py       # RBAC logic
│   ├── db/                       # Database configuration
│   ├── models/                   # SQLAlchemy models
│   ├── repositories/             # Data access layer
│   ├── schemas/                  # Pydantic schemas
│   └── services/                 # Business logic
├── frontend/                     # Frontend source code
│   └── src/
│       ├── api/                  # API client
│       ├── components/           # React components
│       ├── context/              # React context
│       ├── hooks/                # Custom hooks
│       ├── pages/                # Page components
│       ├── services/             # API services
│       └── utils/                # Utilities
├── tests/                        # Backend tests
├── alembic/                      # Database migrations
├── logs/                         # Application logs
├── .circleci/                    # CI/CD configuration
├── docker-compose.yml            # Docker composition
├── pyproject.toml               # Python dependencies
└── README.md                     # This file
```

---

## Architecture & Design Decisions

### 1. Layered Architecture (Repository-Service-Controller Pattern)

**Decision:** Implemented a clean 3-layer architecture separating concerns.

**Structure:**
```
┌─────────────────┐
│   Controllers   │  (API endpoints - src/api/v1/endpoints/)
│   (FastAPI)     │
└────────┬────────┘
         │
┌────────▼────────┐
│    Services     │  (Business logic - src/services/)
│                 │
└────────┬────────┘
         │
┌────────▼────────┐
│  Repositories   │  (Data access - src/repositories/)
│  (SQLAlchemy)   │
└─────────────────┘
```

**Why:**
- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Can test business logic independently of database/HTTP
- **Maintainability**: Changes to one layer don't cascade to others
- **Flexibility**: Easy to swap implementations (e.g., change database)

**Trade-off:** More files and boilerplate, but significantly improved maintainability.

---

### 2. Async/Await with SQLAlchemy 2.0

**Decision:** Used fully asynchronous database operations with SQLAlchemy 2.0's async support.

**Configuration:**
```python
# src/db/session.py
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

**Why:**
- **Performance**: Non-blocking I/O allows handling multiple requests concurrently
- **Scalability**: Better resource utilization under high load
- **Modern Python**: Aligns with FastAPI's async-first design
- **Real async**: Using `asyncpg` driver (not blocking psycopg2)

**Challenges:**
- More complex than sync code
- All database operations must be awaited
- Test fixtures require special async handling

---

### 3. JWT-Based Stateless Authentication

**Decision:** Implemented JWT tokens for authentication instead of session-based auth.

**Why:**
- **Stateless**: No server-side session storage needed
- **Scalability**: Easy to scale horizontally
- **Mobile-friendly**: Works seamlessly with mobile apps
- **API-first**: Perfect for REST APIs

**Trade-offs:**
- Cannot invalidate tokens before expiration (no logout on server)
- Token size larger than session ID
- Need refresh token mechanism for production

**Security Measures:**
- Token expiration (30 minutes configurable)
- HMAC-SHA256 signing
- Secret key from environment variables
- Tokens include user identifier (email) in payload

---

### 4. Role-Based Access Control (RBAC)

**Decision:** Implemented a two-role system (OWNER/MEMBER) with centralized permission logic.

**Roles:**
```python
class UserRole(str, enum.Enum):
    OWNER = "owner"   # Full administrative access
    MEMBER = "member" # Limited to own resources
```

**Permission Model:**
```python
# src/core/permissions.py

def require_owner_role(user: User) -> None:
    """Only OWNER can proceed"""
    if user.role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail=ERROR_OWNER_ROLE_REQUIRED)

def can_user_access_task(user: User, task: Task) -> bool:
    """OWNER can access any task, MEMBER only their own"""
    return task.owner_id == user.id or user.role == UserRole.OWNER

def can_user_modify_task(user: User, task: Task) -> bool:
    """Same as access for this app"""
    return task.owner_id == user.id or user.role == UserRole.OWNER
```

**Why Centralized:**
- **DRY**: Avoids duplicating permission logic across endpoints
- **Consistency**: Same rules applied everywhere
- **Testability**: Test permission logic in isolation
- **Maintainability**: Change permissions in one place

**Access Control Matrix:**

| Operation | OWNER | MEMBER |
|-----------|-------|--------|
| Create Task | ✅ | ✅ |
| View Own Tasks | ✅ | ✅ |
| View All Tasks | ✅ | ❌ |
| Update Own Tasks | ✅ | ✅ |
| Update Any Task | ✅ | ❌ |
| Delete Own Tasks | ✅ | ✅ |
| Delete Any Task | ✅ | ❌ |
| Change Task Owner | ✅ | ❌ |
| Create User | ✅ | ❌ |
| List All Users | ✅ | ❌ |
| Generate Notifications | ✅ | ❌ |

---

### 5. Centralized Configuration, Errors, and Constants

**Decision:** Created centralized modules for configuration, error messages, and constants.

**Files:**
- `src/core/config.py` - All environment variables and settings
- `src/core/errors.py` - Reusable error messages
- `src/core/constants.py` - Business rules and magic numbers

**Example:**
```python
# src/core/constants.py
DEFAULT_PAGE_SIZE = 100
TASK_TITLE_MIN_LENGTH = 1
TASK_TITLE_MAX_LENGTH = 100
USER_PASSWORD_MIN_LENGTH = 8

# src/core/errors.py
ERROR_TASK_NOT_FOUND = "Task not found"
ERROR_NO_TASK_ACCESS = "You do not have permission to access this task"
ERROR_OWNER_ROLE_REQUIRED = "This action requires OWNER role"

# Usage in code
raise HTTPException(status_code=404, detail=ERROR_TASK_NOT_FOUND)
```

**Benefits:**
- **Single Source of Truth**: Change values in one place
- **Consistency**: Same error messages across the app
- **No Magic Numbers**: All constraints are named and documented

---

### 6. Comprehensive Logging System

**Decision:** Implemented dual logging (backend + frontend) with structured formats.

**What We Log:**
- Authentication attempts (success/failure)
- API requests/responses
- User actions (task creation, deletion, etc.)
- Errors with stack traces
- Permission violations

**Why:**
- **Debugging**: Essential for troubleshooting production issues
- **Auditing**: Track who did what and when
- **Monitoring**: Detect patterns and anomalies
- **Compliance**: May be required for certain industries

**See:** [LOGGING.md](LOGGING.md) for complete documentation.

---

## Design Patterns

### 1. Repository Pattern

**What:** Abstracts data access logic from business logic.

**Implementation:**
```python
class TaskRepository:
    @staticmethod
    async def get_by_id(db, id): ...
    
    @staticmethod
    async def create(db, obj_in, owner_id): ...
    
    @staticmethod
    async def update(db, db_obj, obj_in): ...
```

**Benefits:**
- Testable business logic (can mock repositories)
- Can swap database implementations
- Consistent data access patterns

---

### 2. Dependency Injection

**What:** FastAPI's `Depends()` mechanism for injecting dependencies.

**Examples:**
```python
@router.get("/tasks")
async def read_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await TaskService.get_tasks_for_user(db, current_user)
```

**Benefits:**
- Testable (can inject mock dependencies)
- Clear dependencies visible in function signature
- Automatic dependency resolution by FastAPI

---

### 3. Factory Pattern (Tests)

**What:** Factory functions to create test data.

**Implementation:**
```python
# tests/factories.py
async def create_test_user(db, email, role=UserRole.MEMBER, is_active=True):
    user = User(email=email, hashed_password=hash, role=role, is_active=is_active)
    db.add(user)
    await db.commit()
    return user

async def create_test_task(db, owner_id, title="Test Task", ...):
    task = Task(title=title, owner_id=owner_id, ...)
    db.add(task)
    await db.commit()
    return task
```

**Benefits:**
- Reusable test data creation
- Consistent test setup
- Reduces test boilerplate

---

### 4. Service Layer Pattern

**What:** Encapsulates business logic separate from HTTP and data layers.

**Responsibilities:**
- Orchestrate repository calls
- Enforce business rules
- Handle permissions
- Transform data

**Example:**
```python
class TaskService:
    @staticmethod
    async def create_task(db, task_data, current_user):
        # Business rule: inactive users can't create tasks
        if not current_user.is_active:
            raise HTTPException(403, detail=ERROR_INACTIVE_USER_CREATE_TASK)
        
        # Delegate to repository
        task = await TaskRepository.create(db, task_data, current_user.id)
        return task
```

---

## SOLID Principles Application

### S - Single Responsibility Principle ✅

**Each class/module has one reason to change.**

**Examples:**

**1. Repositories** - Only responsible for data access
```python
class TaskRepository:
    # Only database queries, no business logic
    @staticmethod
    async def get_by_id(...): ...
```

**2. Services** - Only responsible for business logic
```python
class TaskService:
    # Only business rules, no HTTP or DB details
    @staticmethod
    async def create_task(...): ...
```

**3. Controllers** - Only responsible for HTTP handling
```python
@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_in: TaskCreate, ...):
    # Only HTTP concerns (request/response)
    return await TaskService.create_task(...)
```

**4. Permissions module** - Only responsible for authorization
```python
# src/core/permissions.py - Only permission logic
def require_owner_role(user): ...
def can_user_access_task(user, task): ...
```

---

### O - Open/Closed Principle ✅

**Open for extension, closed for modification.**

**Examples:**

**1. Notification Types** - Can add new types without changing existing code
```python
class NotificationType(str, enum.Enum):
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    # Easy to add: ASSIGNED = "assigned"
    # Easy to add: COMPLETED = "completed"
```

**2. Task Status** - Can extend statuses
```python
class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    # Easy to add: BLOCKED = "blocked"
    # Easy to add: ARCHIVED = "archived"
```

**3. Service Methods** - Can add new methods without changing existing ones
```python
class TaskService:
    @staticmethod
    async def create_task(...): ...  # Existing
    
    @staticmethod
    async def update_task(...): ...  # Existing
    
    # Can add new methods without modifying above
    @staticmethod
    async def archive_task(...): ...  # New (future)
```

---

### L - Liskov Substitution Principle ✅

**Subtypes must be substitutable for their base types.**

**Application:**
While we don't have explicit inheritance hierarchies, we follow LSP in:

**1. Dependency Injection** - All dependencies follow contracts
```python
# Any async function returning AsyncSession can be substituted
async def get_db() -> AsyncGenerator[AsyncSession, None]: ...
async def get_test_db() -> AsyncGenerator[AsyncSession, None]: ...  # Test substitute
```

**2. User Roles** - Both roles work with same User interface
```python
# Any User can be passed regardless of role
def can_user_access_task(user: User, task: Task):
    # Works for both OWNER and MEMBER
    return task.owner_id == user.id or user.role == UserRole.OWNER
```

---

### I - Interface Segregation Principle ✅

**Clients shouldn't depend on interfaces they don't use.**

**Examples:**

**1. Separate Schemas for Different Operations**
```python
class TaskCreate(BaseModel):  # Only fields needed for creation
    title: str
    description: Optional[str]
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime]

class TaskUpdate(BaseModel):  # All fields optional for updates
    title: Optional[str]
    description: Optional[str]
    status: Optional[TaskStatus]
    due_date: Optional[datetime]

class TaskResponse(TaskBase):  # Includes computed fields for responses
    id: int
    owner_id: int
    owner_email: Optional[str]
    created_at: datetime
```

**2. Specific Permission Functions** - Not one giant "check_permission"
```python
# Instead of check_permission(user, task, "read"), we have:
def can_user_access_task(user, task): ...      # Read permission
def can_user_modify_task(user, task): ...      # Write permission
def require_owner_role(user): ...               # Admin permission
```

---

### D - Dependency Inversion Principle ✅

**Depend on abstractions, not concretions.**

**Examples:**

**1. Services depend on Repository abstractions, not concrete DB**
```python
class TaskService:
    @staticmethod
    async def create_task(db: AsyncSession, ...):  # Depends on abstraction
        # Calls repository, not direct DB access
        task = await TaskRepository.create(db, ...)
```

**2. Controllers depend on Service abstractions**
```python
@router.post("/tasks")
async def create_task(task_in: TaskCreate, ...):
    # Depends on Service abstraction, not Repository or DB
    return await TaskService.create_task(...)
```

**3. Dependency Injection via FastAPI**
```python
# High-level endpoint depends on abstraction (get_current_user)
async def read_tasks(
    current_user: Annotated[User, Depends(get_current_user)],  # Abstraction
):
    # Can swap get_current_user implementation without changing endpoint
```

---

## Security Decisions

### 1. Password Hashing - Argon2

**Decision:** Use Argon2 instead of bcrypt.

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

**Why:**
- **Memory-hard**: Resistant to GPU/ASIC attacks
- **Modern**: Winner of Password Hashing Competition (2015)
- **Secure defaults**: Passlib handles salt generation

---

### 2. JWT Token Security

**Implementation:**
```python
# Token structure
{
  "exp": 1234567890,  # Expiration timestamp
  "sub": "user@example.com"  # User identifier
}

# Security measures
- HMAC-SHA256 signing
- 30-minute expiration (configurable)
- Secret key from environment
- UTC timezone for timestamps
```

**Known Limitations:**
- No token revocation (until expiration)
- No refresh tokens implemented
- Token stored in localStorage (XSS vulnerable)

---

### 3. Input Validation

**Decision:** Use Pydantic for all input validation.

```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=5000)
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Due date cannot be in the past")
        return v
```

**Benefits:**
- Automatic validation before business logic
- Type safety
- Clear error messages
- Self-documenting (Field descriptions)

---

### 4. SQL Injection Prevention

**Decision:** Use SQLAlchemy's parameter binding (never string concatenation).

All queries use SQLAlchemy's safe query building.

---

### 5. CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Design

### 1. Schema Design

**Entity Relationship Diagram:**

```
┌─────────────┐         ┌─────────────┐
│    User     │         │    Task     │
├─────────────┤         ├─────────────┤
│ id (PK)     │◄────────┤ id (PK)     │
│ email       │    1:N  │ title       │
│ password    │         │ description │
│ role        │         │ status      │
│ is_active   │         │ due_date    │
└─────────────┘         │ owner_id(FK)│
      △                 └──────┬──────┘
      │                        △
      │ 1:N                    │ 1:N
      │                        │
┌─────┴──────┐         ┌───────┴─────────┐
│Notification│         │    Comment      │
├────────────┤         ├─────────────────┤
│ id (PK)    │         │ id (PK)         │
│ message    │         │ content         │
│ type       │         │ task_id (FK)    │
│ is_read    │         │ author_id (FK)  │
│ user_id(FK)│         └─────────────────┘
│ task_id(FK)│
└────────────┘
```

**Relationships:**
- User → Task (1:N) - One user owns many tasks
- Task → Comment (1:N) - One task has many comments
- User → Comment (1:N) - One user authors many comments
- Task → Notification (1:N) - One task can have many notifications
- User → Notification (1:N) - One user receives many notifications

---

### 2. Cascade Deletes

**Decision:** Use database-level and ORM-level cascades.

```python
# Database level (ondelete="CASCADE")
user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))

# ORM level (cascade="all, delete-orphan")
tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
```

**Behavior:**
- Delete user → All their tasks, comments, notifications deleted
- Delete task → All its comments and notifications deleted

---

### 3. Eager Loading

**Decision:** Use `joinedload` to prevent N+1 query problems.

---

### 4. Indexes

**Decision:** Add indexes on frequently queried columns.

```python
email = Column(String, unique=True, index=True)  # For login queries
id = Column(Integer, primary_key=True, index=True)  # Automatic
```

**Missing indexes** (for future optimization):
- `task.owner_id` (for user's tasks queries)
- `task.status` (for status filtering)
- `notification.user_id, is_read` (composite for unread notifications)

---

## Logging System

The project implements dual logging for both backend and frontend.

### Backend (Python)

- **Location**: `src/core/logger.py`
- **Output**: Console + rotating files (`logs/app.log`, `logs/error.log`)
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Format**: `[timestamp] - [logger_name] - [level] - [message]`

**Usage:**
```python
from src.core.logger import get_logger
logger = get_logger(__name__)
logger.info("User logged in", extra={"user_id": 1})
```

### Frontend (TypeScript)

- **Location**: `frontend/src/utils/logger.ts`
- **Output**: Browser console
- **Features**: Timestamps, structured logs, API request/response tracking

**Usage:**
```typescript
import logger from './utils/logger';
logger.info('User logged in', { userId: 1 });
```

### Log Files

When running locally:
```bash
# Backend logs
docker-compose logs api

# View log files (if running locally)
cat logs/app.log
cat logs/error.log
```

### Quick Reference

| Environment | Log Level | Output |
|-------------|-----------|--------|
| Docker | INFO | `docker-compose logs api` |
| Local (DEBUG=True) | DEBUG | Console + `logs/` files |

For detailed documentation, see [LOGGING.md](LOGGING.md).

---

## Trade-offs and Compromises

### 1. Repository Pattern Boilerplate

**Trade-off:** More files and code for better separation.

**Cost:**
- Need to create Repository, Service, and Controller for each entity
- More classes to maintain

**Benefit:**
- Testable business logic
- Clear separation of concerns
- Easy to swap implementations

---

### 2. Async Complexity

**Trade-off:** Async code is more complex than sync.

**Cost:**
- Need `async`/`await` everywhere
- Harder to debug (async stack traces)
- Test fixtures more complex

**Benefit:**
- Better performance under load
- Non-blocking I/O
- Aligns with FastAPI

---

### 3. Eager Loading Memory

**Trade-off:** `joinedload` uses more memory.

**Cost:**
- Loads related data even if not needed
- Larger result sets in memory

**Benefit:**
- Avoids N+1 query problem
- Faster (one query vs many)

**Mitigation:**
- Only load relationships actually used
- Use pagination to limit result sets

---

### 4. Integration Tests > Unit Tests

**Trade-off:** Focused on integration tests over unit tests.

**Cost:**
- Slower test execution
- More complex test setup
- Harder to isolate failures

**Benefit:**
- Test real behavior (DB + business logic)
- Catch integration issues
- More confidence in deployments

---

## What I Prioritized and Why

### 1. Code Quality & Maintainability

**Actions:**
- ✅ Layered architecture
- ✅ Comprehensive documentation (docstrings)
- ✅ Centralized errors, constants, permissions
- ✅ Type hints everywhere
- ✅ Consistent naming conventions

**Why:**
- Long-term maintainability > quick hacks
- Easy for team members to understand
- Reduces bugs through clarity

---

### 2. Testing

**Actions:**
- ✅ 98 integration tests
- ✅ Test fixtures with different scopes
- ✅ Factory and Builder pattern for test data
- ✅ Test database isolation

**Why:**
- Confidence in changes
- Catch regressions early
- Documentation through tests
- Required for production readiness

---

### 3. Developer Experience

**Actions:**
- ✅ Docker Compose for one-command setup
- ✅ Comprehensive README
- ✅ QUICKSTART.md guide
- ✅ Logging for debugging
- ✅ Clear error messages

**Why:**
- Faster onboarding
- Easier development
- Less time troubleshooting

---

### 4. Features

**Implemented:**
- ✅ Task CRUD
- ✅ Comments on tasks
- ✅ Due date notifications
- ✅ Task ownership changes
- ✅ User management

**Why:**
- Covers MVP requirements
- Demonstrates capabilities
- Real-world useful

---

## What I Would Improve With More Time

### 1. Refresh Token Implementation

**Current:** Access tokens expire, but no refresh mechanism.

**Benefits:**
- Better UX (no forced re-login)
- More secure (short-lived access tokens)
- Can revoke refresh tokens

---

### 2. WebSocket for Real-Time Notifications

**Current:** Frontend polls every 30 seconds for notifications.

**Benefits:**
- Instant notifications (no polling delay)
- Reduced server load (no periodic requests)
- Better user experience

---

### 3. Caching Layer (Redis)

**Current:** Every request hits the database.

**Benefits:**
- Faster response times
- Reduced database load
- Scalability

---

### 4. Search and Filtering

**Current:** Can only filter tasks by status.

**Improvement:** 
- Search by title, by owner, etc.
- Filter by due date range, etc.

---

### 5. Email Notifications

**Current:** Only in-app notifications.

---

### 6. Frontend Unit Tests and E2E Tests

**Current:** No frontend unit tests or e2e.

---

### 7. Monitoring and Observability

**Current:** Only logs to files.

**Improvement:**
- **Metrics:** Prometheus metrics
- **Tracing:** OpenTelemetry for distributed tracing
- **Dashboards:** Grafana for visualization
- **Alerting:** Alert on errors, slow requests, high load

---

## Areas for Improvement

### Performance
- [ ] Implement Redis caching for frequently accessed data
- [ ] Add database query optimization and indexing strategy
- [ ] Implement WebSocket for real-time notifications instead of polling

### Features
- [ ] Add file attachments to tasks
- [ ] Implement task templates
- [ ] Add projects to group tasks
- [ ] Add task labels/tags for better organization
- [ ] Implement task dependencies and subtasks
- [ ] Add activity/audit log for task changes
- [ ] Implement email notifications

### Code Quality
- [ ] Add frontend unit tests (Vitest/Jest)
- [ ] Add E2E tests (Playwright/Cypress)

### User Experience
- [ ] Implement drag-and-drop for task reordering
- [ ] Add bulk operations (bulk delete, bulk status update)
- [ ] Implement undo/redo functionality

---

## Known Issues

- [ ] **Token Expiration Handling**: Frontend doesn't handle token expiration gracefully - users aren't notified when their session expires
- [ ] **Notification Polling Performance**: Current polling interval may cause unnecessary API calls - consider implementing WebSocket or Server-Sent Events

---

## Conclusion

This project demonstrates:
- ✅ **Clean Architecture** with layered separation of concerns
- ✅ **SOLID Principles** applied throughout
- ✅ **Production-ready** practices (logging, testing, security)
- ✅ **Modern async Python** with SQLAlchemy 2.0
- ✅ **Type safety** with Pydantic and TypeScript
- ✅ **Comprehensive testing** (98 test cases)
- ✅ **Developer experience** (automated scripts, docs)

**Key Strengths:**
- Maintainable codebase with clear structure
- Well-tested with high confidence
- Secure authentication and authorization
- Good documentation and logging

**Areas for Growth:**
- Frontend testing
- Performance optimization (caching, indexing)
- Real-time features (WebSockets)

---

## Additional Resources

- [SCRIPTS.md](SCRIPTS.md) - Scripts for development and testing (docker-compose, setup-dev.sh, run-tests.sh)
- [LOGGING.md](LOGGING.md) - Detailed logging system documentation
- [tests/README.md](tests/README.md) - Complete testing guide with setup instructions, test patterns, and troubleshooting
- [initial_README.md](initial_README.md) - Original project requirements and specifications
- [Backend API Docs](http://localhost:8000/docs) - Swagger UI (when running)
- [Backend API Docs](http://localhost:8000/redoc) - ReDoc (when running)
