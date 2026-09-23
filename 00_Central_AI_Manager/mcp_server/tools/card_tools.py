# -*- coding: utf-8 -*-
"""
Card News & Toon Studio MCP Tools (Level 1 & Level 3)
"""

import logging
from typing import Dict, Any, Optional
from adapters.registry import registry
from mcp_server.auth import auth_guard, PermissionLevel

logger = logging.getLogger("MCPCardTools")

async def get_studio_status(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 1: Read] ToonForge 및 AI 쇼츠 리믹서의 렌더링 엔진 상태와 생성된 미디어 에셋 현황을 조회합니다.
    """
    guard = auth_guard.enforce_guard("get_studio_status", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        toon = registry.get("toonforge_studio")
        shorts = registry.get("shorts_remixer")
        
        toon_status = toon.get_status() if toon else {}
        shorts_status = shorts.get_status() if shorts else {}
        
        return {
            "status": "SUCCESS",
            "toonforge": toon_status,
            "shorts_remixer": shorts_status
        }
    except Exception as e:
        logger.error(f"get_studio_status error: {e}")
        return {"status": "ERROR", "message": str(e)}

async def create_card_news(title: str, content: str = "", image_url: str = "", auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 3: Publish] 지정한 제목과 원고를 바탕으로 1080x1350 규격의 인스타그램/쓰레즈 카드뉴스 및 4컷 툰 에셋을 렌더링합니다.
    """
    guard = auth_guard.enforce_guard("create_card_news", PermissionLevel.PUBLISH, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        toon = registry.get("toonforge_studio")
        if not toon:
            return {"status": "ERROR", "message": "toonforge_studio 어댑터가 로드되지 않았습니다."}
            
        res = toon.render_card_or_toon(title=title, content=content, image_url=image_url)
        return {
            "status": "SUCCESS",
            "title": title,
            "render_result": res
        }
    except Exception as e:
        logger.error(f"create_card_news error: {e}")
        return {"status": "ERROR", "message": str(e)}
