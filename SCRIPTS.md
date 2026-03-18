# Scripts Documentation

This document describes the shell scripts available for development and testing.

## Table of Contents

- [Overview](#overview)
- [Docker Scripts](#docker-scripts)
- [Development Scripts](#development-scripts)
- [Test Scripts](#test-scripts)
- [Usage Examples](#usage-examples)

---

## Overview

The project provides several scripts to automate common development tasks:

| Script | Purpose |
|--------|---------|
| `docker-compose.yml` | Container orchestration (all-in-one) |
| `setup-dev.sh` | Local development environment setup |
| `run-tests.sh` | Test database setup and test execution |

---

## Docker Scripts

### Docker Compose

The main way to run the entire application stack.

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

**What it starts:**
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 80

**Features:**
- Automatic migrations on startup
- Automatic database seeding with sample data
- Health checks for the database

---

## Development Scripts

### setup-dev.sh

Sets up a complete local development environment (backend + frontend + database).

```bash
./setup-dev.sh              # Full setup (all components)
./setup-dev.sh backend      # Backend only
./setup-dev.sh frontend     # Frontend only
./setup-dev.sh env          # Create .env file only
./setup-dev.sh db           # Database setup only
```

#### Full Setup

```bash
./setup-dev.sh
```

This will:

1. **Install uv** (if not present)
   - Downloads and installs the `uv` Python package manager
   - Manages Python 3.13 automatically

2. **Setup Backend**
   - Creates `.venv` virtual environment
   - Installs all Python dependencies
   - Includes dev dependencies (pytest, etc.)

3. **Setup Frontend**
   - Runs `npm install` in the `frontend/` directory
   - Installs all Node.js dependencies

4. **Create .env file**
   - Database connection string
   - Security settings (SECRET_KEY)
   - CORS configuration
   - Debug settings

5. **Setup Database**
   - Starts PostgreSQL via Docker
   - Runs Alembic migrations
   - Creates schema

#### After Setup

Start the application:

```bash
# Terminal 1: Backend
source .venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

#### Cleanup

To remove the virtual environment and start fresh:

```bash
rm -rf .venv
./setup-dev.sh
```

---

## Test Scripts

### run-tests.sh

Runs the test suite with database setup automation.

```bash
./run-tests.sh setup       # Setup test database only
./run-tests.sh setup-test  # Setup database + run tests
./run-tests.sh test        # Run tests only
```

#### Prerequisites

- Docker running (for database)
- Test database created in PostgreSQL

#### First Time Setup

```bash
./run-tests.sh setup-test
```

This will:
1. Create `taskmanager_test` database (if not exists)
2. Grant permissions
3. Run all 98 tests with coverage

#### Subsequent Runs

```bash
# Run tests only (faster, assumes database exists)
./run-tests.sh test

# Setup + test
./run-tests.sh setup-test
```

#### Test Options

```bash
# Run specific test file
uv run pytest tests/test_tasks.py

# Run specific test class
uv run pytest tests/test_tasks.py::TestCreateTask

# Run tests matching pattern
uv run pytest -k "task"

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

---

## Usage Examples

### Scenario 1: New Developer

```bash
# Clone and setup everything
git clone <repo>
cd task-manager-api
./setup-dev.sh

# Start the app
source .venv/bin/activate
uvicorn src.main:app --reload

# In another terminal
cd frontend && npm run dev

# Visit http://localhost
```

### Scenario 2: Running Tests

```bash
# First time (creates test database)
./run-tests.sh setup-test

# Subsequent test runs
./run-tests.sh test

# After schema changes
./run-tests.sh setup-test
```

### Scenario 3: Docker Development

```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View backend logs
docker-compose logs api

# View frontend logs
docker-compose logs frontend

# Stop
docker-compose down
```

### Scenario 4: Backend Only Development

```bash
# Use Docker for database
docker-compose up -d db

# Setup backend only
./setup-dev.sh backend

# Start backend
source .venv/bin/activate
uvicorn src.main:app --reload
```

---

## Troubleshooting

### setup-dev.sh fails

```bash
# Check Docker is running
docker info

# Clean up and retry
rm -rf .venv
./setup-dev.sh backend
```

### run-tests.sh fails

```bash
# Ensure test database exists
docker exec taskmanager_db psql -U taskuser -d postgres -c "CREATE DATABASE taskmanager_test;"

# Retry
./run-tests.sh setup-test
```

### Port already in use

```bash
# Check what's using the port
lsof -i :5432  # Database
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Kill the process
kill -9 <PID>
```
