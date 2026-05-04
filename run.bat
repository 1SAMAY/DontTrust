@echo off
setlocal
set "APP_DIR=%~dp0"
set "APP_PATH=%APP_DIR%app.py"

if not exist "%APP_PATH%" (
  echo Could not find app.py in "%APP_DIR%".
  pause
  exit /b 1
)

if exist "%APP_DIR%venv\Scripts\pythonw.exe" (
  start "" "%APP_DIR%venv\Scripts\pythonw.exe" "%APP_PATH%"
  exit /b
)

for %%P in (pyw pythonw) do (
  where %%P >nul 2>nul
  if not errorlevel 1 (
    start "" %%P "%APP_PATH%"
    exit /b
  )
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

echo Python 3 was not found.
echo Install Python from https://www.python.org/downloads/ or create a local venv.
pause
exit /b 1
