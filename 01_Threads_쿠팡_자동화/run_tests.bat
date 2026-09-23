@echo off
chcp 65001 > nul
echo [THREADS x COUPANG] 단위/서비스/통합 테스트를 실행합니다...
cd /d "%~dp0"
set PYTHONPATH=.
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" -m pytest tests -v
pause
