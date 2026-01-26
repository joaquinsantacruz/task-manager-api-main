# Task Manager - Inicio Rápido 🚀

¡Levanta toda la aplicación con un solo comando!

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instalado:

- ✅ **Docker Desktop** (instalado y en ejecución)
- ✅ **Node.js** y **npm** (v18 o superior)
- ✅ **Python 3.13+** y **uv** (gestor de paquetes)

### Instalar uv (si no lo tienes)

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 🚀 Inicio Rápido con UN SOLO COMANDO

### Windows (PowerShell)

```powershell
.\start.ps1
```

### Linux/macOS (Bash)

```bash
# Dar permisos de ejecución (solo la primera vez)
chmod +x start.sh

# Iniciar
./start.sh
```

**¡Eso es todo!** El script automáticamente:

1. ✅ Verifica que Docker esté corriendo
2. ✅ Inicia la base de datos PostgreSQL
3. ✅ Espera a que la BD esté lista
4. ✅ Instala dependencias del backend
5. ✅ Inicia el servidor backend
6. ✅ Instala dependencias del frontend
7. ✅ Inicia el servidor frontend

---

## 🌐 Acceder a la Aplicación

Una vez iniciado, los servicios estarán disponibles en:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:5173 | Interfaz de usuario React |
| **Backend API** | http://localhost:8000 | API REST FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentación Swagger |
| **Base de Datos** | localhost:5432 | PostgreSQL |

### Credenciales por defecto

**Usuario Owner:**
- Email: `owner@example.com`
- Password: `ownerpass`

**Usuario Member:**
- Email: `member@example.com`
- Password: `memberpass`

---

## 🛑 Detener la Aplicación

### Opción 1: Detener solo Frontend y Backend

Presiona `Ctrl+C` en la terminal donde ejecutaste el script de inicio.

> **Nota:** La base de datos seguirá corriendo en Docker.

### Opción 2: Detener TODO (incluyendo la base de datos)

**Windows:**
```powershell
.\stop.ps1
```

**Linux/macOS:**
```bash
./stop.sh
```

---

## 🔧 Comandos Manuales (Alternativa)

Si prefieres iniciar los servicios manualmente:

### 1. Base de datos
```bash
docker-compose up -d db
```

### 2. Backend
```bash
uv sync                                    # Instalar dependencias
uv run uvicorn src.main:app --reload      # Iniciar servidor
```

### 3. Frontend
```bash
cd frontend
npm install                                # Instalar dependencias
npm run dev                                # Iniciar servidor
```

---

## 🔍 Solución de Problemas

### ❌ "Docker no está corriendo"

**Problema:** El script no puede conectarse a Docker.

**Solución:**
1. Abre Docker Desktop
2. Espera a que el ícono de Docker en la barra de tareas esté verde
3. Vuelve a ejecutar el script

---

### ❌ Puerto ya en uso

**Problema:** Error indicando que un puerto (5432, 8000, 5173) ya está en uso.

**Solución Windows:**
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplaza <PID> con el número mostrado)
taskkill /PID <PID> /F
```

**Solución Linux/macOS:**
```bash
# Ver qué proceso usa el puerto
lsof -i :8000

# Matar el proceso
kill -9 <PID>
```

---

### ❌ "uv: command not found"

**Problema:** uv no está instalado o no está en el PATH.

**Solución:**
```powershell
# Windows (PowerShell como Administrador)
irm https://astral.sh/uv/install.ps1 | iex
```

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Luego, reinicia la terminal.

---

### ❌ Base de datos no se conecta

**Problema:** El backend no puede conectarse a PostgreSQL.

**Solución:**
```bash
# Ver logs de la base de datos
docker-compose logs db

# Reiniciar la base de datos
docker-compose restart db

# O detener y volver a iniciar
docker-compose down
docker-compose up -d db
```

---

### ❌ Errores en dependencias de npm

**Problema:** El frontend no instala correctamente las dependencias.

**Solución:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 Ver Logs

### Backend
Los logs del backend se muestran en la terminal.

**Linux/macOS:** También se guardan en `backend.log`

### Frontend
Los logs de Vite se muestran en la terminal.

### Base de datos
```bash
docker-compose logs db
docker-compose logs -f db    # Seguir logs en tiempo real
```

---

## 🔄 Reiniciar un Servicio Individual

### Solo la base de datos
```bash
docker-compose restart db
```

### Solo el backend
```bash
# Detener (encontrar PID y matar proceso)
# Windows: Ctrl+C o Task Manager
# Linux/macOS: 
pkill -f uvicorn

# Iniciar
uv run uvicorn src.main:app --reload
```

### Solo el frontend
```bash
cd frontend
npm run dev
```

---

## 📚 Documentación Adicional

- **[README_SCRIPTS.md](README_SCRIPTS.md)** - Documentación detallada de los scripts
- **[initial_README.md](initial_README.md)** - Documentación completa del proyecto
- **API Docs:** http://localhost:8000/docs (cuando el backend esté corriendo)

---

## 💡 Tips

- Los cambios en el código se recargan automáticamente (hot-reload)
- El backend tiene **Swagger UI** en http://localhost:8000/docs
- Puedes inspeccionar la base de datos con cualquier cliente PostgreSQL:
  - Host: `localhost`
  - Puerto: `5432`
  - Usuario: `taskuser`
  - Password: `taskpass`
  - Database: `taskmanager`
