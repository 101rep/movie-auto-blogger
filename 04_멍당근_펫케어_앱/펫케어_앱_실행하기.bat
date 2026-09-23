@echo off
chcp 65001 > nul
title 멍당근 (동네 펫용품 나눔 & 펫케어 모바일 앱)
echo ========================================================
echo   🐾 멍당근 (동네 펫용품 나눔 & 펫케어) 모바일 앱 런처
echo ========================================================
echo.
echo [1] 로컬 웹서버를 시작하고 브라우저를 엽니다 (Port 8088).
echo [2] 병원 전송 닥터 차트 / O2O 예약 / AI 진단 / 메타 설정
echo.
cd /d "%~dp0"
start "" "http://localhost:8088/index.html"
python -m http.server 8088
pause
