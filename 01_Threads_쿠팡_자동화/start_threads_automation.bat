@echo off
chcp 65001 > nul
title Threads x Coupang 콘텐츠 자동화 시스템
echo ===================================================
echo [Threads x 쿠팡파트너스 AI 콘텐츠 자동화 시스템]
echo ===================================================
echo.
echo 시스템을 시작합니다...
echo.
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
echo [1/2] 백그라운드 서버 및 자동화 워커 시작 중 (Port 8080)...
start "Threads Coupang Server" /min "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8080
echo [2/2] 브라우저 접속 준비 중...
timeout /t 3 /nobreak > nul
echo 대시보드를 브라우저에서 엽니다: http://localhost:8080
start "" "http://localhost:8080"
echo 시스템이 정상 실행되었습니다!
timeout /t 3 > nul
exit
