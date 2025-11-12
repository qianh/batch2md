@echo off
REM Start script for Batch2MD web interface (Windows)
REM This script starts both the backend API and frontend dev server

echo ========================================
echo   Batch2MD Web Interface Starter
echo ========================================
echo.

REM Check if we're in the project root
if not exist "pyproject.toml" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Check Python dependencies
echo Checking Python dependencies...
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: 'uv' not found. Please install uv first.
    exit /b 1
)

REM Install Python web dependencies
echo Installing Python dependencies...
call uv sync --extra web

REM Check Node.js/npm
echo Checking Node.js dependencies...
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: 'npm' not found. Please install Node.js first.
    exit /b 1
)

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Create log directory
if not exist "logs" mkdir logs

echo.
echo Starting services...
echo Backend API will run on: http://localhost:8000
echo Frontend will run on: http://localhost:5173
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start backend in new window
echo [1/2] Starting backend API...
start "Batch2MD Backend" /MIN cmd /c "uv run batch2md-web > logs\backend.log 2>&1"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo Backend started
echo.

REM Start frontend in new window
echo [2/2] Starting frontend dev server...
cd frontend
start "Batch2MD Frontend" /MIN cmd /c "npm run dev > ..\logs\frontend.log 2>&1"
cd ..

REM Wait for frontend to start
timeout /t 3 /nobreak >nul

echo Frontend started
echo.
echo ========================================
echo   All services are running!
echo ========================================
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Logs:
echo   - Backend: logs\backend.log
echo   - Frontend: logs\frontend.log
echo.
echo Close the terminal windows to stop the services
echo.
pause
