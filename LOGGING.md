# Logging System Documentation

This document describes the logging system implemented in the Task Manager API project.

## Overview

The project uses a comprehensive logging system for both backend (Python/FastAPI) and frontend (TypeScript/React) to help with debugging, monitoring, and auditing.

## Backend Logging (Python)

### Configuration

The backend uses Python's built-in `logging` module with custom configuration located in `src/core/logger.py`.

#### Features

- **Console Output**: Logs are printed to the console for real-time monitoring
- **File Rotation**: Logs are saved to files with automatic rotation
  - Main log file: `logs/app.log` (max 10MB, 5 backup files)
  - Error log file: `logs/error.log` (max 10MB, 5 backup files)
- **Log Levels**: DEBUG mode in development, INFO in production
- **Structured Format**: `[timestamp] - [logger_name] - [level] - [message]`

#### Usage

```python
from src.core.logger import get_logger

logger = get_logger(__name__)

# Different log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include stack trace
```

### Log Locations

All backend logs are stored in the `logs/` directory:
- `logs/app.log`: All logs (INFO and above)
- `logs/error.log`: Error logs only (ERROR and above)

### What We Log

#### Authentication (`src/api/v1/endpoints/login.py`)
- Login attempts (username)
- Failed login attempts
- Inactive user login attempts
- Successful logins

#### Task Operations (`src/services/task.py`)
- Task creation/update/deletion
- Permission violations
- Task owner changes
- Task retrieval

#### User Operations (`src/services/user.py`)
- User creation
- Duplicate email attempts
- User listing operations

#### Notification Operations (`src/services/notification.py`)
- Notification fetching
- Mark as read operations
- Notification deletion

#### Comment Operations (`src/services/comment.py`)
- Comment creation on tasks
- Comment updates
- Comment deletion

## Frontend Logging (TypeScript)

### Configuration

The frontend uses a custom Logger class located in `frontend/src/utils/logger.ts`.

#### Features

- **Log Levels**: DEBUG, INFO, WARN, ERROR
- **Timestamps**: All logs include timestamps
- **Environment Aware**: Full logging in development, can be disabled in production
- **Structured Format**: Organized log entries with metadata

#### Usage

```typescript
import logger from './utils/logger';

// Different log levels
logger.debug('Debugging info', { details: 'value' });
logger.info('Information message');
logger.warn('Warning message');
logger.error('Error occurred', errorObject);

// Special helpers for API calls
logger.logRequest('GET', '/api/tasks', requestData);
logger.logResponse('GET', '/api/tasks', 200);

// User actions
logger.logUserAction('task_created', { taskId: 123 });
```

### What We Log

#### API Calls (`frontend/src/api/axios.ts`)
- All outgoing HTTP requests (method, URL, data)
- All HTTP responses (method, URL, status code)
- Network errors
- Authentication errors

#### Authentication (`frontend/src/context/AuthContext.tsx`)
- Login attempts
- Login success/failure
- User data fetching
- Logout actions
- Token restoration from localStorage

#### User Actions
Track important user interactions:
- Login/logout
- Task operations
- Comment creation
- Notification actions

## Log Output Examples

### Backend Example

```
2024-01-15 10:30:45 - src.api.v1.endpoints.login - INFO - Login attempt for email: user@example.com
2024-01-15 10:30:45 - src.api.v1.endpoints.login - INFO - Successful login for user 1 (user@example.com)
2024-01-15 10:30:50 - src.services.task - INFO - User 1 (user@example.com) creating task: Complete documentation
2024-01-15 10:30:50 - src.services.task - INFO - Task 42 created successfully by user 1
```

### Frontend Example (Browser Console)

```
[2024-01-15 10:30:45] INFO: Login successful for user: user@example.com
[2024-01-15 10:30:45] INFO: User data fetched: user@example.com (Role: MEMBER)
[2024-01-15 10:30:45] DEBUG: API Request: POST /login/access-token
[2024-01-15 10:30:45] DEBUG: API Response: POST /login/access-token - Status: 200
```

## Configuration

### Backend

Logging behavior can be controlled via environment variables in `.env`:

```env
DEBUG=True  # Enable DEBUG level logging
```

### Frontend

The logger is always enabled in development mode. To disable in production:

```typescript
import logger from './utils/logger';

logger.setEnabled(false);
```

## Best Practices

1. **Use Appropriate Log Levels**:
   - `DEBUG`: Detailed information for debugging
   - `INFO`: General information about application flow
   - `WARN`: Warning messages for unusual but valid conditions
   - `ERROR`: Error conditions with stack traces

2. **Include Context**:
   - Always include relevant IDs (user_id, task_id, etc.)
   - Include operation details
   - Add error information when applicable

3. **Protect Sensitive Data**:
   - Never log passwords
   - Be careful with tokens
   - Sanitize user input before logging

4. **Performance**:
   - Use DEBUG level for verbose logging
   - Avoid logging in tight loops
   - Use log rotation to prevent disk space issues

## Maintenance

### Log Rotation

Backend logs automatically rotate when they reach 10MB, keeping 5 backup files. Old backups are automatically deleted.

### Log Cleanup

The `logs/` directory is excluded from version control via `.gitignore`. To manually clean logs:

```bash
# Backend logs
rm -rf logs/*.log*

# The directory will be recreated automatically on next run
```

## Troubleshooting

### Backend Logs Not Appearing

1. Check that the `logs/` directory exists and is writable
2. Verify `DEBUG` setting in environment variables
3. Check console output for configuration errors

### Frontend Logs Not Appearing

1. Open browser developer console
2. Check that logger is enabled: `logger.setEnabled(true)`
3. Verify you're in development mode

### Too Many Logs

1. Adjust log level (use INFO instead of DEBUG in production)
2. Disable specific loggers if needed
3. Increase rotation file size if needed
