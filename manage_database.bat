@echo off
title InternUp - Database & Sync Manager
color 0B

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe db_sync_backup.py
) else (
    python db_sync_backup.py
)

pause
