@echo off
title GRAV - Galaxy Rotation Analyze Viewer
:: Get the directory of the batch file
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ▣ Initializing GRAV Engine...
python launcher.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Error: Critical failure during startup.
    pause
)

