@echo off
REM Build script for Windows

echo ===========================================
echo   Symlink Manager - Build Script
echo ===========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found!
    echo Please create it with: python -m venv .venv
    pause
    exit /b 1
)

REM Run the build
.venv\Scripts\python.exe build_executable.py

pause
