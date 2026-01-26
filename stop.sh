#!/bin/bash

# Task Manager - Script de detención para Unix/Linux/macOS
# Este script detiene todos los servicios

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Task Manager - Deteniendo servicios${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# Detener contenedores de Docker
echo -e "${YELLOW}Deteniendo contenedores Docker...${NC}"
docker-compose down
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Contenedores Docker detenidos${NC}"
else
    echo -e "${YELLOW}! No se pudieron detener algunos contenedores${NC}"
fi
echo ""

# Detener procesos de uvicorn (backend)
echo -e "${YELLOW}Deteniendo servidor backend...${NC}"
pkill -f "uvicorn src.main:app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Servidor backend detenido${NC}"
else
    echo -e "${GRAY}- No se encontraron procesos backend activos${NC}"
fi
echo ""

# Detener procesos de Vite (frontend)
echo -e "${YELLOW}Deteniendo servidor frontend...${NC}"
pkill -f "vite" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Servidor frontend detenido${NC}"
else
    echo -e "${GRAY}- No se encontraron procesos frontend activos${NC}"
fi
echo ""

echo -e "${CYAN}=====================================${NC}"
echo -e "${GREEN}  ✓ Servicios detenidos${NC}"
echo -e "${CYAN}=====================================${NC}"
