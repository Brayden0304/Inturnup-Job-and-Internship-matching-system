@echo off
title LaunchPad Database Reseed
cd /d "%~dp0"
echo ====================================================
echo Resetting and Seeding Database...
echo Populating 8 Demo Accounts and 20 Job Postings
echo ====================================================
echo.
python seed.py
echo.
echo Database setup complete! You can now start the server with start_server.bat.
pause
