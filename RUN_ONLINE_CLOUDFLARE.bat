@echo off
title InternUp - 1-Click Cloudflare Online Host
color 0A

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe run_cloudflare.py
) else (
    python run_cloudflare.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Process exited with code %ERRORLEVEL%.
    pause
)
