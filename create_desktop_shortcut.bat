@echo off
setlocal enabledelayedexpansion
title Create InternUp Desktop Shortcut
echo =========================================================================
echo              Create InternUp Desktop Web Link Shortcut
echo =========================================================================
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\InternUp.url"
set "SITE_URL=http://127.0.0.1:5000/"

:: Check if Cloudflare URL was saved from tunnel execution
if exist "%~dp0CLOUDFLARE_URL.txt" (
    set /p CF_SAVED=<"%~dp0CLOUDFLARE_URL.txt"
    if not "!CF_SAVED!"=="" (
        set "SITE_URL=!CF_SAVED!"
        echo Found active Cloudflare link: !SITE_URL!
    )
)

echo Generating shortcut pointing to: %SITE_URL%
(
    echo [InternetShortcut]
    echo URL=%SITE_URL%
    echo IconIndex=0
    echo HotKey=0
) > "%SHORTCUT%"

echo.
echo =========================================================================
echo [SUCCESS] InternUp web link shortcut created on your Desktop:
echo "%SHORTCUT%"
echo Destination URL: %SITE_URL%
echo =========================================================================
echo.
pause
