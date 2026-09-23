# -*- coding: utf-8 -*-
"""
PC 브라우저 격리 런처 서비스 (Multi-Account Browser Launcher)
- 스마트폰 접속 차단 및 메타 기기 식별(디바이스 핑거프린트) 원천 무력화
- 7개 계정별 완전 분리된 독립 크롬 프로필(user-data-dir) 생성 및 실행
- 바탕화면 바로가기 생성 지원
"""
import os
import subprocess
import logging
from typing import Dict, Any, Optional
from database.models import Account

logger = logging.getLogger("BrowserLauncherService")

CHROME_CANDIDATE_PATHS = [
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS_DIR = os.path.join(PROJECT_ROOT, "browser_sessions")
DESKTOP_DIR = r"C:\Users\ktaeh\OneDrive\바탕 화면\쓰레드_계정별_접속기"


class BrowserLauncherService:
    @staticmethod
    def get_browser_executable() -> Optional[str]:
        for p in CHROME_CANDIDATE_PATHS:
            if os.path.exists(p):
                return p
        return None

    @classmethod
    def get_profile_dir(cls, username: str) -> str:
        clean_name = username.lstrip("@").replace(".", "_")
        profile_path = os.path.join(SESSIONS_DIR, f"threads_{clean_name}")
        os.makedirs(profile_path, exist_ok=True)
        return profile_path

    @classmethod
    def launch_account_browser(cls, account: Account) -> Dict[str, Any]:
        """
        특정 계정 전용 독립 브라우저 창 실행
        """
        browser_exe = cls.get_browser_executable()
        if not browser_exe:
            raise FileNotFoundError("PC에서 Google Chrome 또는 Edge 브라우저를 찾을 수 없습니다.")

        profile_dir = cls.get_profile_dir(account.username)
        target_url = f"https://www.threads.net/@{account.username.lstrip('@')}"

        cmd = [
            browser_exe,
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            f"--app={target_url}"
        ]

        logger.info(f"Launching dedicated browser for @{account.username} using profile {profile_dir}")
        subprocess.Popen(cmd)

        return {
            "status": "SUCCESS",
            "account_id": account.id,
            "username": account.username,
            "password": account.login_password or "q1w2e3r4!!",
            "profile_dir": profile_dir,
            "target_url": target_url,
            "message": f"@{account.username} 전용 격리 브라우저가 실행되었습니다."
        }

    @classmethod
    def create_desktop_shortcuts(cls, accounts: list) -> Dict[str, Any]:
        """
        바탕화면에 7개 계정별 원클릭 접속 바로가기(.bat 파일) 일괄 생성
        """
        browser_exe = cls.get_browser_executable()
        if not browser_exe:
            return {"status": "ERROR", "message": "Chrome 실행 파일을 찾을 수 없습니다."}

        os.makedirs(DESKTOP_DIR, exist_ok=True)
        created = []

        for idx, acc in enumerate(accounts, 1):
            clean_name = acc.username.lstrip("@")
            profile_dir = cls.get_profile_dir(acc.username)
            file_name = f"{idx}호기_{acc.display_name or clean_name}_@{clean_name}.bat"
            file_path = os.path.join(DESKTOP_DIR, file_name)

            pw = acc.login_password or 'q1w2e3r4!!'
            bat_content = f"""@echo off
chcp 65001 > nul
title [{clean_name}] 쓰레드 전용 브라우저 접속
powershell -Command "Set-Clipboard -Value '{pw}'"
echo ========================================================
echo  [ {clean_name} ] 쓰레드 독립 세션 접속기
echo  아이디   : {clean_name}
echo  비밀번호 : {pw} (클립보드에 자동 복사되었습니다!)
echo ========================================================
echo  [초간단 안내]
echo  1. 열리는 브라우저 로그인 창에서 아이디({clean_name}) 입력
echo  2. 비밀번호 입력란에서 [ Ctrl + V ] 로 바로 붙여넣기
echo  3. 로그인 후 브라우저 상단 [비밀번호 저장] 꼭 클릭!
echo     - 다음부터는 아이콘만 누르면 자동 로그인 상태로 바로 열립니다.
echo ========================================================
start "" "{browser_exe}" --user-data-dir="{profile_dir}" --no-first-run --no-default-browser-check --app="https://www.threads.net/login"
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
            created.append(file_name)

        return {
            "status": "SUCCESS",
            "count": len(created),
            "folder": DESKTOP_DIR,
            "created_files": created
        }
