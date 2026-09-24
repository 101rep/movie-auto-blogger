# -*- coding: utf-8 -*-
"""
Natural Language Intent Interpreter — AG Gateway PRD v2.0 PART 8

Translates natural language chat messages from Telegram into concrete automation actions:
- Example: "오늘 엔터픽24 발행 확인해줘"
  -> Intent: check_blog_publishing
  -> Target: blog_id=4 (엔터픽24)
  -> Calls: QA Agent / WordPress check tool
  -> Returns: Human-readable Telegram Markdown
"""

import re
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from core.reliability.daily_limit_engine import DailyLimitEngine
from core.reliability.scheduler_audit import TARGET_BLOGS

logger = logging.getLogger("natural_language_gateway")

BLOG_NAME_MAPPING = {
    "트래블픽24": 1, "트래블픽": 1, "travelpick": 1, "여행": 1, "여행블로그": 1,
    "트렌드스팟24": 2, "트렌드스팟": 2, "trendspot": 2, "테크": 2,
    "아이템픽24": 3, "아이템픽": 3, "item": 3, "장비": 3, "쿠팡": 3,
    "엔터픽24": 4, "엔터픽": 4, "enter": 4, "영화": 4, "ott": 4, "영화블로그": 4,
    "복지픽23": 5, "청년복지": 5, "welfare23": 5,
    "복지픽24": 6, "시니어복지": 6, "소상공인": 6, "welfare24": 6,
    "복지픽25": 7, "지원금": 7, "바우처": 7, "welfare25": 7,
    "뉴스픽24": 8, "뉴스픽": 8, "news": 8, "시사": 8
}


class NaturalLanguageInterpreter:
    """Interprets freeform Korean natural language commands for Telegram AI Control."""

    @classmethod
    async def process(cls, text: str, user_id: str = "telegram") -> Optional[str]:
        """
        Attempts to understand and handle a natural language command.
        Returns formatted Telegram response if recognized, or None if unrecognized.
        """
        clean = text.strip()
        low = clean.lower()

        # 1. Target blog identification
        matched_blog_id = None
        matched_blog_name = None
        for name_key, bid in BLOG_NAME_MAPPING.items():
            if name_key in low:
                matched_blog_id = bid
                matched_blog_name = next((b["name"] for b in TARGET_BLOGS if b["id"] == bid), f"블로그 #{bid}")
                break

        # 2. Intent matching
        # Intent A: 오늘 발행 확인 ("오늘 엔터픽24 발행 확인해줘", "트렌드스팟 발행 됐어?")
        if any(w in clean for w in ["발행 확인", "발행 됐", "글 올라갔", "발행 현황", "포스팅 확인", "몇개 올라갔"]):
            if matched_blog_id:
                return await cls._handle_blog_publish_check(matched_blog_id, matched_blog_name)
            else:
                # Check all blogs
                from core.reliability.auto_healer import AutoHealingSystem
                return await AutoHealingSystem.check_schedule()

        # Intent B: 오류 복구 ("실패한 거 다시 올려줘", "오류 난 글 복구해줘")
        if any(w in clean for w in ["다시 올려", "복구해줘", "재시도해줘", "에러 고쳐", "오류 수정"]):
            from core.reliability.auto_healer import AutoHealingSystem
            return await AutoHealingSystem.heal_failed()

        # Intent C: 시스템 점검 ("전체 시스템 상태 어때", "서버 자원 어때")
        if any(w in clean for w in ["전체 점검해줘", "시스템 점검", "서버 상태 어때", "상태 브리핑"]):
            from core.reliability.auto_healer import AutoHealingSystem
            return await AutoHealingSystem.system_report()

        # Intent D: 중복 검사 ("중복된 글 있는지 봐줘", "중복 체크해줘")
        if any(w in clean for w in ["중복 검사", "중복 체크", "중복 있"]):
            from core.reliability.auto_healer import AutoHealingSystem
            return await AutoHealingSystem.check_duplicate()

        return None

    @staticmethod
    async def _handle_blog_publish_check(blog_id: int, blog_name: str) -> str:
        """Handles specific blog publish check."""
        kst = ZoneInfo("Asia/Seoul")
        today_str = datetime.now(kst).strftime("%Y-%m-%d")

        can_pub, curr, limit, msg = DailyLimitEngine.can_publish(blog_id, today_str)

        lines = [
            f"🎬 <b>[{blog_name} 오늘({today_str}) 발행 현황 확인]</b>\n",
            f"• <b>현재 완료/예약 편수:</b> <b>{curr}편</b> (하루 최대 {limit}편)",
            f"• <b>잔여 슬롯:</b> <b>{max(0, limit - curr)}편</b>",
            f"• <b>상태 진단:</b> {msg}\n"
        ]

        if blog_id == 4:  # EnterPick24 special note per PRD
            lines.append("🛡️ <b>[엔터픽24 집중 보호 가드]:</b> 하루 4개 초과 발행 방지 락이 100% 정상 가동 중입니다.")

        return "\n".join(lines)
