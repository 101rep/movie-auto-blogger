@echo off
chcp 65001 > nul
echo ========================================================
echo  🐾 펫로그 AI (PetLog AI) 모바일 앱 실행 중...
echo ========================================================
echo.
echo [1] 로컬 웹서버를 시작하고 브라우저를 엽니다.
echo [2] 병원 전송 닥터 차트 / O2O 예약 / AI 진단 / 메타 설정
echo.

start "" "http://localhost:8088/index.html"
python -m http.server 8088
pause
