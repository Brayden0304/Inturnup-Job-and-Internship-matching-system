@echo off
title InternUp - Local Development Mode
color 0B

cd /d "%~dp0"
echo ========================================
echo   InternUp - LOCAL Development Mode
echo ========================================
echo.
echo Starting Flask app in development mode...
echo - Debug mode: ON
echo - Access: http://localhost:5000
echo - Database: instance/app.db
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe app.py
) else (
    python app.py
)

pause
