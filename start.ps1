# Task Manager - Script de inicio para Windows (PowerShell)
# Este script levanta toda la aplicacion con un solo comando

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Task Manager - Iniciando servicios" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker este corriendo
Write-Host "[1/6] Verificando Docker..." -ForegroundColor Yellow
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker no esta corriendo. Por favor inicia Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "OK - Docker esta corriendo" -ForegroundColor Green
Write-Host ""

# Iniciar la base de datos con docker-compose
Write-Host "[2/6] Iniciando base de datos PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d db
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo iniciar la base de datos" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Base de datos iniciada" -ForegroundColor Green
Write-Host ""

# Esperar a que la base de datos este lista
Write-Host "[3/6] Esperando a que la base de datos este lista..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$dbReady = $false

while ($attempt -lt $maxAttempts -and -not $dbReady) {
    $attempt++
    $healthCheck = docker-compose ps db --format json | ConvertFrom-Json
    if ($healthCheck.Health -eq "healthy") {
        $dbReady = $true
    } else {
        Write-Host "  Intento $attempt/$maxAttempts - Esperando..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $dbReady) {
    Write-Host "ERROR: La base de datos no respondio a tiempo" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Base de datos lista" -ForegroundColor Green
Write-Host ""

# Instalar dependencias del backend con uv
Write-Host "[4/6] Instalando dependencias del backend..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar las dependencias del backend" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Dependencias del backend instaladas" -ForegroundColor Green
Write-Host ""

# Ejecutar migraciones de la base de datos
Write-Host "[4.5/6] Ejecutando migraciones de base de datos..." -ForegroundColor Yellow
uv run alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: Las migraciones fallaron, pero continuando..." -ForegroundColor Yellow
}
Write-Host "OK - Migraciones ejecutadas" -ForegroundColor Green
Write-Host ""

# Ejecutar seeder para datos iniciales
Write-Host "[4.7/6] Cargando datos iniciales (seeder)..." -ForegroundColor Yellow
uv run python -m src.seed_data
if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: El seeder fallo, pero continuando..." -ForegroundColor Yellow
}
Write-Host "OK - Datos iniciales cargados" -ForegroundColor Green
Write-Host ""

# Iniciar el backend en segundo plano
Write-Host "[5/6] Iniciando servidor backend..." -ForegroundColor Yellow
# Crear archivos de log para el backend
$backendLogOut = Join-Path $PWD "backend-stdout.log"
$backendLogErr = Join-Path $PWD "backend-stderr.log"
# Iniciar uvicorn con reload
$backendProcess = Start-Process -FilePath "uv" -ArgumentList "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -PassThru -NoNewWindow -WorkingDirectory $PWD -RedirectStandardOutput $backendLogOut -RedirectStandardError $backendLogErr
if ($backendProcess) {
    Write-Host "OK - Backend iniciado (PID: $($backendProcess.Id))" -ForegroundColor Green
    Write-Host "     Logs: backend-stdout.log y backend-stderr.log" -ForegroundColor Gray
} else {
    Write-Host "ERROR: No se pudo iniciar el backend" -ForegroundColor Red
    exit 1
}
Start-Sleep -Seconds 5
Write-Host ""

# Instalar dependencias del frontend
Write-Host "[6/6] Instalando dependencias del frontend..." -ForegroundColor Yellow
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudieron instalar las dependencias del frontend" -ForegroundColor Red
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
        exit 1
    }
}
Write-Host "OK - Dependencias del frontend instaladas" -ForegroundColor Green
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  OK - Todos los servicios iniciados" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servicios disponibles:" -ForegroundColor White
Write-Host "  - Base de datos: localhost:5432" -ForegroundColor White
Write-Host "  - API Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Frontend:      (iniciando...)" -ForegroundColor White
Write-Host ""
Write-Host "Para detener los servicios presiona Ctrl+C" -ForegroundColor Yellow
Write-Host "Para detener la base de datos ejecuta: docker-compose down" -ForegroundColor Yellow
Write-Host ""

# Iniciar el frontend (esto bloqueara la terminal)
Write-Host "Iniciando frontend..." -ForegroundColor Yellow
npm run dev

# Cleanup cuando se detenga el frontend
Write-Host ""
Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
# Usar taskkill con /T para matar el proceso y todos sus hijos
taskkill /F /T /PID $backendProcess.Id > $null 2>&1
Set-Location ..
Write-Host "OK - Backend detenido" -ForegroundColor Green
Write-Host "Para detener la base de datos, ejecuta: docker-compose down" -ForegroundColor Yellow
