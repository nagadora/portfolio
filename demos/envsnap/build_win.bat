@echo off
setlocal

REM --- move to project root (this file's dir) ---
cd /d "%~dp0"

echo [EnvSnap] Build (Windows)

REM --- choose python (prefer venv, then py, then python) ---
set PY=
if exist ".venv\Scripts\python.exe" set PY=.venv\Scripts\python.exe

if "%PY%"=="" (
  where py >nul 2>nul
  if %ERRORLEVEL%==0 set PY=py -3
)

if "%PY%"=="" (
  where python >nul 2>nul
  if %ERRORLEVEL%==0 set PY=python
)

if "%PY%"=="" (
  echo Python not found. Install Python or enable 'py' launcher.
  echo Or create .venv manually.
  exit /b 2
)

REM --- create venv if missing ---
if not exist ".venv\Scripts\python.exe" (
  echo [EnvSnap] Creating venv...
  %PY% -m venv .venv
)

set VPY=.venv\Scripts\python.exe

echo [EnvSnap] Upgrading pip...
"%VPY%" -m pip install --upgrade pip >nul

echo [EnvSnap] Installing PyInstaller...
"%VPY%" -m pip install --upgrade pyinstaller >nul

echo [EnvSnap] Cleaning old outputs...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo [EnvSnap] Building envsnap_win.exe ...
"%VPY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name envsnap_win ^
  --paths python_core ^
  python_core\envsnap_gui.py

echo.
echo [EnvSnap] Done.
echo Output: dist\envsnap_win.exe
endlocal