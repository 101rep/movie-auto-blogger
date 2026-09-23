@echo off
chcp 65001 > nul
echo ======================================================
echo   Cloudways 클라우드 서버에서 최신 코드 및 DB 다운로드 중...
echo ======================================================
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" scripts\pull_from_cloudways.py
echo.
pause
