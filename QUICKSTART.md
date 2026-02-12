# Task Manager - Quick Start

Bring the entire application up with a single command.

## Prerequisites

Before you start, make sure you have installed:

- Docker Desktop (installed and running)
- Node.js and npm (v18 or higher)
- Python 3.13+ and uv (package manager)

### Install uv (if you do not have it)

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Quick Start With ONE COMMAND

> **Note:** Bash scripts are not tested and may not work correctly in this version.

### Windows (PowerShell)

```powershell
.\start.ps1
```

### Linux/macOS (Bash)

```bash
# Give execute permissions (only the first time)
chmod +x start.sh

# Start
./start.sh
```

That's it. The script automatically:

1. Verifies Docker is running
2. Starts the PostgreSQL database
3. Waits for the database to be ready
4. Installs backend dependencies
5. Starts the backend server
6. Installs frontend dependencies
7. Starts the frontend server

---

## Access the Application

> **Note:** The app is not deployed at the moment and is currently offline. Use the local URLs below after starting the services.

Once started, the services will be available at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React user interface |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Database | localhost:5432 | PostgreSQL |

### Default credentials

**Owner user:**
- Email: `admin@admin.com`
- Password: `admin123`

**Member user:**
- Email: `john.doe@example.com`
- Password: `password123`

---

## Stop the Application

### Option 1: Stop only Frontend and Backend

Press `Ctrl+C` in the terminal where you ran the start script.

> **Note:** The database will keep running in Docker.

### Option 2: Stop EVERYTHING (including the database)

**Windows:**
```powershell
.\stop.ps1
```

**Linux/macOS:**
```bash
./stop.sh
```

---

## Manual Commands (Alternative)

If you prefer to start the services manually:

### 1. Database
```bash
docker-compose up -d db
```

### 2. Backend
```bash
uv sync                                    # Install dependencies
uv run uvicorn src.main:app --reload      # Start server
```

### 3. Frontend
```bash
cd frontend
npm install                                # Install dependencies
npm run dev                                # Start server
```

---

## Troubleshooting

### "Docker is not running"

**Problem:** The script cannot connect to Docker.

**Solution:**
1. Open Docker Desktop
2. Wait for the Docker icon in the taskbar to turn green
3. Run the script again

---

### Port already in use

**Problem:** Error indicating a port (5432, 8000, 5173) is already in use.

**Windows solution:**
```powershell
# See which process uses the port
netstat -ano | findstr :8000

# Kill the process (replace <PID> with the number shown)
taskkill /PID <PID> /F
```

**Linux/macOS solution:**
```bash
# See which process uses the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

---

### "uv: command not found"

**Problem:** uv is not installed or not in PATH.

**Solution:**
```powershell
# Windows (PowerShell as Administrator)
irm https://astral.sh/uv/install.ps1 | iex
```

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart the terminal.

---

### Database does not connect

**Problem:** The backend cannot connect to PostgreSQL.

**Solution:**
```bash
# View database logs
docker-compose logs db

# Restart the database
docker-compose restart db

# Or stop and start again
docker-compose down
docker-compose up -d db
```

---

### npm dependency errors

**Problem:** The frontend does not install dependencies correctly.

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## View Logs

### Backend
Backend logs show in the terminal.

**Linux/macOS:** They are also saved in `backend.log`

### Frontend
Vite logs show in the terminal.

### Database
```bash
docker-compose logs db
docker-compose logs -f db    # Follow logs in real time
```

---

## Restart an Individual Service

### Only the database
```bash
docker-compose restart db
```

### Only the backend
```bash
# Stop (find PID and kill the process)
# Windows: Ctrl+C or Task Manager
# Linux/macOS:
pkill -f uvicorn

# Start
uv run uvicorn src.main:app --reload
```

### Only the frontend
```bash
cd frontend
npm run dev
```

---

## Additional Documentation

- [README_SCRIPTS.md](README_SCRIPTS.md) - Detailed script documentation
- [initial_README.md](initial_README.md) - Full project documentation
- API Docs: http://localhost:8000/docs (when the backend is running)

---

## Tips

- Code changes reload automatically (hot reload)
- The backend has Swagger UI at http://localhost:8000/docs
- You can inspect the database with any PostgreSQL client:
  - Host: `localhost`
  - Port: `5432`
  - User: `taskuser`
  - Password: `taskpass`
  - Database: `taskmanager`
