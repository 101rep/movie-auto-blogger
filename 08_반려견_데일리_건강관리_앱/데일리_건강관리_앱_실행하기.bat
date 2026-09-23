@echo off
chcp 65001 > nul
echo ======================================================
echo   [펫닥터 데일리] 데일리 건강기록 앱 로컬 서버 구동 중...
echo ======================================================
start http://localhost:8092/index.html
python -m http.server 8092
