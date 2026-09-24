@echo off
chcp 65001 > nul
title 8대 블로그 Cloudways 서버 원클릭 최신 동기화
echo ======================================================
echo   8대 블로그 통합 시스템 -^> Cloudways 서버 원클릭 최신 동기화
echo ======================================================
echo.
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" deploy_to_cloudways.py
echo.
pause
