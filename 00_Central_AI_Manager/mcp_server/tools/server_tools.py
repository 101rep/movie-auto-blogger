# -*- coding: utf-8 -*-
"""
Server Health & Operations MCP Tools (Level 1)
"""

import sys
import logging
from typing import Dict, Any
from adapters.registry import registry
from monitor.ops_monitor import ops_center
from mcp_server.auth import auth_guard, PermissionLevel

logger = logging.getLogger("MCPServerTools")

async def get_server_health(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 1: Read] Cloudways 리눅스 서버의 CPU, RAM, 디스크 용량, 핵심 데몬 프로세스 상태를 종합 조회합니다.
    """
    guard = auth_guard.enforce_guard("server_health", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        raw_metrics = await ops_center.get_total_status_report()
        # Direct metrics lookup via cloudways adapter
        cw = registry.get("cloudways_server")
        status_data = {}
        if cw:
            res = await cw.get_status()
            if hasattr(res, "metrics"):
                status_data = res.metrics
            elif isinstance(res, dict):
                status_data = res
        
        return {
            "status": "SUCCESS",
            "server_ip": "139.59.125.237",
            "os": "Linux Cloudways Ubuntu",
            "metrics": status_data,
            "summary_text": raw_metrics
        }
    except Exception as e:
        logger.error(f"server_health error: {e}")
        return {
            "status": "ERROR",
            "message": str(e)
        }
