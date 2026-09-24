@echo off
cd /d "%~dp0"
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
"%PYTHON_EXE%" "%~dp0launcher.py"
