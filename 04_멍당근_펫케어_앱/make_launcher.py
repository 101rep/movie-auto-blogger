import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bat_path = os.path.join(root_dir, "펫케어_앱_실행하기.bat")

bat_lines = [
    "@echo off",
    "chcp 65001 > nul",
    "echo ========================================================",
    "echo   🐾 펫로그 AI (PetLog AI) 모바일 앱 런처",
    "echo ========================================================",
    "echo.",
    "echo [1] 로컬 웹서버를 시작하고 브라우저를 엽니다.",
    "echo [2] 병원 전송 닥터 차트 / O2O 예약 / AI 진단 / 메타 설정",
    "echo.",
    'start "" "http://localhost:8088/index.html"',
    'cd /d "%~dp0PetCare_App"',
    "python -m http.server 8088",
    "pause"
]

with open(bat_path, "w", encoding="utf-8") as f:
    f.write("\n".join(bat_lines))

print("Created 펫케어_앱_실행하기.bat successfully at:", bat_path)