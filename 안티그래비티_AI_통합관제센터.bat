@echo off
chcp 65001 > nul
title [Antigravity] Central AI Manager Control Center
cd /d "%~dp0\00_Central_AI_Manager"

python desktop_controller.py

pause
