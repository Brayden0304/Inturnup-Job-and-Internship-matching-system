@echo off
title InternUp - Windows Task Scheduler Auto-Backup
color 0B

cd /d "%~dp0"
echo =========================================================================
echo       INTERNUP - WINDOWS AUTOMATED SCHEDULED TASK CONFIGURATION
echo =========================================================================
echo.
echo  This tool registers an automated background task in Windows Task Scheduler
echo  so your database is automatically backed up periodically in the background,
echo  even when no terminal is open.
echo.
echo  Choose an automated schedule:
echo    [1] Daily at 12:00 PM (Noon)
echo    [2] Daily at 06:00 PM
echo    [3] Hourly (Every 60 minutes)
echo    [4] Remove / Delete Existing Scheduled Backup Task
echo =========================================================================
echo.

set /p choice="Select option [1-4]: "

set "TASK_NAME=InternUp_Database_AutoBackup"
set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python.exe"
set "SCRIPT_PATH=%~dp0periodic_backup.py"

if "%choice%"=="1" (
    schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --once" /sc daily /st 12:00 /f
    echo.
    echo [SUCCESS] Scheduled Task created: Runs daily at 12:00 PM.
)
if "%choice%"=="2" (
    schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --once" /sc daily /st 18:00 /f
    echo.
    echo [SUCCESS] Scheduled Task created: Runs daily at 06:00 PM.
)
if "%choice%"=="3" (
    schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --once" /sc hourly /mo 1 /f
    echo.
    echo [SUCCESS] Scheduled Task created: Runs hourly.
)
if "%choice%"=="4" (
    schtasks /delete /tn "%TASK_NAME%" /f
    echo.
    echo [SUCCESS] Scheduled Task '%TASK_NAME%' has been removed.
)

echo.
pause
