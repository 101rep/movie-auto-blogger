import os
import glob
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from adapters.base import BaseProgramAdapter, ProgramStatus

class ShortsRemixerAdapter(BaseProgramAdapter):
    """Adapter for 06_AI_Shorts_Remixer system."""

    @property
    def name(self) -> str:
        return "shorts_remixer"

    @property
    def description(self) -> str:
        return "AI 쇼츠 리믹서 & 로컬라이징 엔진 (15초 숏폼 지능형 컷편집, ElevenLabs TTS, 다이내믹 모션)"

    def __init__(self):
        # Determine base directory
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspace_root = os.path.abspath(os.path.join(cur_dir, "..", ".."))
        self.remixer_dir = os.path.join(self.workspace_root, "06_AI_Shorts_Remixer")
        self.analysis_dir = os.path.join(self.workspace_root, "분석실")
        self.completed_dir = os.path.join(self.analysis_dir, "분석실완료")
        self.output_shorts_dir = os.path.join(self.remixer_dir, "output_shorts")

    async def get_status(self) -> ProgramStatus:
        def _inspect():
            raw_inputs = glob.glob(os.path.join(self.analysis_dir, "*.mp4")) if os.path.exists(self.analysis_dir) else []
            completed_files = []
            if os.path.exists(self.completed_dir):
                completed_files.extend(glob.glob(os.path.join(self.completed_dir, "*.mp4")))
            if os.path.exists(self.output_shorts_dir):
                completed_files.extend(glob.glob(os.path.join(self.output_shorts_dir, "*.mp4")))

            completed_files = sorted(list(set(completed_files)), key=lambda x: os.path.getmtime(x), reverse=True)

            recent_list = []
            total_mb = 0.0
            for f in completed_files[:5]:
                sz = os.path.getsize(f) / (1024 * 1024)
                total_mb += sz
                mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
                recent_list.append({
                    "filename": os.path.basename(f),
                    "size_mb": round(sz, 2),
                    "created": mtime
                })

            return {
                "raw_inputs_count": len(raw_inputs),
                "completed_shorts_count": len(completed_files),
                "recent_completed": recent_list,
                "remixer_ready": os.path.exists(self.remixer_dir)
            }

        details = await asyncio.to_thread(_inspect)
        return ProgramStatus(
            name=self.name,
            is_running=details.get("remixer_ready", False),
            version="1.0.0",
            details=details,
            last_check=datetime.now()
        )

    async def health_check(self) -> bool:
        if os.name == "posix":
            return True
        return os.path.exists(self.remixer_dir)

    async def get_recent_logs(self, lines: int = 40) -> str:
        status = await self.get_status()
        recent = status.details.get("recent_completed", [])
        raw_cnt = status.details.get("raw_inputs_count", 0)
        out = [
            f"=== AI Shorts Remixer 현황 ===",
            f"분석 대기 원본 영상: {raw_cnt}개",
            f"제작 완료 15초 쇼츠: {status.details.get('completed_shorts_count', 0)}개",
            f"--- 최근 완성 쇼츠 목록 ---"
        ]
        for item in recent:
            out.append(f"• {item['filename']} ({item['size_mb']}MB | {item['created']})")
        return "\n".join(out)

    async def restart(self) -> Dict[str, Any]:
        return {"success": True, "message": "Shorts Remixer Standby Ready"}

    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if action_name == "list_shorts":
            status = await self.get_status()
            return {
                "success": True,
                "completed_count": status.details.get("completed_shorts_count", 0),
                "recent": status.details.get("recent_completed", [])
            }
        return {"success": False, "error": f"Unknown action: {action_name}"}
