@echo off
chcp 65001 > nul
echo ======================================================
echo   Cloudways 클라우드 서버 원클릭 최신 동기화 진행 중...
echo ======================================================
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" scripts\sync_to_cloudways.py
echo.
pause
