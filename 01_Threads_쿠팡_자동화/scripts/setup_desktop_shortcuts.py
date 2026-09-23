import os
import sys
import subprocess

# Ensure UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

desktop_dir = r"C:\Users\ktaeh\OneDrive\바탕 화면"
antigravity_dir = r"C:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티"
movie_dir = os.path.join(antigravity_dir, "movie-auto-blogger")
toon_dir = os.path.join(antigravity_dir, "ToonForge_Desktop_Windows")
company_dir = r"C:\Users\ktaeh\OneDrive\바탕 화면\앱_개발_마스터회사"
threads_accounts_dir = r"C:\Users\ktaeh\OneDrive\바탕 화면\쓰레드_계정별_접속기"
instagram_dir = r"C:\Users\ktaeh\OneDrive\바탕 화면\InstagramAI"

print("1. 보조 런처 파일 생성 및 업데이트 중...")

# 1-1. InstagramAI run_app.bat
insta_bat_path = os.path.join(instagram_dir, "run_app.bat")
insta_bat_content = """@echo off
chcp 65001 > nul
title Instagram AI Viral Localization Toolkit
echo ========================================================
echo   📸 Instagram AI Viral Localization Toolkit 실행 중...
echo   브라우저가 자동으로 열립니다 (http://localhost:8501)
echo ========================================================
cd /d "%~dp0"
python -m streamlit run app.py
pause
"""
with open(insta_bat_path, "w", encoding="utf-8") as f:
    f.write(insta_bat_content)
print(f"  ✓ 생성 완료: {insta_bat_path}")

# 1-2. 쓰레드 통합 계정접속기.bat
threads_master_bat = os.path.join(threads_accounts_dir, "통합_계정접속기.bat")
threads_master_content = """@echo off
chcp 65001 > nul
title 쓰레드(Threads) 7개 계정 원클릭 통합 접속기
:MENU
cls
echo ========================================================
echo   🧵 Threads 부계정 1초 원클릭 자동 접속기
echo   (각 계정별 독립 세션 쿠키가 완벽히 보존됩니다)
echo ========================================================
echo.
echo   [1] 1호기: IT 테크 큐레이터 (@kth.101rep)
echo   [2] 2호기: 툰툰이의 귀여운 꿀템 (@toontoooon)
echo   [3] 3호기: 룩앳미 AI 뷰티&트렌드 (@lookatmeai)
echo   [4] 4호기: 태치튜브 감성 라이프 (@taechi.tube)
echo   [5] 5호기: 호구탈출 가성비 핫딜 (@101rep80)
echo   [6] 6호기: 살림로그 스마트 리빙 (@yr170425)
echo   [7] 7호기: 30대 직장인의 현실생존 (@ktaehoon80)
echo.
echo   [A] 계정 접속기 폴더 열기
echo   [Q] 종료
echo ========================================================
set /p choice="접속할 번호를 입력하세요 (1~7, A, Q): "

if "%choice%"=="1" (
    call "%~dp01호기_IT 테크 큐레이터_@kth.101rep.bat"
    goto MENU
)
if "%choice%"=="2" (
    call "%~dp02호기_툰툰이의 귀여운 꿀템_@toontoooon.bat"
    goto MENU
)
if "%choice%"=="3" (
    call "%~dp03호기_룩앳미 AI 뷰티&트렌드_@lookatmeai.bat"
    goto MENU
)
if "%choice%"=="4" (
    call "%~dp04호기_태치튜브 감성 라이프_@taechi.tube.bat"
    goto MENU
)
if "%choice%"=="5" (
    call "%~dp05호기_호구탈출 가성비 핫딜_@101rep80.bat"
    goto MENU
)
if "%choice%"=="6" (
    call "%~dp06호기_살림로그 스마트 리빙_@yr170425.bat"
    goto MENU
)
if "%choice%"=="7" (
    call "%~dp07호기_30대 직장인의 현실생존_@ktaehoon80.bat"
    goto MENU
)
if /i "%choice%"=="A" (
    start "" "%~dp0"
    goto MENU
)
if /i "%choice%"=="Q" exit
goto MENU
"""
with open(threads_master_bat, "w", encoding="utf-8") as f:
    f.write(threads_master_content)
print(f"  ✓ 생성 완료: {threads_master_bat}")

# 1-3. 앱_개발_마스터회사 START_SERVER.bat 개선
company_bat = os.path.join(company_dir, "START_SERVER.bat")
company_bat_content = """@echo off
chcp 65001 > nul
title AI Company OS - Autonomous AI Software Company
echo ========================================================
echo   ⚡ AI Company OS (가상 AI 소프트웨어 개발사)
echo ========================================================
echo   서버를 시작하고 대시보드를 엽니다...
echo   접속 주소: http://localhost:3000
echo ========================================================
cd /d "%~dp0backend"
start "" "http://localhost:3000"
python -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
pause
"""
with open(company_bat, "w", encoding="utf-8") as f:
    f.write(company_bat_content)
print(f"  ✓ 갱신 완료: {company_bat}")

print("\n2. 바탕화면 바로가기(.lnk) 생성 및 아이콘 매핑 중...")

# Shortcut definitions:
# (Name, TargetPath, WorkingDir, IconLocation, Description)
shortcuts = [
    (
        "Threads x 쿠팡 자동화.lnk",
        os.path.join(antigravity_dir, "start_threads_automation.bat"),
        antigravity_dir,
        "shell32.dll,220",
        "Threads x 쿠팡파트너스 AI 자동화 시스템 (Port 8080)"
    ),
    (
        "Movie Auto Blogger.lnk",
        os.path.join(movie_dir, "start_app.bat"),
        movie_dir,
        "imageres.dll,67",
        "무비 오토 블로거 관리자 대시보드 (Port 8000)"
    ),
    (
        "ToonForge 스튜디오.lnk",
        os.path.join(toon_dir, "ToonForge.exe"),
        toon_dir,
        f"{os.path.join(toon_dir, 'ToonForge.exe')},0",
        "ToonForge Desktop Studio v2.0 (인스타툰 & 카드뉴스 제작기)"
    ),
    (
        "멍당근 펫케어 앱.lnk",
        os.path.join(antigravity_dir, "펫케어_앱_실행하기.bat"),
        antigravity_dir,
        "imageres.dll,102",
        "멍당근 펫케어 & 나눔 마켓 모바일 웹앱 (Port 8088)"
    ),
    (
        "가상직원 3명 AI 스튜디오.lnk",
        os.path.join(antigravity_dir, "가상직원3명_스튜디오_실행.bat"),
        antigravity_dir,
        "imageres.dll,26",
        "가상직원 3명(큐레이터/스토리작가/디자이너) 자율 파이프라인"
    ),
    (
        "텔레그램 링크 배달원.lnk",
        os.path.join(antigravity_dir, "텔레그램_중간직원_실행.bat"),
        antigravity_dir,
        r"C:\Users\ktaeh\AppData\Roaming\Telegram Desktop\Telegram.exe,0",
        "텔레그램 쇼핑 링크 실시간 감지 및 자동 제작 쿠리어 봇"
    ),
    (
        "AI 앱개발 마스터회사.lnk",
        os.path.join(company_dir, "START_SERVER.bat"),
        company_dir,
        "imageres.dll,114",
        "AI Company OS - 자율 소프트웨어 개발사 (Port 3000)"
    ),
    (
        "쓰레드 7개 계정 원클릭 접속기.lnk",
        threads_master_bat,
        threads_accounts_dir,
        "shell32.dll,15",
        "Threads 7개 부계정 독립 세션 원클릭 자동 접속기"
    ),
    (
        "Instagram AI 떡상 탐색기.lnk",
        insta_bat_path,
        instagram_dir,
        "imageres.dll,109",
        "Instagram AI Viral Localization Toolkit"
    ),
    (
        "Cloudways 서버 원클릭 동기화.lnk",
        os.path.join(antigravity_dir, "서버_원클릭_동기화.bat"),
        antigravity_dir,
        "shell32.dll,146",
        "Cloudways 운영 서버 최신 코드 및 DB 원클릭 동기화"
    ),
]

# Create shortcuts using PowerShell COM object
ps_script_lines = [
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
    "$ws = New-Object -ComObject WScript.Shell"
]

for name, target, workdir, icon, desc in shortcuts:
    link_path = os.path.join(desktop_dir, name)
    ps_script_lines.append(f'$s = $ws.CreateShortcut("{link_path}")')
    ps_script_lines.append(f'$s.TargetPath = "{target}"')
    ps_script_lines.append(f'$s.WorkingDirectory = "{workdir}"')
    if icon:
        ps_script_lines.append(f'$s.IconLocation = "{icon}"')
    ps_script_lines.append(f'$s.Description = "{desc}"')
    ps_script_lines.append('$s.Save()')
    ps_script_lines.append(f'Write-Host "  ✓ 바로가기 생성 완료: {name}"')

ps_script_content = "\n".join(ps_script_lines)
ps_temp_file = os.path.join(antigravity_dir, "scratch", "create_shortcuts.ps1")
os.makedirs(os.path.dirname(ps_temp_file), exist_ok=True)
with open(ps_temp_file, "w", encoding="utf-8") as f:
    f.write(ps_script_content)

res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_temp_file], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
if res.stderr:
    print("Errors:", res.stderr)

print("\n전체 바로가기 생성 및 아이콘 세팅이 완료되었습니다!")
