import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from config import settings
from adapters.base import BaseProgramAdapter, ProgramStatus

class MultisiteBloggerAdapter(BaseProgramAdapter):
    """Adapter for the 8-Blog Automated Scheduling and Publishing System."""

    @property
    def name(self) -> str:
        return "multisite_blogger"

    @property
    def description(self) -> str:
        return "8대 워드프레스 블로그 통합 자동 예약 및 발행 시스템 (트래블픽24, 트렌드스팟24, 아이템픽24 등)"

    def _get_active_url(self) -> str:
        import os
        # On Cloudways server, port 8000 is localhost only (external IP is firewalled)
        if os.path.exists("/home/master"):
            return settings.BLOGGER_LOCAL_URL
        return settings.BLOGGER_LOCAL_URL

    async def get_status(self) -> ProgramStatus:
        target_url = self._get_active_url()
        is_healthy = False
        health_data = {}
        
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                res = await client.get(f"{target_url}/health")
                if res.status_code == 200:
                    health_data = res.json()
                    is_healthy = health_data.get("status") == "healthy"
            except Exception:
                # Try fallback local
                try:
                    res_local = await client.get(f"{settings.BLOGGER_LOCAL_URL}/health")
                    if res_local.status_code == 200:
                        health_data = res_local.json()
                        is_healthy = True
                        target_url = settings.BLOGGER_LOCAL_URL
                except Exception:
                    is_healthy = False

        if not is_healthy:
            # Fallback to SSH probe (works from external desktop when Cloudways firewall blocks port 8000)
            try:
                from adapters.cloudways import CloudwaysServerAdapter
                import json
                cw = CloudwaysServerAdapter()
                def _probe_ssh():
                    ssh = cw._get_ssh_client()
                    try:
                        stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8000/health", timeout=3)
                        out = stdout.read().decode('utf-8', errors='ignore').strip()
                        return json.loads(out)
                    finally:
                        ssh.close()
                ssh_data = await asyncio.to_thread(_probe_ssh)
                if ssh_data.get("status") == "healthy":
                    is_healthy = True
                    target_url = settings.BLOGGER_REMOTE_URL
                    health_data = ssh_data
            except Exception:
                pass

        return ProgramStatus(
            name=self.name,
            is_running=is_healthy,
            url=target_url,
            port=8000,
            version=health_data.get("version", "2.0.0"),
            details={
                "target_url": target_url,
                "timezone": health_data.get("timezone", "Asia/Seoul"),
                "scheduler_status": health_data.get("scheduler", {}).get("status", "unknown"),
                "jobs_count": health_data.get("scheduler", {}).get("jobs_count", 0),
                "managed_blogs": [
                    "travelpick24.com (여행)",
                    "trendspot24.com (영화)",
                    "item.travelpick24.com (상품리뷰)",
                    "enter.trendspot24.com (연예/K-콘텐츠)",
                    "welfare23.travelpick24.com (청년복지)",
                    "welfare24.travelpick24.com (시니어복지)",
                    "welfare25.travelpick24.com (지원금가이드)",
                    "news.trendspot24.com (뉴스픽24)"
                ]
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
        # Query remote server via Cloudways adapter or read local
        try:
            from adapters.cloudways import CloudwaysServerAdapter
            cw = CloudwaysServerAdapter()
            return await cw.get_recent_logs(lines)
        except Exception as e:
            return f"로그 조회 실패: {e}"

    async def restart(self) -> Dict[str, Any]:
        from adapters.cloudways import CloudwaysServerAdapter
        cw = CloudwaysServerAdapter()
        return await cw.trigger_action("restart_service", {"service": "blogger"})

    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        target_url = self._get_active_url()
        
        if action_name in ("trigger_all", "trigger_publish"):
            vertical = params.get("vertical", "ALL")
            force = params.get("force", True)
            post_count = params.get("post_count", 1)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    payload = {"vertical": vertical, "force": force, "post_count": post_count}
                    res = await client.post(f"{target_url}/api/trigger-automation", json=payload)
                    return {"success": res.status_code == 200, "data": res.json()}
                except Exception as e:
                    return {"success": False, "error": str(e)}

        elif action_name == "get_recent_posts":
            try:
                import sqlite3
                import os
                db_candidates = [
                    "/home/master/multisite_auto_blogger/data/movie_blogger.db",
                    r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\02_Movie_Auto_Blogger\data\movie_blogger.db"
                ]
                db_path = next((p for p in db_candidates if os.path.exists(p)), None)
                if db_path:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT id, site_id, title, status, scheduled_at, wordpress_url, created_at FROM posts ORDER BY id DESC LIMIT 10")
                    rows = cur.fetchall()
                    conn.close()
                    posts = [
                        {"id": r[0], "site_id": r[1], "title": r[2], "status": r[3], "scheduled_at": r[4], "url": r[5]}
                        for r in rows
                    ]
                    return {"success": True, "posts": posts}
                return {"success": True, "posts": []}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif action_name in ("manage_posts", "manage_blog_posts"):
            from adapters.blog_post_manager import manage_blog_posts
            action = params.get("action", "check_duplicates")
            site_id = int(params.get("site_id", 2))
            post_id = params.get("post_id")
            if post_id is not None:
                post_id = int(post_id)
            keyword = params.get("keyword")
            return await manage_blog_posts(action=action, site_id=site_id, post_id=post_id, keyword=keyword)

        elif action_name in ("fix_posters", "fix_blog_post_poster"):
            from adapters.blog_post_manager import fix_blog_post_poster
            site_id = int(params.get("site_id", 2))
            post_id = params.get("post_id")
            if post_id is not None:
                post_id = int(post_id)
            movie_title = params.get("movie_title")
            return await fix_blog_post_poster(site_id=site_id, post_id=post_id, movie_title=movie_title)

        return {"success": False, "error": f"Unknown action: {action_name}"}

