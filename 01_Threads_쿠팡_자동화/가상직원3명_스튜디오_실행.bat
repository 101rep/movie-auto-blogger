@echo off
chcp 65001 > nul
title 가상직원 3명 AI 콘텐츠 스튜디오
echo ============================================================
echo [가상의 직원 3명 스튜디오] 자율 파이프라인 시작
echo 직원 1: trend_curator (트렌드/결핍 큐레이터)
echo 직원 2: story_writer  (인스타툰/카드뉴스 스토리 작가)
echo 직원 3: visual_designer (HTML5 4K 비주얼 디자이너)
echo ============================================================
echo.
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0..\02_Movie_Auto_Blogger\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
"%PYTHON_EXE%" scripts/run_virtual_studio.py --product_id 11 --type both
echo.
echo ============================================================
echo [완료] 제작된 결과물은 [05_결과물_및_문서] 폴더에서 확인 가능합니다!
echo ============================================================
pause
