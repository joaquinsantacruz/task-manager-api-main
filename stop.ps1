# Task Manager - Script de detención para Windows (PowerShell)
# Este script detiene todos los servicios

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Task Manager - Deteniendo servicios" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Detener contenedores de Docker
Write-Host "Deteniendo contenedores Docker..." -ForegroundColor Yellow
docker-compose down
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Contenedores Docker detenidos" -ForegroundColor Green
} else {
    Write-Host "! No se pudieron detener algunos contenedores" -ForegroundColor Yellow
}
Write-Host ""

# Detener procesos de uvicorn (backend)
Write-Host "Deteniendo servidor backend..." -ForegroundColor Yellow
$uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }
if ($uvicornProcesses) {
    $uvicornProcesses | Stop-Process -Force
    Write-Host "✓ Servidor backend detenido" -ForegroundColor Green
} else {
    Write-Host "- No se encontraron procesos backend activos" -ForegroundColor Gray
}
Write-Host ""

# Detener procesos de Vite (frontend)
Write-Host "Deteniendo servidor frontend..." -ForegroundColor Yellow
$viteProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
if ($viteProcesses) {
    $viteProcesses | Stop-Process -Force
    Write-Host "✓ Servidor frontend detenido" -ForegroundColor Green
} else {
    Write-Host "- No se encontraron procesos frontend activos" -ForegroundColor Gray
}
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ✓ Servicios detenidos" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
