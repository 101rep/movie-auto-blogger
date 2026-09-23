@echo off
chcp 65001 > nul
echo ======================================================
echo   [펫케어 메이트] 전문 펫시터 케어 앱 로컬 서버 구동 중...
echo ======================================================
start http://localhost:8090/index.html
python -m http.server 8090
