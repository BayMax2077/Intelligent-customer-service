@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ======================================
echo Intelligent Customer Service - Start
echo ======================================

REM 1) Ensure Python exists
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found in PATH.
  echo Please install Python 3.10+ and re-run.
  pause
  exit /b 1
)

REM 2) Create and activate venv if missing
if not exist .venv\Scripts\activate.bat (
  echo [INFO] Creating virtual environment...
  python -m venv .venv || (
    echo [ERROR] Failed to create virtual environment.
    pause & exit /b 1
  )
)

REM 3) Install backend requirements if first run (or upgrade marker missing)
if not exist .venv\.installed (
  echo [INFO] Installing Python dependencies...
  call .venv\Scripts\activate.bat && pip install -r requirements.txt || (
    echo [ERROR] Failed to install Python dependencies.
    pause & exit /b 1
  )
  echo ok> .venv\.installed
)

REM 4) Start backend on port 5002 in a new window
echo [INFO] Starting backend (port 5002)...
start "Backend-5002" cmd /c "call .venv\Scripts\activate.bat && python -m houduan.app"

REM 5) Prepare frontend (install deps on first run)
if not exist qianduan\node_modules (
  echo [INFO] Installing frontend dependencies...
  pushd qianduan
  call npm install || (echo [ERROR] npm install failed & popd & pause & exit /b 1)
  popd
)

REM 6) Start frontend preview on port 5174 in a new window
echo [INFO] Starting frontend (port 5174)...
start "Frontend-5174" cmd /c "cd /d qianduan && npm run preview -- --port 5174 --strictPort"

REM 7) Print URLs
echo.
echo Backend:  http://localhost:5002/health
echo Frontend: http://localhost:5174/
echo.
echo Press any key to close this launcher (services keep running)...
pause >nul


