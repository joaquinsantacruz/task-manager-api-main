# Quick Start Scripts

This project includes scripts to make it easy to start and stop all services with a single command.

## Prerequisites

- Docker Desktop installed and running
- Node.js and npm installed
- Python 3.13+ and uv installed

## Quick Start

> **Note:** Bash scripts are not tested and may not work correctly in this version.

### Windows (PowerShell)

```powershell
# Start all services
.\start.ps1

# Stop all services (in another terminal)
.\stop.ps1
```

### Linux/macOS (Bash)

```bash
# Give execute permissions (only the first time)
chmod +x start.sh stop.sh

# Start all services
./start.sh

# Stop all services (in another terminal)
./stop.sh
```

## What does the start script do?

The `start.ps1` / `start.sh` script automates the following steps:

1. **Check Docker**: Confirms Docker is running
2. **Start the database**: Brings up PostgreSQL with `docker-compose up -d db`
3. **Wait for the database**: Verifies PostgreSQL is ready to accept connections
4. **Install backend dependencies**: Runs `uv sync`
5. **Start the backend**: Runs `uv run uvicorn src.main:app --reload` in the background
6. **Install frontend dependencies**: Runs `npm install` if needed
7. **Start the frontend**: Runs `npm run dev`

## Available Services

> **Note:** The app is not deployed at the moment and is currently offline. Use the local URLs below after starting the services.

Once started, the services will be available at:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL database: localhost:5432

## Stop the Services

### Option 1: Ctrl+C
Press `Ctrl+C` in the terminal where the start script is running. This will stop the frontend and backend, but the database will keep running.

### Option 2: Stop script
Run `stop.ps1` (Windows) or `stop.sh` (Linux/macOS) in another terminal to stop all services including the database.

```powershell
# Windows
.\stop.ps1
```

```bash
# Linux/macOS
./stop.sh
```

## Troubleshooting

### Docker is not running
```
ERROR: Docker is not running. Please start Docker Desktop.
```
**Solution**: Start Docker Desktop and wait until it is fully loaded before running the script.

### Port already in use
If any port (5432, 8000, 5173) is in use:

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### uv issues
If `uv` is not installed:

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### npm issues
If frontend dependencies do not install correctly:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Logs

- Backend logs: Shown in the terminal or in `backend.log` (Linux/macOS)
- Frontend logs: Shown in the terminal
- Database logs: `docker-compose logs db`

## Restart an Individual Service

### Only the database
```bash
docker-compose restart db
```

### Only the backend
```bash
# Stop
pkill -f uvicorn  # Linux/macOS
# Or find the process on Windows and kill it

# Start
uv run uvicorn src.main:app --reload
```

### Only the frontend
```bash
cd frontend
npm run dev
```
