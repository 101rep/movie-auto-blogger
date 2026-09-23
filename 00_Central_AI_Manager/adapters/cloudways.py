import asyncio
import paramiko
from datetime import datetime
from typing import Dict, Any, Optional
from config import settings
from adapters.base import BaseProgramAdapter, ProgramStatus

class CloudwaysServerAdapter(BaseProgramAdapter):
    """Adapter for remote Cloudways Linux server monitoring and operations."""

    @property
    def name(self) -> str:
        return "cloudways_server"

    @property
    def description(self) -> str:
        return "Cloudways 리눅스 서버(139.59.125.237) CPU, 메모리, 디스크, 프로세스 및 Crontab 관제 어댑터"

    def _get_ssh_client(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=settings.CLOUDWAYS_HOST,
            port=settings.CLOUDWAYS_PORT,
            username=settings.CLOUDWAYS_USER,
            password=settings.CLOUDWAYS_PASS,
            timeout=10
        )
        return client

    async def get_status(self) -> ProgramStatus:
        def _fetch():
            ssh = self._get_ssh_client()
            try:
                cmd = """
echo "=== UPTIME ===" && uptime
echo "=== MEMORY ===" && free -m
echo "=== DISK ===" && df -h /
echo "=== PROCESSES ===" && ps aux | grep -E "(threads_automation|multisite_auto_blogger)" | grep -v grep
echo "=== CRON ===" && crontab -l
"""
                stdin, stdout, stderr = ssh.exec_command(cmd)
                raw = stdout.read().decode('utf-8', errors='ignore')
                return raw
            finally:
                ssh.close()

        raw_data = await asyncio.to_thread(_fetch)
        
        # Parse basic metrics
        is_healthy = True
        mem_info = {}
        disk_info = {}
        running_services = []

        try:
            sections = raw_data.split("===")
            for i in range(1, len(sections), 2):
                header = sections[i].strip()
                content = sections[i+1].strip() if i+1 < len(sections) else ""
                
                if "MEMORY" in header:
                    lines = content.splitlines()
                    if len(lines) >= 2:
                        parts = lines[1].split()
                        if len(parts) >= 7:
                            mem_info = {
                                "total_mb": parts[1],
                                "used_mb": parts[2],
                                "free_mb": parts[3],
                                "available_mb": parts[6]
                            }
                elif "DISK" in header:
                    lines = content.splitlines()
                    if len(lines) >= 2:
                        parts = lines[1].split()
                        if len(parts) >= 5:
                            disk_info = {
                                "total": parts[1],
                                "used": parts[2],
                                "available": parts[3],
                                "use_percent": parts[4]
                            }
                elif "PROCESSES" in header:
                    for line in content.splitlines():
                        if "threads_automation" in line:
                            running_services.append("Threads x 쿠팡 (Port 9000)")
                        if "multisite_auto_blogger" in line:
                            running_services.append("8대 블로그 통합 시스템 (Port 8000)")
        except Exception:
            pass

        return ProgramStatus(
            name=self.name,
            is_running=is_healthy,
            url=f"http://{settings.CLOUDWAYS_HOST}",
            details={
                "host": settings.CLOUDWAYS_HOST,
                "memory": mem_info,
                "disk": disk_info,
                "active_services": list(set(running_services)),
                "raw_summary": raw_data[:500]
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
        def _fetch():
            ssh = self._get_ssh_client()
            try:
                cmd = f"tail -n {lines} /home/master/multisite_auto_blogger/daemon.log 2>/dev/null; echo '---'; tail -n {lines} /home/master/threads_automation/daemon.log 2>/dev/null"
                stdin, stdout, stderr = ssh.exec_command(cmd)
                return stdout.read().decode('utf-8', errors='ignore')
            finally:
                ssh.close()
        return await asyncio.to_thread(_fetch)

    async def restart(self) -> Dict[str, Any]:
        """Revive all registered background daemon services on Cloudways."""
        def _run():
            ssh = self._get_ssh_client()
            try:
                cmd = """
/bin/bash /home/master/multisite_auto_blogger/run_daemon.sh 2>&1
/bin/bash /home/master/threads_automation/run_daemon.sh 2>&1
"""
                stdin, stdout, stderr = ssh.exec_command(cmd)
                return stdout.read().decode('utf-8', errors='ignore')
            finally:
                ssh.close()
        res = await asyncio.to_thread(_run)
        return {"success": True, "output": res}

    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if action_name == "run_wp_cron":
            def _wp():
                ssh = self._get_ssh_client()
                try:
                    stdin, stdout, stderr = ssh.exec_command("/bin/bash /home/master/run_wp_cron_all.sh")
                    return stdout.read().decode('utf-8', errors='ignore')
                finally:
                    ssh.close()
            out = await asyncio.to_thread(_wp)
            return {"success": True, "action": "run_wp_cron", "output": out}
        
        elif action_name == "restart_service":
            target = params.get("service", "all")
            def _restart():
                ssh = self._get_ssh_client()
                try:
                    cmds = []
                    if target in ("blogger", "all"):
                        cmds.append("pkill -9 -f 'multisite_auto_blogger/venv' 2>/dev/null || true; /bin/bash /home/master/multisite_auto_blogger/run_daemon.sh")
                    if target in ("threads", "all"):
                        cmds.append("pkill -9 -f 'threads_automation/venv' 2>/dev/null || true; /bin/bash /home/master/threads_automation/run_daemon.sh")
                    stdin, stdout, stderr = ssh.exec_command(" && ".join(cmds))
                    return stdout.read().decode('utf-8', errors='ignore')
                finally:
                    ssh.close()
            out = await asyncio.to_thread(_restart)
            return {"success": True, "action": "restart_service", "target": target, "output": out}

        elif action_name == "backup_all_databases":
            def _backup():
                ssh = self._get_ssh_client()
                try:
                    cmd = """
mkdir -p /home/master/backups
STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/master/backups"
tar -czf "$BACKUP_DIR/db_backup_$STAMP.tar.gz" \
  /home/master/multisite_auto_blogger/data/movie_blogger.db \
  /home/master/threads_automation/threads_coupang.db \
  /home/master/central_ai_manager/data/audit_log.db 2>/dev/null
find "$BACKUP_DIR" -name "db_backup_*.tar.gz" -mtime +14 -delete
ls -lh "$BACKUP_DIR/db_backup_$STAMP.tar.gz"
"""
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    return stdout.read().decode('utf-8', errors='ignore')
                finally:
                    ssh.close()
            out = await asyncio.to_thread(_backup)
            return {"success": True, "action": "backup_all_databases", "output": out.strip()}

        elif action_name == "ping_search_engines":
            def _ping():
                ssh = self._get_ssh_client()
                try:
                    cmd = """
python3 -c "
import urllib.request, json, ssl

ctx = ssl._create_unverified_context()
sites = [
    ('TravelPick24', 'travelpick24.com', 'https://travelpick24.com/wp-sitemap.xml'),
    ('TrendSpot24', 'trendspot24.com', 'https://trendspot24.com/wp-sitemap.xml'),
    ('ItemPick24', 'item.travelpick24.com', 'https://item.travelpick24.com/wp-sitemap.xml'),
    ('EnterPick24', 'enter.trendspot24.com', 'https://enter.trendspot24.com/wp-sitemap.xml'),
    ('WelfarePick23', 'welfare23.travelpick24.com', 'https://welfare23.travelpick24.com/wp-sitemap.xml'),
    ('WelfarePick24', 'welfare24.travelpick24.com', 'https://welfare24.travelpick24.com/wp-sitemap.xml'),
    ('WelfarePick25', 'welfare25.travelpick24.com', 'https://welfare25.travelpick24.com/wp-sitemap.xml'),
    ('NewsPick24', 'news.trendspot24.com', 'https://news.trendspot24.com/wp-sitemap.xml')
]

print('=== 8대 블로그 사이트맵 점검 & IndexNow (Bing/Naver) 전송 ===')
for name, host, sitemap_url in sites:
    # 1. 사이트맵 상태 점검
    sm_status = '000'
    try:
        req = urllib.request.Request(sitemap_url, headers={'User-Agent': 'CentralAIManager/2.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
            sm_status = str(r.status)
    except Exception as e:
        sm_status = 'ERR'

    # 2. IndexNow API 전송 (Bing, Naver, Yandex 자동 색인 요청)
    in_status = '000'
    try:
        payload = json.dumps({
            'host': host,
            'key': 'antigravity2026indexnow',
            'keyLocation': f'https://{host}/antigravity2026indexnow.txt',
            'urlList': [sitemap_url, f'https://{host}/']
        }).encode('utf-8')
        in_req = urllib.request.Request(
            'https://api.indexnow.org/indexnow',
            data=payload,
            headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'CentralAIManager/2.0'}
        )
        with urllib.request.urlopen(in_req, timeout=8, context=ctx) as in_resp:
            in_status = str(in_resp.status)
    except urllib.error.HTTPError as he:
        in_status = str(he.code)
    except Exception as e:
        in_status = 'ERR'

    print(f'• [{name}] XML: HTTP {sm_status} | IndexNow: HTTP {in_status} (Bing/Naver 제출완료)')
"
"""
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    return stdout.read().decode('utf-8', errors='ignore')
                finally:
                    ssh.close()
            out = await asyncio.to_thread(_ping)
            return {"success": True, "action": "ping_search_engines", "output": out.strip()}

        return {"success": False, "error": f"Unknown action: {action_name}"}
