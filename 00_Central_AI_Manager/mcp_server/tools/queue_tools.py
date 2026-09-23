# -*- coding: utf-8 -*-
"""
ItemPick24 Queue MCP Tools (Level 1 & Level 3)
"""

import logging
from typing import Dict, Any, Optional
from services.itempick_queue_service import itempick_queue_service
from mcp_server.auth import auth_guard, PermissionLevel

logger = logging.getLogger("MCPQueueTools")

async def get_queue_status(auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 1: Read] 아이템픽24(item.travelpick24.com)의 예약 발행 대기열(Queue) 현황과 최근 완료된 글 목록을 조회합니다.
    """
    guard = auth_guard.enforce_guard("get_queue_status", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        queue = itempick_queue_service._load_queue()
        pending = [i for i in queue if i.get("status") == "pending"]
        completed = [i for i in queue if i.get("status") == "completed"]
        
        return {
            "status": "SUCCESS",
            "pending_count": len(pending),
            "completed_count": len(completed),
            "pending_items": pending,
            "recent_completed": completed[-5:]
        }
    except Exception as e:
        logger.error(f"get_queue_status error: {e}")
        return {"status": "ERROR", "message": str(e)}

async def add_to_itempick_queue(url: str, title_hint: str = "", mode: str = "guide", auth_token: str = "") -> Dict[str, Any]:
    """
    [Level 3: Publish] 쿠팡, 오늘의집, 또는 올리브영 제휴 링크를 아이템픽24 순차 지연 큐(+10분, +1시간10분)에 예약 등록합니다.
    mode 옵션: 'guide'(구매가이드), 'price_compare'(가격비교), 'review_synthesis'(후기분석), 'hotdeal_hack'(핫딜선점)
    """
    guard = auth_guard.enforce_guard("add_to_itempick_queue", PermissionLevel.PUBLISH, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    try:
        raw_text = f"{title_hint} {url}" if title_hint else url
        if mode in ["price_compare", "가격비교"]:
            raw_text = f"[가격비교] {raw_text}"
        elif mode in ["review_synthesis", "후기분석", "리뷰"]:
            raw_text = f"[리뷰분석] {raw_text}"
        elif mode in ["hotdeal_hack", "핫딜", "선점"]:
            raw_text = f"[핫딜] {raw_text}"

        res = itempick_queue_service.add_to_queue(raw_text, user_id="mcp_client")
        return res
    except Exception as e:
        logger.error(f"add_to_itempick_queue error: {e}")
        return {"status": "ERROR", "message": str(e)}
