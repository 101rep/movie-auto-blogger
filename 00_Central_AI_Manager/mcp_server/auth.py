# -*- coding: utf-8 -*-
"""
Antigravity MCP Gateway Authentication & Permission Guard
Protects Cloudways automation infrastructure against unauthorized tool calls.
"""

import logging
from typing import Dict, Any, Optional
from mcp_server.mcp_config import mcp_settings

logger = logging.getLogger("MCPAuth")

class PermissionLevel:
    READ = 1        # Read/Inspect metrics, logs, queues, blog posts
    OPS = 2         # Restarts, syncs, cron triggers, cache purges
    PUBLISH = 3     # Content generation, queue adds, blog publishing
    CONFIG = 4      # Settings changes (Restricted)
    CODE = 5        # Code modification/Deploy (Restricted)

class MCPAuthGuard:
    @staticmethod
    def verify_token(token: Optional[str]) -> bool:
        if not token:
            return False
        return token.strip() == mcp_settings.MCP_AUTH_TOKEN.strip()

    @staticmethod
    def check_permission(tool_level: int) -> bool:
        """Ensures tool execution is within the permitted security ceiling (Level 1~3)."""
        if tool_level > mcp_settings.MAX_ALLOWED_LEVEL:
            logger.warning(f"[MCP Guard Rejected] Tool level {tool_level} exceeds max allowed {mcp_settings.MAX_ALLOWED_LEVEL}")
            return False
        return True

    @staticmethod
    def enforce_guard(tool_name: str, tool_level: int, auth_token: Optional[str] = None) -> Dict[str, Any]:
        if auth_token is not None and not MCPAuthGuard.verify_token(auth_token):
            return {
                "status": "AUTH_ERROR",
                "message": "인증 실패: 유효하지 않은 MCP_AUTH_TOKEN 입니다."
            }
            
        if not MCPAuthGuard.check_permission(tool_level):
            return {
                "status": "PERMISSION_DENIED",
                "message": f"보안 거부: '{tool_name}' 도구(Level {tool_level})는 현재 활성화된 최대 보안 등급(Level {mcp_settings.MAX_ALLOWED_LEVEL})을 초과합니다."
            }
            
        return {"status": "ALLOWED"}

auth_guard = MCPAuthGuard()
