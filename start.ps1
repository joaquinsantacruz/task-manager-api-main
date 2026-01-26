# Task Manager - Script de inicio para Windows (PowerShell)
# Este script levanta toda la aplicación con un solo comando

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Task Manager - Iniciando servicios" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esté corriendo
Write-Host "[1/6] Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker no está corriendo. Por favor inicia Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker está corriendo" -ForegroundColor Green
Write-Host ""

# Iniciar la base de datos con docker-compose
Write-Host "[2/6] Iniciando base de datos PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d db
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo iniciar la base de datos" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Base de datos iniciada" -ForegroundColor Green
Write-Host ""

# Esperar a que la base de datos esté lista
Write-Host "[3/6] Esperando a que la base de datos esté lista..." -ForegroundColor Yellow
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
    Write-Host "ERROR: La base de datos no respondió a tiempo" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Base de datos lista" -ForegroundColor Green
Write-Host ""

# Instalar dependencias del backend con uv
Write-Host "[4/6] Instalando dependencias del backend..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar las dependencias del backend" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencias del backend instaladas" -ForegroundColor Green
Write-Host ""

# Iniciar el backend en segundo plano
Write-Host "[5/6] Iniciando servidor backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
}
Write-Host "✓ Backend iniciado (Job ID: $($backendJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 3
Write-Host ""

# Instalar dependencias del frontend
Write-Host "[6/6] Instalando dependencias del frontend..." -ForegroundColor Yellow
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudieron instalar las dependencias del frontend" -ForegroundColor Red
        Stop-Job $backendJob
        Remove-Job $backendJob
        exit 1
    }
}
Write-Host "✓ Dependencias del frontend instaladas" -ForegroundColor Green
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ✓ Todos los servicios iniciados" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servicios disponibles:" -ForegroundColor White
Write-Host "  - Base de datos: localhost:5432" -ForegroundColor White
Write-Host "  - API Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Frontend:      (iniciando...)" -ForegroundColor White
Write-Host ""
Write-Host "Para detener los servicios, presiona Ctrl+C y ejecuta: docker-compose down" -ForegroundColor Yellow
Write-Host ""

# Iniciar el frontend (esto bloqueará la terminal)
Write-Host "Iniciando frontend..." -ForegroundColor Yellow
npm run dev

# Cleanup cuando se detenga el frontend
Write-Host ""
Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
Stop-Job $backendJob -ErrorAction SilentlyContinue
Remove-Job $backendJob -ErrorAction SilentlyContinue
Set-Location ..
Write-Host "Para detener la base de datos, ejecuta: docker-compose down" -ForegroundColor Yellow
