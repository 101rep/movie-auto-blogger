@echo off
chcp 65001 > nul
title 텔레그램 링크 배달원 (Telegram Courier)
echo ============================================================
echo [신규 직원 채용: 링크 배달원 (Telegram Courier)] 실시간 감시 시작
echo 사장님이 텔레그램 채팅방에 올린 링크(올영, 오늘의집, 쿠팡 등)를
echo 실시간 감지하여 [직원 1: 큐레이터]에게 즉시 토스합니다!
echo ============================================================
echo.
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" scripts/run_telegram_courier.py
pause
