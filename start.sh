#!/bin/bash

# Task Manager - Script de inicio para Unix/Linux/macOS
# Este script levanta toda la aplicación con un solo comando

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Task Manager - Iniciando servicios${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# Verificar que Docker esté corriendo
echo -e "${YELLOW}[1/6] Verificando Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker no está corriendo. Por favor inicia Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker está corriendo${NC}"
echo ""

# Iniciar la base de datos con docker-compose
echo -e "${YELLOW}[2/6] Iniciando base de datos PostgreSQL...${NC}"
docker-compose up -d db
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudo iniciar la base de datos${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Base de datos iniciada${NC}"
echo ""

# Esperar a que la base de datos esté lista
echo -e "${YELLOW}[3/6] Esperando a que la base de datos esté lista...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    if docker-compose exec -T db pg_isready -U taskuser -d taskmanager > /dev/null 2>&1; then
        break
    fi
    echo "  Intento $attempt/$max_attempts - Esperando..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}ERROR: La base de datos no respondió a tiempo${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Base de datos lista${NC}"
echo ""

# Instalar dependencias del backend con uv
echo -e "${YELLOW}[4/6] Instalando dependencias del backend...${NC}"
uv sync
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudieron instalar las dependencias del backend${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencias del backend instaladas${NC}"
echo ""

# Iniciar el backend en segundo plano
echo -e "${YELLOW}[5/6] Iniciando servidor backend...${NC}"
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend iniciado (PID: $BACKEND_PID)${NC}"
sleep 3
echo ""

# Instalar dependencias del frontend
echo -e "${YELLOW}[6/6] Instalando dependencias del frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: No se pudieron instalar las dependencias del frontend${NC}"
        kill $BACKEND_PID
        exit 1
    fi
fi
echo -e "${GREEN}✓ Dependencias del frontend instaladas${NC}"
echo ""

echo -e "${CYAN}=====================================${NC}"
echo -e "${GREEN}  ✓ Todos los servicios iniciados${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""
echo -e "Servicios disponibles:"
echo -e "  - Base de datos: localhost:5432"
echo -e "  - API Backend:   http://localhost:8000"
echo -e "  - API Docs:      http://localhost:8000/docs"
echo -e "  - Frontend:      (iniciando...)"
echo ""
echo -e "${YELLOW}Para detener los servicios, presiona Ctrl+C${NC}"
echo ""

# Función para cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}Deteniendo servicios...${NC}"
    kill $BACKEND_PID 2>/dev/null
    cd ..
    echo -e "${YELLOW}Para detener la base de datos, ejecuta: docker-compose down${NC}"
    exit 0
}

# Registrar cleanup en señales de terminación
trap cleanup SIGINT SIGTERM

# Iniciar el frontend (esto bloqueará la terminal)
echo -e "${YELLOW}Iniciando frontend...${NC}"
npm run dev

# Si npm run dev termina, ejecutar cleanup
cleanup
