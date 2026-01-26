# Scripts de Inicio Rápido

Este proyecto incluye scripts para facilitar el inicio y detención de todos los servicios con un solo comando.

## 📋 Requisitos Previos

- Docker Desktop instalado y en ejecución
- Node.js y npm instalados
- Python 3.13+ y uv instalados

## 🚀 Inicio Rápido

### Windows (PowerShell)

```powershell
# Iniciar todos los servicios
.\start.ps1

# Detener todos los servicios (en otra terminal)
.\stop.ps1
```

### Linux/macOS (Bash)

```bash
# Dar permisos de ejecución (solo la primera vez)
chmod +x start.sh stop.sh

# Iniciar todos los servicios
./start.sh

# Detener todos los servicios (en otra terminal)
./stop.sh
```

## 🔧 ¿Qué hace el script de inicio?

El script `start.ps1` / `start.sh` automatiza los siguientes pasos:

1. **Verifica Docker**: Confirma que Docker esté corriendo
2. **Inicia la base de datos**: Levanta PostgreSQL con `docker-compose up -d db`
3. **Espera la base de datos**: Verifica que PostgreSQL esté listo para aceptar conexiones
4. **Instala dependencias del backend**: Ejecuta `uv sync`
5. **Inicia el backend**: Corre `uv run uvicorn src.main:app --reload` en segundo plano
6. **Instala dependencias del frontend**: Ejecuta `npm install` si es necesario
7. **Inicia el frontend**: Corre `npm run dev`

## 🌐 Servicios Disponibles

Una vez iniciados, los servicios estarán disponibles en:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Base de datos PostgreSQL**: localhost:5432

## 🛑 Detener los Servicios

### Opción 1: Ctrl+C
Presiona `Ctrl+C` en la terminal donde se está ejecutando el script de inicio. Esto detendrá el frontend y el backend, pero la base de datos seguirá corriendo.

### Opción 2: Script de detención
Ejecuta el script `stop.ps1` (Windows) o `stop.sh` (Linux/macOS) en otra terminal para detener todos los servicios incluyendo la base de datos.

```powershell
# Windows
.\stop.ps1
```

```bash
# Linux/macOS
./stop.sh
```

## 🔍 Solución de Problemas

### Docker no está corriendo
```
ERROR: Docker no está corriendo. Por favor inicia Docker Desktop.
```
**Solución**: Inicia Docker Desktop y espera a que esté completamente cargado antes de ejecutar el script.

### Puerto ya en uso
Si algún puerto (5432, 8000, 5173) está en uso:

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Problemas con uv
Si `uv` no está instalado:

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Problemas con npm
Si las dependencias del frontend no se instalan correctamente:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📝 Logs

- **Backend logs**: Se muestran en la terminal o en `backend.log` (Linux/macOS)
- **Frontend logs**: Se muestran en la terminal
- **Database logs**: `docker-compose logs db`

## 🔄 Reiniciar un Servicio Individual

### Solo la base de datos
```bash
docker-compose restart db
```

### Solo el backend
```bash
# Detener
pkill -f uvicorn  # Linux/macOS
# o encontrar el proceso en Windows y matarlo

# Iniciar
uv run uvicorn src.main:app --reload
```

### Solo el frontend
```bash
cd frontend
npm run dev
```
