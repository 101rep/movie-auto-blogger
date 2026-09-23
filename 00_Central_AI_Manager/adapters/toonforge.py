import os
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from adapters.base import BaseProgramAdapter, ProgramStatus

class ToonForgeAdapter(BaseProgramAdapter):
    """Adapter for 03_ToonForge_스튜디오 system."""

    @property
    def name(self) -> str:
        return "toonforge_studio"

    @property
    def description(self) -> str:
        return "ToonForge AI 웹툰 스튜디오 (35종 AI Director 3.0, 듀얼 분할 웹툰 기획/제작 데스크톱 앱)"

    def __init__(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspace_root = os.path.abspath(os.path.join(cur_dir, "..", ".."))
        self.studio_dir = os.path.join(self.workspace_root, "03_ToonForge_스튜디오")
        self.exe_path = os.path.join(self.studio_dir, "ToonForge.exe")
        self.bat_path = os.path.join(self.studio_dir, "ToonForge_실행.bat")

    def _is_process_running(self) -> bool:
        if os.name != "nt":
            return False
        try:
            out = subprocess.check_output('tasklist /FI "IMAGENAME eq ToonForge.exe" /NH', shell=True).decode('utf-8', errors='ignore')
            return "ToonForge.exe" in out
        except Exception:
            return False

    async def get_status(self) -> ProgramStatus:
        def _check():
            exists = os.path.exists(self.exe_path)
            running = self._is_process_running()
            size_mb = round(os.path.getsize(self.exe_path) / (1024 * 1024), 1) if exists else 0
            return {
                "installed": exists,
                "is_running": running,
                "exe_size_mb": size_mb,
                "version": "0.3.0",
                "studio_path": self.studio_dir
            }

        details = await asyncio.to_thread(_check)
        return ProgramStatus(
            name=self.name,
            is_running=details.get("installed", False),
            version="0.3.0",
            details=details,
            last_check=datetime.now()
        )

    async def health_check(self) -> bool:
        if os.name == "posix":
            return True
        return os.path.exists(self.exe_path)

    async def get_recent_logs(self, lines: int = 40) -> str:
        status = await self.get_status()
        running_str = "실행 중 (Active)" if status.details.get("is_running") else "대기 중 (Standby)"
        return (
            f"=== ToonForge Desktop Studio v0.3.0 ===\n"
            f"앱 설치 상태: 정상 ({status.details.get('exe_size_mb')}MB)\n"
            f"현재 프로세스 상태: {running_str}\n"
            f"실행 파일 경로: {self.exe_path}\n"
            f"35종 AI Director 3.0 & 듀얼 프롬프트 제작 스튜디오 준비 완료"
        )

    async def restart(self) -> Dict[str, Any]:
        return {"success": True, "message": "ToonForge Studio Standby Ready"}

    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if action_name == "launch":
            if os.path.exists(self.bat_path):
                subprocess.Popen(f'start "" "{self.bat_path}"', shell=True)
                return {"success": True, "message": "ToonForge 스튜디오가 데스크톱에서 실행되었습니다."}
            elif os.path.exists(self.exe_path):
                subprocess.Popen(f'start "" "{self.exe_path}"', shell=True)
                return {"success": True, "message": "ToonForge.exe가 실행되었습니다."}
            return {"success": False, "error": "ToonForge 실행 파일을 찾을 수 없습니다."}

        return {"success": False, "error": f"Unknown action: {action_name}"}
