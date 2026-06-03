#!/usr/bin/env powershell
# Jarvis Assistant - Schnellstart Script (PowerShell)
# Startet Ollama und die GUI automatisch mit besserer Fehlerbehandlung

param(
    [switch]$SkipOllamaCheck = $false,
    [switch]$NoOllamaWarning = $false
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Jarvis Assistant - Schnellstart (PowerShell Version)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/4] Prüfe Python Installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Python nicht installiert!" -ForegroundColor Red
    Write-Host "  Download: https://python.org" -ForegroundColor Yellow
    Read-Host "  Drücke Enter zum Beenden"
    exit 1
}
Write-Host "  ✓ Python gefunden: $pythonVersion" -ForegroundColor Green

# Check Ollama
Write-Host ""
Write-Host "[2/4] Prüfe Ollama Status..." -ForegroundColor Yellow
$ollamaStatus = $null
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Ollama läuft!" -ForegroundColor Green
        $models = ($response.Content | ConvertFrom-Json).models
        Write-Host "  ✓ Models geladen: $($models.Count)" -ForegroundColor Green
        foreach ($model in $models | Select-Object -First 3) {
            Write-Host "    - $($model.name)" -ForegroundColor Cyan
        }
        $ollamaStatus = $true
    }
} catch {
    $ollamaStatus = $false
}

if (-not $ollamaStatus) {
    Write-Host "  ⚠ Ollama nicht erreichbar!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Öffne ein NEUES Terminal und starte:" -ForegroundColor Yellow
    Write-Host "    > ollama serve" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Warte dann 5 Sekunden, bis Ollama bereit ist..." -ForegroundColor Yellow
    Read-Host "  Drücke Enter wenn Ollama läuft"
    Write-Host ""
}

# Starte GUI
Write-Host "[3/4] Starte Jarvis GUI..." -ForegroundColor Yellow
$jarvisPath = "f:\VSC\Terry"
Push-Location $jarvisPath

try {
    Write-Host "  -> Pfad: $jarvisPath" -ForegroundColor Cyan
    Write-Host "  -> Starte: python Main.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    
    & python Main.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Jarvis konnte nicht gestartet werden!" -ForegroundColor Red
        Write-Host "Exit Code: $LASTEXITCODE" -ForegroundColor Red
        Read-Host "Drücke Enter zum Beenden"
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "ERROR: $($_)" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
} finally {
    Pop-Location
}
