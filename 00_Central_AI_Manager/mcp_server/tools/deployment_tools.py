# -*- coding: utf-8 -*-
"""
Deployment & Worker Operations MCP Tools (Level 2)
"""

import logging
from typing import Dict, Any
from adapters.registry import registry
from mcp_server.auth import auth_guard, PermissionLevel

logger = logging.getLogger("MCPDeploymentTools")

async def restart_worker(service_name: str, auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 2: Ops] Cloudways 서버의 백그라운드 워커 서비스('blogger', 'threads', 또는 'all')를 안전하게 재시작합니다.
    """
    guard = auth_guard.enforce_guard("restart_worker", PermissionLevel.OPS, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    valid_services = ["blogger", "threads", "all"]
    if service_name.lower() not in valid_services:
        return {
            "status": "ERROR",
            "message": f"유효하지 않은 서비스명입니다. 선택 가능: {valid_services}"
        }

    try:
        cw = registry.get("cloudways_server")
        if not cw:
            return {"status": "ERROR", "message": "cloudways_server 어댑터가 로드되지 않았습니다."}
            
        res = cw.restart_service(service_name.lower())
        return {
            "status": "SUCCESS",
            "target": service_name,
            "message": f"서비스 '{service_name}' 재시작 명령이 안전하게 실행되었습니다.",
            "detail": res
        }
    except Exception as e:
        logger.error(f"restart_worker error: {e}")
        return {"status": "ERROR", "message": str(e)}
