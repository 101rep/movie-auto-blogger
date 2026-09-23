@echo off
chcp 65001 > nul
title AI Shorts Remixer Studio
cd /d "%~dp006_AI_Shorts_Remixer"
echo ========================================================
echo        AI 쇼츠 리믹스 & 로컬라이징 스튜디오 가동
echo ========================================================
python gui.py
pause
