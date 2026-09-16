@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo                  DATALENS 2.0 STARTUP
echo ============================================================
echo Root: %CD%
echo.

if not exist "backend\requirements.txt" (
  echo ERROR: backend\requirements.txt is missing.
  echo This launcher must stay in the DataLens root folder.
  pause
  exit /b 1
)
if not exist "frontend\package.json" (
  echo ERROR: frontend\package.json is missing.
  pause
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -m venv venv
  if errorlevel 1 python -m venv venv
)
call "venv\Scripts\activate.bat"
python -m pip install -r "backend\requirements.txt"

cd /d "%~dp0frontend"
echo Checking frontend dependencies...
call npm install
if errorlevel 1 (
  echo ERROR: npm install failed.
  pause
  exit /b 1
)
cd /d "%~dp0"

echo Starting backend and frontend...
start "DataLens Backend" cmd /k "cd /d "%~dp0backend" && call ..\venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "DataLens Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
timeout /t 4 /nobreak >nul
start "" http://localhost:5173/
exit /b 0
