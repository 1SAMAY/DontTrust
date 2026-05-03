@echo off
setlocal
set PYTHON_EXE=C:\Users\Samay\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
set PYTHONW_EXE=C:\Users\Samay\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe
if exist "%PYTHONW_EXE%" (
  start "" "%PYTHONW_EXE%" "%~dp0app.py"
) else if exist "%PYTHON_EXE%" (
  start "" "%PYTHON_EXE%" "%~dp0app.py"
) else (
  start "" pythonw "%~dp0app.py"
)
