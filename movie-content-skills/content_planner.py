# -*- coding: utf-8 -*-
"""
EnterPick24 Daily Content Planner (V4).
Plans 4 distinct daily slots with non-overlapping search intents and entity isolation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class DailyContentPlanner:
    """Plans daily content generation for EnterPick24."""

    SLOT_DEFINITIONS = {
        1: {
            "slot_name": "SLOT 1: DISCOVERY / CURATION",
            "time_kst": "08:00",
            "skill_name": "movie-top5-writer",
            "search_intent": "discovery_curation",
            "intent_korean": "신작/명작 발견 및 다작 비교 탐색",
            "category": "추천·큐레이션",
            "category_id": 36,
        },
        2: {
            "slot_name": "SLOT 2: SINGLE TITLE DEEP DIVE",
            "time_kst": "12:30",
            "skill_name": "ott-movie-review",
            "search_intent": "single_title_deep_dive",
            "intent_korean": "화제작 단일 작품 심층 비평 및 관전 포인트",
            "category": "OTT",
            "category_id": 34,
        },
        3: {
            "slot_name": "SLOT 3: THEME CURATION",
            "time_kst": "18:00",
            "skill_name": "ott-theme-curator",
            "search_intent": "theme_curation",
            "intent_korean": "특정 테마/장르별 몰아보기(Binge-watch) 큐레이션",
            "category": "추천·큐레이션",
            "category_id": 36,
        },
        4: {
            "slot_name": "SLOT 4: STREAMING / INFORMATION",
            "time_kst": "21:30",
            "skill_name": "ott-streaming-guide",
            "search_intent": "streaming_information",
            "intent_korean": "국내 OTT 합법 시청 플랫폼 및 요금/할인 정보",
            "category": "OTT",
            "category_id": 34,
        },
    }

    def __init__(self):
        # Rotating seed topics to guarantee daily diversity
        self.daily_seed_candidates = [
            {
                "slot_1": {"topic": "스릴러", "primary_entity": "스릴러 명작 5선", "target_keyword": "스릴러 영화 추천"},
                "slot_2": {"topic": "세브란스 (단절)", "primary_entity": "SEVERANCE", "target_keyword": "세브란스 단절 리뷰"},
                "slot_3": {"topic": "넷플릭스 심리 미스터리", "primary_entity": "넷플릭스 미스터리", "target_keyword": "넷플릭스 미스터리 추천"},
                "slot_4": {"topic": "오징어 게임", "primary_entity": "SQUID_GAME", "target_keyword": "오징어 게임 스트리밍"},
            },
            {
                "slot_1": {"topic": "SF 판타지", "primary_entity": "SF 판타지 명작 5선", "target_keyword": "SF 영화 추천"},
                "slot_2": {"topic": "삼체", "primary_entity": "THREE_BODY_PROBLEM", "target_keyword": "삼체 심층 리뷰"},
                "slot_3": {"topic": "웰메이드 범죄 수사극", "primary_entity": "범죄 수사극", "target_keyword": "범죄 수사 시리즈 추천"},
                "slot_4": {"topic": "기묘한 이야기", "primary_entity": "STRANGER_THINGS", "target_keyword": "기묘한 이야기 보는 곳"},
            },
            {
                "slot_1": {"topic": "한국 명작 영화", "primary_entity": "한국 영화 5선", "target_keyword": "한국 영화 추천"},
                "slot_2": {"topic": "무빙", "primary_entity": "MOVING", "target_keyword": "디즈니 무빙 관전포인트"},
                "slot_3": {"topic": "디즈니+ 오리지널 명작", "primary_entity": "디즈니플러스 추천", "target_keyword": "디즈니 플러스 추천작"},
                "slot_4": {"topic": "더 글로리", "primary_entity": "THE_GLORY", "target_keyword": "더 글로리 스트리밍"},
            }
        ]

    def create_daily_plan(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Creates a structured daily plan of 4 slots.
        Validates that primary entities do not collide and intents are distinct.
        """
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")

        # Pick candidate seed by date day
        day_num = int(target_date.replace("-", "")) % len(self.daily_seed_candidates)
        seed = self.daily_seed_candidates[day_num]

        plans = []
        seen_entities = set()
        seen_intents = set()

        for slot_num in [1, 2, 3, 4]:
            slot_def = self.SLOT_DEFINITIONS[slot_num]
            slot_seed = seed[f"slot_{slot_num}"]

            entity = slot_seed["primary_entity"]
            intent = slot_def["search_intent"]

            if entity in seen_entities:
                raise ValueError(f"Entity collision detected in slot {slot_num}: {entity}")
            if intent in seen_intents:
                raise ValueError(f"Intent collision detected in slot {slot_num}: {intent}")

            seen_entities.add(entity)
            seen_intents.add(intent)

            plan = {
                "date": target_date,
                "slot_num": slot_num,
                "slot_name": slot_def["slot_name"],
                "time_kst": slot_def["time_kst"],
                "skill_name": slot_def["skill_name"],
                "search_intent": intent,
                "intent_korean": slot_def["intent_korean"],
                "category": slot_def["category"],
                "category_id": slot_def["category_id"],
                "topic": slot_seed["topic"],
                "primary_entity": entity,
                "target_keyword": slot_seed["target_keyword"]
            }
            plans.append(plan)

        return plans

    def format_plan_report(self, plans: List[Dict[str, Any]]) -> str:
        """Formats the daily plan for Telegram reporting."""
        if not plans:
            return "편성 계획이 없습니다."
        dt = plans[0].get("date", datetime.now().strftime("%Y-%m-%d"))
        lines = [
            f"📅 [EnterPick24 오늘의 편성 계획] {dt}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "총 4개 슬롯 (검색 의도 및 엔티티 중복 격리 검증 완료)\n"
        ]
        for p in plans:
            lines.append(f"[{p['time_kst']}] {p['slot_name']}")
            lines.append(f"• 주제/작품: {p['topic']} ({p['primary_entity']})")
            lines.append(f"• 검색 의도: {p['intent_korean']}")
            lines.append(f"• 타깃 카테고리: {p['category']}")
            lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)
