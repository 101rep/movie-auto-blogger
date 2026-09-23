# -*- coding: utf-8 -*-
"""
WordPress Multi-Site Blog MCP Tools (Level 1 & Level 3)
"""

import logging
from typing import Dict, Any, Optional
from adapters.registry import registry
from monitor.ops_monitor import ops_center
from mcp_server.auth import auth_guard, PermissionLevel

logger = logging.getLogger("MCPBlogTools")

async def get_blog_status(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 1: Read] 8대 WordPress 블로그 가동 상태, 최근 발행 성공 수, 예약 대기 포스팅 목록을 조회합니다.
    """
    guard = auth_guard.enforce_guard("blog_status", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        summary = await ops_center.get_wordpress_daily_summary()
        report_text = ops_center.format_wordpress_telegram_report(summary)
        
        return {
            "status": "SUCCESS",
            "sites_count": len(summary.get("sites", [])),
            "total_today_posts": summary.get("total_today_posts", 0),
            "recent_posts": summary.get("recent_posts", [])[:10],
            "report_text": report_text
        }
    except Exception as e:
        logger.error(f"blog_status error: {e}")
        return {"status": "ERROR", "message": str(e)}

async def publish_content(vertical: str = "ALL", post_count: int = 1, auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 3: Publish] 지정한 버티컬(ALL, MOVIE, TRAVEL, PRODUCT, ENTERTAINMENT, WELFARE, NEWS)의 AI 글 작성 및 워드프레스 발행을 즉시 1회 트리거합니다.
    """
    guard = auth_guard.enforce_guard("publish_content", PermissionLevel.PUBLISH, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        blogger = registry.get("multisite_blogger")
        if not blogger:
            return {"status": "ERROR", "message": "multisite_blogger 어댑터가 로드되지 않았습니다."}
            
        res = blogger.trigger_daily_job(vertical=vertical, count=post_count)
        return {
            "status": "SUCCESS",
            "vertical": vertical,
            "post_count": post_count,
            "result": res
        }
    except Exception as e:
        logger.error(f"publish_content error: {e}")
        return {"status": "ERROR", "message": str(e)}

async def run_wp_cron(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 2: Ops] 8대 워드프레스의 예약 글이 정시에 발행되도록 Cloudways 서버의 WP-Cron 일괄 처리 스크립트를 즉시 실행합니다.
    """
    guard = auth_guard.enforce_guard("run_wp_cron", PermissionLevel.OPS, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        cw = registry.get("cloudways_server")
        if not cw:
            return {"status": "ERROR", "message": "cloudways_server 어댑터가 로드되지 않았습니다."}
            
        res = cw.execute_safe_command("/home/master/run_wp_cron_all.sh")
        return {
            "status": "SUCCESS",
            "message": "Cloudways 8대 블로그 WP-Cron 실행 완료",
            "output": res.get("output", "")
        }
    except Exception as e:
        logger.error(f"run_wp_cron error: {e}")
        return {"status": "ERROR", "message": str(e)}
