# Task Manager API

A full-stack task management application built with FastAPI and React, featuring role-based access control, real-time notifications, and comprehensive task collaboration tools.

[![CircleCI](https://circleci.com/gh/YOUR_USERNAME/task-manager-api.svg?style=svg)](https://circleci.com/gh/YOUR_USERNAME/task-manager-api)
[![Coverage Status](https://coveralls.io/repos/github/YOUR_USERNAME/task-manager-api/badge.svg?branch=main)](https://coveralls.io/github/YOUR_USERNAME/task-manager-api?branch=main)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?style=flat&logo=React&logoColor=white)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-3178C6.svg?style=flat&logo=TypeScript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat&logo=PostgreSQL&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Areas for Improvement](#areas-for-improvement)
- [Known Issues](#known-issues)
- [Contributing](#contributing)
- [License](#license)

## Overview

Task Manager API is a modern, full-stack application designed for efficient task management and team collaboration. It provides a robust RESTful API built with FastAPI and a responsive React frontend, featuring role-based access control (RBAC), real-time notifications, task commenting, and comprehensive task lifecycle management.

The application supports two user roles:
- **OWNER**: Full administrative access to all tasks and users
- **MEMBER**: Access to personal tasks and limited permissions

## Features

### Core Functionality
- ✅ **Task Management**: Create, read, update, and delete tasks with status tracking
- ✅ **Role-Based Access Control (RBAC)**: Owner and Member roles with granular permissions
- ✅ **User Authentication**: JWT-based authentication with secure token handling
- ✅ **Task Comments**: Collaborative commenting system on tasks
- ✅ **Smart Notifications**: Automated due date notifications (overdue, due today, due soon)
- ✅ **Task Assignment**: Owners can reassign tasks to other users
- ✅ **Due Date Management**: Set and track task deadlines with visual indicators

### Technical Features
- 🔒 **Security**: Argon2 password hashing, JWT tokens, CORS protection
- 📊 **Comprehensive Logging**: Backend and frontend logging with file rotation
- 🧪 **Test Coverage**: 98 test cases with pytest
- 🚀 **CI/CD Pipeline**: Automated testing and coverage reporting with CircleCI
- 📱 **Responsive UI**: Mobile-friendly React interface
- 🔄 **Real-time Updates**: Automatic notification polling
- 📄 **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- 🐳 **Docker Support**: Containerized deployment with Docker Compose

## Tech Stack

### Backend
- **Framework**: FastAPI 0.115.6
- **Language**: Python 3.13
- **Database**: PostgreSQL 16 with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT with python-jose
- **Password Hashing**: Argon2
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Package Manager**: uv

### Frontend
- **Framework**: React 18.3.1
- **Language**: TypeScript 5.6.2
- **Build Tool**: Vite 6.0.3
- **HTTP Client**: Axios
- **Styling**: CSS3 with modern layouts

### DevOps & Tools
- **CI/CD**: CircleCI
- **Code Coverage**: Coveralls
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git
- **API Testing**: Swagger UI

## Documentation

Additional documentation is available in the following files:

- **[initial_README.md](initial_README.md)** - Original project requirements and specifications
- **[LOGGING.md](LOGGING.md)** - Comprehensive logging system documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide for getting up and running
- **[README_SCRIPTS.md](README_SCRIPTS.md)** - Available scripts and commands reference
- **Backend API Docs** - Available at `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs** - Available at `http://localhost:8000/redoc` (ReDoc)

## Prerequisites

Before running this application, ensure you have the following installed:

### Required
- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 16+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **uv** - Python package manager ([Installation](https://github.com/astral-sh/uv))

### Optional
- **Docker & Docker Compose** - For containerized deployment
- **Git** - For version control

### Installing uv

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/task-manager-api.git
cd task-manager-api
```

### 2. Backend Setup

#### Create PostgreSQL Database

```bash
# Access PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE taskmanager;
CREATE USER taskuser WITH PASSWORD 'taskpass';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskuser;
\q
```

#### Install Backend Dependencies

```bash
# Install dependencies with uv
uv sync
```

#### Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskmanager

# Security
SECRET_KEY=your-secret-key-here-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Logging
DEBUG=True
```

#### Run Database Migrations

```bash
# Run migrations
uv run alembic upgrade head
```

#### (Optional) Seed Initial Data

```bash
# Seed the database with sample data
uv run python -m src.seed_data
```

This creates:
- **Owner Users**: 
    - `admin@admin.com` / `admin123`
    - `bob.wilson@example.com` / `password123`
- **Member Users**: 
    - `john.doe@example.com` / `password123`
    - `jane.smith@example.com` / `password123`
    - `alice.johnson@example.com` / `password123`
- Sample tasks and notifications

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Quick Start

For a simplified one-command setup, see **[QUICKSTART.md](QUICKSTART.md)**, which provides automated scripts to start the entire application stack on Windows, Linux, or macOS.

### Conventional Setup

If you prefer to start services manually or need more control over the process, follow these conventional methods:

#### Prerequisites

Ensure you have completed the [Installation](#installation) steps before proceeding.

#### Option 1: Run Backend and Frontend Separately

**1. Start the Database**

```bash
# Start PostgreSQL using Docker Compose
docker-compose up -d db

# Verify it's running
docker-compose ps
```

**2. Start Backend Server**

```bash
# From project root
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**3. Start Frontend Development Server**

Open a new terminal window:

```bash
# From frontend directory
cd frontend
npm run dev
```

The frontend will be available at:
- **App**: http://localhost:5173

#### Option 2: Run with Docker Compose (Database + Backend)

**1. Start Database and Backend**

```bash
# Build and start database and backend services
docker-compose up -d

# View logs
docker-compose logs -f
```

**2. Start Frontend Development Server**

Open a new terminal window:

```bash
# From frontend directory
cd frontend
npm run dev
```

**3. Stop Services**

```bash
# Stop backend and database
docker-compose down
```

Services:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **PostgreSQL**: localhost:5432

## Running Tests

### Backend Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_tasks.py

# Run specific test class
uv run pytest tests/test_tasks.py::TestCreateTask

# View coverage report
open htmlcov/index.html  # macOS
# or
start htmlcov/index.html  # Windows
```

### Frontend Tests

```bash
cd frontend
npm run test
```

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

## API Documentation

### Authentication

All endpoints (except `/login/access-token`) require JWT authentication.

**Login:**
```bash
POST /api/v1/login/access-token
Content-Type: application/x-www-form-urlencoded

username=owner@example.com&password=ownerpass123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Use Token:**
```bash
Authorization: Bearer <access_token>
```

### Key Endpoints

#### Tasks
- `GET /api/v1/tasks` - List user's tasks
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{task_id}` - Get task details
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- `PATCH /api/v1/tasks/{task_id}/owner` - Change task owner (OWNER only)

#### Comments
- `GET /api/v1/tasks/{task_id}/comments` - Get task comments
- `POST /api/v1/tasks/{task_id}/comments` - Create comment
- `PUT /api/v1/comments/{comment_id}` - Update comment
- `DELETE /api/v1/comments/{comment_id}` - Delete comment

#### Notifications
- `GET /api/v1/notifications` - Get notifications
- `GET /api/v1/notifications/unread/count` - Count unread notifications
- `PATCH /api/v1/notifications/{notification_id}/read` - Mark as read
- `DELETE /api/v1/notifications/{notification_id}` - Delete notification
- `POST /api/v1/notifications/check-due-dates` - Generate due date notifications (OWNER only)

#### Users
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users` - List users (OWNER sees all, MEMBER sees self)
- `POST /api/v1/users` - Create user (OWNER only)

For complete API documentation, visit http://localhost:8000/docs when running the application.

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

## Known Issues

- [ ] **Token Expiration Handling**: Frontend doesn't handle token expiration gracefully - users aren't notified when their session expires
- [ ] **Notification Polling Performance**: Current polling interval may cause unnecessary API calls - consider implementing WebSocket or Server-Sent Events

## Followed Development Guidelines 
- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Keep commits atomic and well-described