# SOLUTIONS.md - Task Manager API

## Table of Contents

- [Architectural Decisions](#architectural-decisions)
- [Design Patterns](#design-patterns)
- [SOLID Principles Application](#solid-principles-application)
- [Security Decisions](#security-decisions)
- [Database Design](#database-design)
- [Trade-offs and Compromises](#trade-offs-and-compromises)
- [What I Prioritized and Why](#what-i-prioritized-and-why)
- [What I Would Improve With More Time](#what-i-would-improve-with-more-time)
- [How to Run and Test](#how-to-run-and-test)

---

## Architectural Decisions

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

### 3. Factory and Builder Pattern (Tests)

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

**Alternative considered:** bcrypt

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

**Improvementes to make:**
- Implement refresh tokens

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

**All queries use SQLAlchemy's safe query building.**

---

### 5. CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production TODO:**
- Use environment variable for allowed origins
- Restrict to production domains
- Consider more restrictive methods/headers

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

**Why:**
- **Data Integrity**: No orphaned records
- **User Privacy**: Complete data removal on user deletion
- **Simplicity**: Don't need manual cleanup code

---

### 3. Eager Loading

**Decision:** Use `joinedload` to prevent N+1 query problems.

**Applied in:**
- Task queries (load owner relationship)
- Comment queries (load author relationship)
- Notification queries (load task and user relationships)

---

### 4. Indexes

**Decision:** Add indexes on frequently queried columns.

```python
email = Column(String, unique=True, index=True)  # For login queries
id = Column(Integer, primary_key=True, index=True)  # Automatic
```

**Missing indexes**:
- `task.owner_id` (for user's tasks queries)
- `task.status` (for status filtering)
- `notification.user_id, is_read` (composite for unread notifications)

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
- ✅ 95 integration tests
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
- ✅ Automated startup scripts (start.ps1, start.sh)
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

### High Priority

#### 1. Refresh Token Implementation

**Current:** Access tokens expire, but no refresh mechanism.

**Improvement:**
```python
# Add refresh token to response
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}

# New endpoint
@router.post("/refresh")
async def refresh_access_token(refresh_token: str):
    # Validate refresh token
    # Issue new access token
```

**Benefits:**
- Better UX (no forced re-login)
- More secure (short-lived access tokens)
- Can revoke refresh tokens

---

#### 2. WebSocket for Real-Time Notifications

**Current:** Frontend polls every 30 seconds for notifications.

**Benefits:**
- Instant notifications (no polling delay)
- Reduced server load (no periodic requests)
- Better user experience

---

### Medium Priority

#### 3. Caching Layer (Redis)

**Current:** Every request hits the database.

**Benefits:**
- Faster response times
- Reduced database load
- Scalability

---

#### 4. Search and Filtering

**Current:** Can only filter tasks by status.

**Improvement:** 
- Search by title, by owner, etc.
- Filter by due date range, etc.

---

#### 5. Email Notifications

**Current:** Only in-app notifications.

---

#### 6. Frontend Unit Tests and e2e Tests

**Current:** No frontend unit tests or e2e.

---

#### 7. Monitoring and Observability

**Current:** Only logs to files.

**Improvement:**
- **Metrics:** Prometheus metrics
- **Tracing:** OpenTelemetry for distributed tracing
- **Dashboards:** Grafana for visualization
- **Alerting:** Alert on errors, slow requests, high load

---

### Lower Priority

#### 8. Task Templates

**Feature:** Save tasks as templates for reuse.

---

#### 9. Task Dependencies

**Feature:** Tasks can depend on other tasks.

---

#### 10. Audit Log

**Feature:** Track all changes to tasks.

---

## How to Run and Test

### Quick Start

For the fastest way to get the application running, see **[QUICKSTART.md](QUICKSTART.md)**.

The quick start guide provides:
- ✅ One-command automated setup for Windows, Linux, and macOS
- ✅ Automated dependency installation
- ✅ Database initialization
- ✅ Service startup (database, backend, frontend)
- ✅ Troubleshooting common issues

**Windows:**
```powershell
.\start.ps1
```

**Linux/macOS:**
```bash
./start.sh
```

---

### Detailed Setup Instructions

For complete installation instructions, manual setup, and configuration options, see **[README.md](README.md#installation)**.

The README provides:
- Prerequisites and system requirements
- Step-by-step installation guide
- Environment configuration
- Database setup and migrations
- Running services individually or with Docker Compose

---

### Running Tests

#### Backend Tests

```bash
# Run all tests
uv run --extra dev pytest

# Run with coverage report
uv run --extra dev pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
uv run --extra dev pytest tests/test_tasks.py

# Run specific test class
uv run --extra dev pytest tests/test_tasks.py::TestCreateTask

# View HTML coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

**Test Organization:**
- **Integration tests**: 95 test cases covering full request → database → response flow
- **Test fixtures**: Different scopes (session, function) for optimal performance
- **Factory pattern**: Reusable test data creation
- **Database isolation**: Each test gets a clean database state

**Coverage:** Tests cover authentication, RBAC, task CRUD, comments, notifications, and user management.

#### Frontend Tests

```bash
cd frontend
npm run test
```

**Note:** Frontend tests not yet implemented. See [improvement section](#6-frontend-unit-tests-and-e2e-tests).

---

### Accessing the Application

Once running, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React UI |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Alternative API documentation |
| **Database** | localhost:5432 | PostgreSQL |

**Default Credentials:**
- Owner: `admin@admin.com` / `admin123`
- Member: `john.doe@example.com` / `password123`

---

### Project Structure

For a complete overview of the project structure, see **[README.md](README.md#project-structure)**.

**Key directories:**
```
task-manager-api/
├── src/                    # Backend source (layered architecture)
│   ├── api/v1/endpoints/  # API route handlers
│   ├── core/              # Config, security, permissions, errors
│   ├── models/            # SQLAlchemy ORM models
│   ├── repositories/      # Data access layer
│   ├── schemas/           # Pydantic validation schemas
│   └── services/          # Business logic layer
├── frontend/src/          # Frontend source
│   ├── components/        # React components
│   ├── services/          # API service layer
│   └── types/             # TypeScript types
├── tests/                 # Backend test suite
└── alembic/              # Database migrations
```

---

### Debugging Tips

**Backend:**
1. Enable SQL query logging by setting `echo=True` in [src/db/session.py](src/db/session.py)
2. Check application logs in `logs/app.log` and `logs/error.log`
3. Use `import pdb; pdb.set_trace()` for interactive debugging

**Frontend:**
1. Open browser DevTools (F12)
2. Check Console for errors and Network tab for API calls
3. Use React DevTools extension for component inspection

**Database:**
```bash
# Connect to PostgreSQL
docker exec -it taskmanager_db psql -U taskuser -d taskmanager

# List tables
\dt

# Query data
SELECT * FROM users;
SELECT * FROM tasks;
```

---

### Common Issues

See **[QUICKSTART.md](QUICKSTART.md#solución-de-problemas)** for detailed troubleshooting:
- Docker not running
- Ports already in use
- Database connection errors
- Dependency installation issues

---

## Conclusion

This project demonstrates:
- ✅ **Clean Architecture** with layered separation of concerns
- ✅ **SOLID Principles** applied throughout
- ✅ **Production-ready** practices (logging, testing, security)
- ✅ **Modern async Python** with SQLAlchemy 2.0
- ✅ **Type safety** with Pydantic and TypeScript
- ✅ **Comprehensive testing** (95 test cases)
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