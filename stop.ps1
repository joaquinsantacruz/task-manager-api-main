# Task Manager - Script de detencion para Windows (PowerShell)
# Este script detiene todos los servicios

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Task Manager - Deteniendo servicios" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Detener contenedores de Docker
Write-Host "Deteniendo contenedores Docker..." -ForegroundColor Yellow
docker-compose down
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Contenedores Docker detenidos" -ForegroundColor Green
} else {
    Write-Host "AVISO - No se pudieron detener algunos contenedores" -ForegroundColor Yellow
}
Write-Host ""

# Detener procesos de uvicorn (backend)
Write-Host "Deteniendo servidor backend..." -ForegroundColor Yellow
$backendPort = 8000
$backendConnection = Get-NetTCPConnection -LocalPort $backendPort -State Listen -ErrorAction SilentlyContinue
if ($backendConnection) {
    $backendPID = $backendConnection.OwningProcess
    # Usar taskkill con /T para matar el proceso y todos sus hijos
    taskkill /F /T /PID $backendPID > $null 2>&1
    Write-Host "OK - Servidor backend detenido (PID: $backendPID y procesos hijos)" -ForegroundColor Green
} else {
    Write-Host "INFO - No se encontraron procesos backend activos en puerto $backendPort" -ForegroundColor Gray
}
Write-Host ""

# Detener procesos de Vite (frontend)
Write-Host "Deteniendo servidor frontend..." -ForegroundColor Yellow
$frontendPort = 5173
$frontendConnection = Get-NetTCPConnection -LocalPort $frontendPort -State Listen -ErrorAction SilentlyContinue
if ($frontendConnection) {
    $frontendPID = $frontendConnection.OwningProcess
    # Usar taskkill con /T para matar el proceso y todos sus hijos
    taskkill /F /T /PID $frontendPID > $null 2>&1
    Write-Host "OK - Servidor frontend detenido (PID: $frontendPID y procesos hijos)" -ForegroundColor Green
} else {
    Write-Host "INFO - No se encontraron procesos frontend activos en puerto $frontendPort" -ForegroundColor Gray
}
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  OK - Servicios detenidos" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
