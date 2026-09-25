# -*- coding: utf-8 -*-
"""
EnterPick24 Dedicated Scheduler & WordPress Pipeline Adapter.
Strictly isolated to EnterPick24 (Site ID 4 / enter.trendspot24.com).
Prohibits execution against any other blog.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from zoneinfo import ZoneInfo
from movie_content_skills.generators import MovieSkillsEngine
from core.reliability.quality_gate import ContentQualityGate
from core.ott_engine.publisher import OTTPublisher
from core.ott_engine.config import WP_URL, WP_USER, WP_PASS, WP_SITE_ID

logger = logging.getLogger("enterpick_adapter")

# Golden Publishing Schedule for EnterPick24 (KST)
ENTERPICK_DAILY_SLOTS = [
    {"slot": 1, "time": "08:00", "skill": "movie-top5-writer", "topic": "스릴러"},
    {"slot": 2, "time": "12:30", "skill": "ott-movie-review", "topic": "Stranger Things"},
    {"slot": 3, "time": "18:00", "skill": "ott-theme-curator", "topic": "넷플릭스 범죄 수사극"},
    {"slot": 4, "time": "21:30", "skill": "ott-streaming-guide", "topic": "Squid Game"},
]


class EnterPickIsolationGuard:
    """Guarantees this adapter ONLY touches EnterPick24."""

    @staticmethod
    def verify(site_id: int, site_url: str):
        if site_id != WP_SITE_ID or "enter.trendspot24.com" not in (site_url or ""):
            raise PermissionError(
                f"🚨 [EnterPick Isolation Guard] Publication attempt to site_id={site_id}, url='{site_url}' rejected! "
                "This engine is strictly restricted to 엔터픽24 (Site ID 4 / enter.trendspot24.com) only."
            )


class EnterPickContentPipeline:
    """Manages generation, duplicate checking, WordPress publishing, and reporting for EnterPick24."""

    def __init__(self, wp_url: str = WP_URL, wp_user: str = WP_USER, wp_pass: str = WP_PASS):
        EnterPickIsolationGuard.verify(WP_SITE_ID, wp_url)
        self.wp_url = wp_url.rstrip("/")
        self.publisher = OTTPublisher(wp_url=wp_url, user=wp_user, password=wp_pass)
        self.engine = MovieSkillsEngine()

    def check_duplicate(self, candidate_title: str, existing_titles: List[str]) -> bool:
        """Checks if a title or topic has already been published recently."""
        clean_target = candidate_title.replace(" ", "").lower()
        for t in existing_titles:
            clean_t = t.replace(" ", "").lower()
            if clean_target in clean_t or clean_t in clean_target:
                return True
        return False

    def generate_slot_content(self, slot_idx: int) -> Dict[str, Any]:
        """Generates content matching the slot's designated skill."""
        slot_info = ENTERPICK_DAILY_SLOTS[slot_idx % len(ENTERPICK_DAILY_SLOTS)]
        skill_name = slot_info["skill"]
        topic = slot_info["topic"]

        if skill_name == "movie-top5-writer":
            data = self.engine.generate_top5(topic)
        elif skill_name == "ott-movie-review":
            data = self.engine.generate_review(topic)
        elif skill_name == "ott-theme-curator":
            data = self.engine.generate_curation(topic)
        elif skill_name == "ott-streaming-guide":
            data = self.engine.generate_streaming_guide(topic)
        else:
            raise ValueError(f"Unknown skill: {skill_name}")

        data["slot_time"] = slot_info["time"]
        return data

    def execute_daily_pipeline(
        self,
        publish_status: str = "draft",  # Default to 'draft' for safety & testing
        target_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates 4 posts for EnterPick24, validates them, and sends to WordPress.
        publish_status: 'draft' during testing, 'future' for scheduling.
        """
        kst = ZoneInfo("Asia/Seoul")
        now_kst = datetime.now(kst)
        date_str = target_date or now_kst.strftime("%Y-%m-%d")

        results = []
        existing_titles: List[str] = []

        for slot_idx, slot in enumerate(ENTERPICK_DAILY_SLOTS):
            logger.info(f"Processing EnterPick24 Slot {slot['slot']} ({slot['time']} KST, Skill: {slot['skill']})...")
            
            try:
                content_data = self.generate_slot_content(slot_idx)
                title = content_data["title"]
                body = content_data["content"]
                img_url = content_data.get("featured_image")
                movie_list = content_data.get("movie_list", [])

                # 1. Duplicate check
                if self.check_duplicate(title, existing_titles):
                    logger.warning(f"Duplicate detected for slot {slot['slot']}: {title}")
                    results.append({
                        "slot": slot["slot"],
                        "skill": slot["skill"],
                        "title": title,
                        "success": False,
                        "error": "중복 주제 감지 (Duplicate Detected)"
                    })
                    continue

                # 2. Quality Gate check
                gate = ContentQualityGate.evaluate(
                    title=title,
                    content=body,
                    category="OTT 매거진",
                    image_url=img_url
                )
                if not gate.passed:
                    logger.warning(f"Quality gate rejected slot {slot['slot']}: {gate.issues}")
                    results.append({
                        "slot": slot["slot"],
                        "skill": slot["skill"],
                        "title": title,
                        "success": False,
                        "error": f"품질 기준 미달 ({', '.join(gate.issues)})"
                    })
                    continue

                # 3. Publish to WordPress
                article_payload = {
                    "title": title,
                    "content": body,
                    "featured_image_url": img_url
                }
                pub_res = self.publisher.publish_article(article_payload, status=publish_status)

                if pub_res.get("success"):
                    existing_titles.append(title)
                    res_item = {
                        "slot": slot["slot"],
                        "skill": slot["skill"],
                        "title": title,
                        "movie_list": movie_list,
                        "scheduled_time": f"{date_str} {slot['time']} KST",
                        "post_id": pub_res.get("post_id"),
                        "status": publish_status,
                        "link": pub_res.get("link"),
                        "success": True
                    }
                else:
                    res_item = {
                        "slot": slot["slot"],
                        "skill": slot["skill"],
                        "title": title,
                        "success": False,
                        "error": pub_res.get("error", "Unknown publishing error")
                    }
                results.append(res_item)

            except Exception as e:
                logger.error(f"Error in slot {slot['slot']}: {e}")
                results.append({
                    "slot": slot["slot"],
                    "skill": slot["skill"],
                    "title": slot.get("topic", "N/A"),
                    "success": False,
                    "error": str(e)
                })

        return results

    @staticmethod
    def format_telegram_report(pipeline_results: List[Dict[str, Any]]) -> str:
        """
        Formats executive telegram notification.
        Never exposes API keys or passwords.
        """
        lines = [
            "🎬 [엔터픽24 영화·OTT 4대 스킬 자동 발행 보고서]",
            "📌 대상 블로그: enter.trendspot24.com (Site ID 4 전용)",
            "──────────────────────────"
        ]

        for item in pipeline_results:
            slot_num = item.get("slot")
            skill = item.get("skill")
            title = item.get("title", "")
            success = item.get("success", False)

            if success:
                post_id = item.get("post_id")
                status = item.get("status")
                sched_time = item.get("scheduled_time")
                link = item.get("link")
                movies = ", ".join(item.get("movie_list", []))
                lines.append(f"✅ [슬롯 {slot_num}] {skill}")
                lines.append(f"  • 제목: {title}")
                lines.append(f"  • 소개 작품: {movies}")
                lines.append(f"  • 등록 상태: {status.upper()} (ID: #{post_id})")
                lines.append(f"  • 예정 시간: {sched_time}")
                lines.append(f"  • 링크: {link}")
            else:
                err = item.get("error", "검증 실패")
                lines.append(f"❌ [슬롯 {slot_num}] {skill}")
                lines.append(f"  • 제목: {title}")
                lines.append(f"  • 원인: {err} (관리자 검토 전환)")
            lines.append("──────────────────────────")

        return "\n".join(lines)
