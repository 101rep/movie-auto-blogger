# -*- coding: utf-8 -*-
"""
Threads x Coupang Automation MCP Tools (Level 1 & Level 3)
"""

import logging
from typing import Dict, Any
from adapters.registry import registry
from monitor.ops_monitor import ops_center
from mcp_server.auth import auth_guard, PermissionLevel

logger = logging.getLogger("MCPThreadsTools")

async def get_threads_status(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 1: Read] Threads 7대 계정 가동 현황, 신뢰도(Trust Score), 오늘 작성된 게시물 수, 아웃바운드 소통(좋아요/댓글) 활동 내역을 조회합니다.
    """
    guard = auth_guard.enforce_guard("threads_status", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        summary = await ops_center.get_threads_daily_summary()
        report_text = ops_center.format_threads_telegram_report(summary)
        
        return {
            "status": "SUCCESS",
            "accounts_count": summary.get("accounts_count", 7),
            "total_today_posts": summary.get("total_today_posts", 0),
            "total_today_interactions": summary.get("total_today_interactions", 0),
            "accounts": summary.get("accounts", []),
            "report_text": report_text
        }
    except Exception as e:
        logger.error(f"threads_status error: {e}")
        return {"status": "ERROR", "message": str(e)}

async def trigger_threads_warmup(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 3: Publish] Threads 7대 계정의 아웃바운드 웜업 및 소통 활동(중복 방지 & 7일 쿨다운 기반)을 즉시 1회 실행합니다.
    """
    guard = auth_guard.enforce_guard("trigger_threads_warmup", PermissionLevel.PUBLISH, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        threads_adapter = registry.get("threads_coupang")
        if not threads_adapter:
            return {"status": "ERROR", "message": "threads_coupang 어댑터가 로드되지 않았습니다."}
            
        res = threads_adapter.trigger_warmup_cycle()
        return {
            "status": "SUCCESS",
            "message": "Threads 7대 계정 웜업 소통 사이클 실행 완료",
            "result": res
        }
    except Exception as e:
        logger.error(f"trigger_threads_warmup error: {e}")
        return {"status": "ERROR", "message": str(e)}
