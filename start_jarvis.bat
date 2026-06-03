@echo off
REM Jarvis Assistant - Schnellstart Script
REM Startet Ollama und die GUI automatisch

echo.
echo ============================================================
echo   Jarvis Assistant - Schnellstart
echo ============================================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python nicht installiert!
    echo Bitte Python 3.10+ von python.org installieren
    pause
    exit /b 1
)

REM Starte Ollama im Hintergrund (falls nicht läuft)
echo [1/3] Starte Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo   -> Ollama nicht gefunden. Bitte manuell starten:
    echo   -> ollama serve
    echo.
    echo   Warte 5 Sekunden, dann startet Jarvis...
    timeout /t 5 /nobreak
) else (
    echo   -> Ollama läuft bereits
)

echo.
echo [2/3] Starte Jarvis GUI...
cd /d f:\VSC\Terry
python Main.py

if errorlevel 1 (
    echo.
    echo ERROR: Jarvis konnte nicht gestartet werden!
    pause
    exit /b 1
)
