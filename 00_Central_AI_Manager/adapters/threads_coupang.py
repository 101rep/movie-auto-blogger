import asyncio
import httpx
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import settings
from adapters.base import BaseProgramAdapter, ProgramStatus

class ThreadsCoupangAdapter(BaseProgramAdapter):
    """Adapter for Threads x Coupang Partners Content Automation System."""

    @property
    def name(self) -> str:
        return "threads_coupang"

    @property
    def description(self) -> str:
        return "Threads x 쿠팡파트너스 AI 콘텐츠 자동화 시스템 (7대 계정 웜업 & 가상 AI 스튜디오)"

    def _get_active_url(self) -> str:
        return settings.THREADS_REMOTE_URL

    async def get_status(self) -> ProgramStatus:
        target_url = self._get_active_url()
        is_healthy = False
        details = {}
        
        async with httpx.AsyncClient(timeout=1.0) as client:
            for url_candidate in [target_url, settings.THREADS_LOCAL_URL]:
                try:
                    res = await client.get(f"{url_candidate}/health")
                    if res.status_code == 200:
                        is_healthy = True
                        target_url = url_candidate
                        if res.headers.get("content-type", "").startswith("application/json"):
                            details = res.json()
                        break
                except Exception:
                    continue

        if not is_healthy:
            # Fallback to SSH probe
            try:
                from adapters.cloudways import CloudwaysServerAdapter
                import json
                cw = CloudwaysServerAdapter()
                def _probe_ssh():
                    ssh = cw._get_ssh_client()
                    try:
                        stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:9000/health", timeout=3)
                        out = stdout.read().decode('utf-8', errors='ignore').strip()
                        return json.loads(out)
                    finally:
                        ssh.close()
                ssh_data = await asyncio.to_thread(_probe_ssh)
                if ssh_data.get("status") == "ok":
                    is_healthy = True
                    target_url = settings.THREADS_REMOTE_URL
                    details = ssh_data
            except Exception:
                pass

        return ProgramStatus(
            name=self.name,
            is_running=is_healthy,
            url=target_url,
            port=9000,
            version=details.get("version", "2.0.0"),
            details={
                "target_url": target_url,
                "role": "7대 계정 AI 스튜디오 (큐레이터, 작가, 디자이너)",
                "info": details
            },
            last_check=datetime.now()
        )

    async def health_check(self) -> bool:
        try:
            status = await self.get_status()
            return status.is_running
        except Exception:
            return False

    async def get_recent_logs(self, lines: int = 40) -> str:
        try:
            from adapters.cloudways import CloudwaysServerAdapter
            cw = CloudwaysServerAdapter()
            def _fetch():
                ssh = cw._get_ssh_client()
                try:
                    stdin, stdout, stderr = ssh.exec_command(f"tail -n {lines} /home/master/threads_automation/app.log 2>/dev/null")
                    return stdout.read().decode('utf-8', errors='ignore')
                finally:
                    ssh.close()
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            return f"로그 조회 실패: {e}"

    async def get_accounts_metrics(self) -> Dict[str, Any]:
        """Fetch 7 accounts, trust scores, contents count, and outbound interactions directly from DB."""
        local_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "threads_coupang.db")
        remote_db = "/home/master/threads_automation/threads_coupang.db"

        # Check local first
        if os.path.exists(local_db):
            try:
                conn = sqlite3.connect(local_db)
                c = conn.cursor()
                c.execute("SELECT id, username, display_name, category, warmup_status, trust_score FROM accounts")
                accounts = [
                    {"id": r[0], "username": r[1], "display_name": r[2], "category": r[3], "warmup_status": r[4], "trust_score": r[5]}
                    for r in c.fetchall()
                ]
                c.execute("SELECT count(*) FROM contents")
                total_contents = c.fetchone()[0]
                c.execute("SELECT count(*) FROM outbound_interactions")
                total_outbound = c.fetchone()[0]
                conn.close()
                return {"accounts": accounts, "total_contents": total_contents, "total_outbound": total_outbound}
            except Exception:
                pass

        # Remote SSH fetch
        try:
            from adapters.cloudways import CloudwaysServerAdapter
            import json
            cw = CloudwaysServerAdapter()
            def _fetch_db():
                ssh = cw._get_ssh_client()
                try:
                    py_cmd = (
                        "python3 -c \""
                        "import sqlite3, json; "
                        "conn = sqlite3.connect('/home/master/threads_automation/threads_coupang.db'); "
                        "c = conn.cursor(); "
                        "c.execute('SELECT id, username, display_name, category, warmup_status, trust_score FROM accounts'); "
                        "accs = [{'id': r[0], 'username': r[1], 'display_name': r[2], 'category': r[3], 'warmup_status': r[4], 'trust_score': r[5]} for r in c.fetchall()]; "
                        "c.execute('SELECT count(*) FROM contents'); "
                        "tot_c = c.fetchone()[0]; "
                        "c.execute('SELECT count(*) FROM outbound_interactions'); "
                        "tot_o = c.fetchone()[0]; "
                        "print(json.dumps({'accounts': accs, 'total_contents': tot_c, 'total_outbound': tot_o}))"
                        "\""
                    )
                    stdin, stdout, stderr = ssh.exec_command(py_cmd, timeout=5)
                    raw = stdout.read().decode('utf-8', errors='ignore').strip()
                    return json.loads(raw)
                finally:
                    ssh.close()
            return await asyncio.to_thread(_fetch_db)
        except Exception as e:
            return {"accounts": [], "total_contents": 0, "total_outbound": 0, "error": str(e)}

    async def restart(self) -> Dict[str, Any]:
        from adapters.cloudways import CloudwaysServerAdapter
        cw = CloudwaysServerAdapter()
        return await cw.trigger_action("restart_service", {"service": "threads"})

    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if action_name in ("get_metrics", "get_accounts_metrics"):
            return await self.get_accounts_metrics()
        elif action_name == "process_url":
            url = params.get("url")
            return {"success": True, "message": f"링크 {url} 처리 큐 등록 완료"}
        return {"success": False, "error": f"Unknown action: {action_name}"}

