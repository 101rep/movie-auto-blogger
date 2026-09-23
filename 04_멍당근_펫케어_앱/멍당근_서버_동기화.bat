@echo off
chcp 65001 > nul
echo ======================================================
echo   [멍당근] Cloudways 서버 실시간 배포 동기화 진행 중...
echo ======================================================
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" ..\01_Threads_쿠팡_자동화\scripts\deploy_mung_to_cloudways.py
echo.
echo ======================================================
echo   배포가 완료되었습니다!
echo   접속 주소: https://trendspot24.com/mung/index.html
echo ======================================================
pause
