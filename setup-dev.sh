#!/bin/bash
# Setup Local Development Environment
# Usage:
#   ./setup-dev.sh              - Full setup (backend + frontend + db)
#   ./setup-dev.sh backend      - Backend only (venv + deps)
#   ./setup-dev.sh frontend     - Frontend only (npm deps)
#   ./setup-dev.sh env          - Create .env file only
#   ./setup-dev.sh db           - Setup database only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ACTION="${1:-all}"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for Python 3.13+
check_python() {
    local py_version=$(python3 -c 'import sys; print(sys.version_info[1])')
    if [ "$py_version" -lt 13 ]; then
        echo -e "${RED}❌ Error: Python 3.13+ is required!${NC}"
        echo "  Current version: $(python3 --version)"
        echo ""
        echo "  Install uv to get the correct Python version:"
        echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo ""
        echo "  Or install Python 3.13 manually."
        exit 1
    fi
}

install_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${CYAN}📦 Installing uv (Python package manager)...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

setup_backend() {
    echo -e "${CYAN}🐍 Setting up backend...${NC}"
    
    # Use uv if available for better Python management
    if command -v uv &> /dev/null; then
        echo "  Using uv for environment management..."
        if [ -d ".venv" ]; then
            echo "  Virtual environment already exists, skipping..."
        else
            echo "  Creating virtual environment with Python 3.13..."
            uv venv .venv --python 3.13
        fi
        
        echo "  Installing dependencies..."
        uv sync --extra dev
    else
        # Fallback to system Python
        check_python
        
        if [ -d "venv" ]; then
            echo "  Virtual environment already exists, skipping..."
        else
            echo "  Creating virtual environment..."
            python3 -m venv venv
        fi
        
        echo "  Activating virtual environment..."
        source venv/bin/activate
        
        echo "  Upgrading pip..."
        pip install --upgrade pip
        
        echo "  Installing dependencies..."
        pip install -e ".[dev]"
    fi
    
    echo -e "${GREEN}✅ Backend ready!${NC}"
}

setup_frontend() {
    echo -e "${CYAN}⚛️  Setting up frontend...${NC}"
    
    if [ ! -d "frontend" ]; then
        echo -e "${RED}❌ Error: frontend directory not found!${NC}"
        return 1
    fi
    
    cd frontend
    
    if [ -d "node_modules" ]; then
        echo "  node_modules already exists, skipping..."
    else
        echo "  Installing frontend dependencies..."
        npm install
    fi
    
    cd ..
    
    echo -e "${GREEN}✅ Frontend ready!${NC}"
}

setup_env() {
    echo -e "${CYAN}⚙️  Setting up environment file...${NC}"
    
    if [ -f ".env" ]; then
        echo "  .env already exists, skipping..."
    else
        echo "  Creating .env file..."
        cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskmanager

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost", "http://localhost:5173", "http://localhost:8000"]

# Logging
DEBUG=True
EOF
        echo -e "${GREEN}✅ .env file created!${NC}"
    fi
}

setup_database() {
    echo -e "${CYAN}🗄️  Setting up database...${NC}"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker is not running.${NC}"
        echo "  Please start Docker and run: ./setup-dev.sh db"
        return 1
    fi
    
    echo "  Starting PostgreSQL..."
    docker-compose up -d db
    
    echo "  Waiting for database to be ready..."
    sleep 3
    
    echo "  Running migrations..."
    
    # Determine the correct python/pytest command
    if command -v uv &> /dev/null; then
        uv run alembic upgrade head
    elif [ -f ".venv/bin/python" ]; then
        .venv/bin/python -m alembic upgrade head
    elif [ -f "venv/bin/python" ]; then
        source venv/bin/activate
        alembic upgrade head
    else
        echo -e "${RED}❌ Error: No Python environment found!${NC}"
        echo "  Run './setup-dev.sh backend' first."
        exit 1
    fi
    
    echo -e "${GREEN}✅ Database ready!${NC}"
}

# Main
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Local Development Environment Setup    ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

case "$ACTION" in
    backend)
        install_uv
        setup_backend
        ;;
    frontend)
        setup_frontend
        ;;
    env)
        setup_env
        ;;
    db)
        setup_database
        ;;
    all)
        install_uv
        setup_backend
        echo ""
        setup_frontend
        echo ""
        setup_env
        echo ""
        setup_database
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ✅ Setup Complete!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "To start the application:"
        echo ""
        echo "  Backend:"
        if command -v uv &> /dev/null; then
            echo "    source .venv/bin/activate"
            echo "    uvicorn src.main:app --reload"
        else
            echo "    source venv/bin/activate"
            echo "    uvicorn src.main:app --reload"
        fi
        echo ""
        echo "  Frontend (new terminal):"
        echo "    cd frontend"
        echo "    npm run dev"
        echo ""
        echo "To stop the database:"
        echo "  docker-compose down"
        ;;
    *)
        echo -e "${YELLOW}Usage: $0 [backend|frontend|env|db|all]${NC}"
        echo "  backend   - Setup backend only (venv + dependencies)"
        echo "  frontend  - Setup frontend only (npm dependencies)"
        echo "  env      - Create .env file"
        echo "  db       - Setup database (requires Docker)"
        echo "  all      - Full setup (default)"
        exit 1
        ;;
esac
