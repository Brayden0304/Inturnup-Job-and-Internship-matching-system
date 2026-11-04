@echo off
title InternUp - Database Backup Manager
color 0A

cd /d "%~dp0"
echo =========================================================================
echo              INTERNUP - ONE-CLICK DATABASE BACKUP
echo =========================================================================
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe db_sync_backup.py --backup
    echo.
    venv\Scripts\python.exe db_sync_backup.py --stats
) else (
    python db_sync_backup.py --backup
    echo.
    python db_sync_backup.py --stats
)

echo.
echo =========================================================================
echo [SUCCESS] Backup finished! You can view snapshots in the \backups folder.
echo =========================================================================
echo.
pause
