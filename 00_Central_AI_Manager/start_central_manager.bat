@echo off
chcp 65001 > nul
title [Antigravity] Central AI Manager Control Center
cd /d "%~dp0"

echo ======================================================================
echo   🚀 Antigravity Central AI Manager 관제 센터를 가동합니다...
echo ======================================================================
echo.

python desktop_controller.py

pause
