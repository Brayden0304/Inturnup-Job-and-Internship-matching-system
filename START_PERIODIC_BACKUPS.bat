@echo off
title InternUp - Periodic Database Auto-Backup Service
color 0A

cd /d "%~dp0"
echo =========================================================================
echo              INTERNUP - PERIODIC DATABASE AUTO-BACKUP
echo =========================================================================
echo.
echo  This service automatically takes timestamped snapshots of your database
echo  and saves them into the \backups folder.
echo.
echo  Choose your desired backup interval:
echo    [1] Every 15 minutes (Selected / Active)
echo    [2] Every 30 minutes (Default / Recommended)
echo    [3] Every 1 hour
echo    [4] Every 6 hours
echo    [5] Run ONE backup right now and exit
echo =========================================================================
echo.

set /p choice="Enter choice [1-5, default 1]: "
if "%choice%"=="" set choice=1

set "INTERVAL=30"
if "%choice%"=="1" set "INTERVAL=15"
if "%choice%"=="2" set "INTERVAL=30"
if "%choice%"=="3" set "INTERVAL=60"
if "%choice%"=="4" set "INTERVAL=360"
if "%choice%"=="5" (
    if exist "venv\Scripts\python.exe" (
        venv\Scripts\python.exe periodic_backup.py --once
    ) else (
        python periodic_backup.py --once
    )
    pause
    exit /b 0
)

echo.
echo Starting auto-backup loop (Interval: %INTERVAL% minutes)...
echo NOTE: Keep this window minimized to keep automatic backups active.
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe periodic_backup.py --interval %INTERVAL% --retention 20
) else (
    python periodic_backup.py --interval %INTERVAL% --retention 20
)

pause
