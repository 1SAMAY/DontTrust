@echo off
setlocal
set "APP_DIR=%~dp0"
set "APP_PATH=%APP_DIR%app.py"

if exist "%APP_DIR%venv\Scripts\pythonw.exe" (
  start "" "%APP_DIR%venv\Scripts\pythonw.exe" "%APP_PATH%"
  exit /b
)

where pyw >nul 2>nul
if not errorlevel 1 (
  start "" pyw "%APP_PATH%"
  exit /b
)

where pythonw >nul 2>nul
if not errorlevel 1 (
  start "" pythonw "%APP_PATH%"
  exit /b
)

where py >nul 2>nul
if not errorlevel 1 (
  start "" py -3 "%APP_PATH%"
  exit /b
)

where python >nul 2>nul
if not errorlevel 1 (
  start "" python "%APP_PATH%"
  exit /b
)

echo Python was not found. Install Python 3 or add a local venv.
pause
