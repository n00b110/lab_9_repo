@echo off
REM Setup script for Domain Adapted AI Assistant on Windows
REM This script sets up the development environment

echo.
echo ============================================================
echo Domain Adapted AI Assistant - Windows Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found:
python --version

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [4/4] Installing dependencies...
echo This may take several minutes...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo .env file created - please review and update settings if needed
)

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist logs mkdir logs
if not exist models mkdir models
if not exist evaluation_results mkdir evaluation_results

REM Summary
echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Virtual environment is now active.
echo.
echo To start the API server:
echo   python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
echo.
echo To start the Streamlit frontend (in a new terminal):
echo   streamlit run app/streamlit_app.py --server.port 8501
echo.
echo Or use the Makefile if you have make installed:
echo   make run
echo.
echo For more information, see README.md
echo.
pause
