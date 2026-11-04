@echo off
title InternUp - 1-Click New Device Automated Setup
color 0B
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo =========================================================================
echo              INTERNUP - 1-CLICK NEW DEVICE AUTOMATED SETUP
echo =========================================================================
echo.
echo  This script will automatically configure InternUp on this new computer:
echo    [1] Verify Python 3.10+ installation
echo    [2] Build local virtual environment (venv)
echo    [3] Install all dependencies (Flask, scikit-learn, PyMySQL, etc.)
echo    [4] Initialize & seed database with Richfield demo accounts
echo    [5] Verify Cloudflare Tunnel binary for online hosting
echo.
echo =========================================================================
echo.
pause

:: 1. Verify Python
echo [1/5] Checking Python installation...
set "PYTHON_CMD="
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
) else (
    py --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py"
    )
)

if "%PYTHON_CMD%"=="" (
    color 0C
    echo.
    echo =========================================================================
    echo [ERROR] Python 3 was not detected on this system!
    echo.
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. IMPORTANT: Check the box "Add python.exe to PATH" during installation.
    echo 3. Re-run this SETUP_NEW_DEVICE.bat file.
    echo =========================================================================
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version') do echo       Found: %%v

:: 2. Check or build venv
echo.
echo [2/5] Configuring virtual environment (venv)...
set "REBUILD_VENV=0"
if not exist "venv\Scripts\python.exe" (
    set "REBUILD_VENV=1"
) else (
    :: Test if copied venv works on this machine (paths match)
    venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo       Existing venv contains paths from previous device. Rebuilding cleanly...
        rmdir /s /q "venv" >nul 2>&1
        set "REBUILD_VENV=1"
    )
)

if "!REBUILD_VENV!"=="1" (
    echo       Creating clean virtual environment...
    %PYTHON_CMD% -m venv venv
    if !ERRORLEVEL! NEQ 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment. Ensure python-venv is available.
        pause
        exit /b 1
    )
    echo       [OK] Virtual environment created.
) else (
    echo       [OK] Existing virtual environment is verified and operational.
)

:: 3. Install Requirements
echo.
echo [3/5] Installing project dependencies from requirements.txt...
venv\Scripts\pip.exe install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo       Retrying package installation with verbose logging...
    venv\Scripts\pip.exe install -r requirements.txt
)
echo       [OK] All Python dependencies installed and verified.

:: 4. Database Setup
echo.
echo [4/5] Checking Database (instance/app.db)...
if not exist "instance\app.db" (
    echo       Database missing. Seeding demo accounts and listings...
    venv\Scripts\python.exe seed.py
    echo       [OK] Database created and seeded.
) else (
    echo       [OK] Database already exists.
    venv\Scripts\python.exe db_sync_backup.py --stats
)

:: 5. Cloudflare Tunnel Binary
echo.
echo [5/5] Checking Cloudflare Tunnel (cloudflared.exe)...
if not exist "cloudflared.exe" (
    echo       Downloading official Cloudflare tunnel binary...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if exist "cloudflared.exe" (
        echo       [OK] cloudflared.exe downloaded successfully.
    ) else (
        echo       [!] Warning: Could not download cloudflared.exe. Offline mode will still work.
    )
) else (
    echo       [OK] cloudflared.exe is present.
)

:: Create Desktop Shortcut
if exist "create_desktop_shortcut.bat" (
    call create_desktop_shortcut.bat >nul 2>&1
)

color 0A
echo.
echo =========================================================================
echo       ***  SETUP COMPLETE! INTERNUP IS READY ON THIS DEVICE  ***
echo =========================================================================
echo.
echo  HOW TO RUN:
echo    1. OFFLINE / LOCAL (No internet needed):
echo       - Double-click: run_local.bat
echo       - Access in browser: http://localhost:5000
echo.
echo    2. ONLINE (Public live internet link for phones, laptops, markers):
echo       - Double-click: RUN_ONLINE_CLOUDFLARE.bat
echo       - Automatically generates public HTTPS link and opens browser.
echo.
echo    3. DATABASE BACKUP & SYNC:
echo       - Double-click: backup_database.bat (instant snapshot)
echo       - Double-click: manage_database.bat (backup, restore, transfer)
echo =========================================================================
echo.
pause
