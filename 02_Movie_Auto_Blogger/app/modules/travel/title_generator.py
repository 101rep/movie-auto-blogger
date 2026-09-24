"""Utility for generating click‑through‑rate (CTR) optimized travel titles.
Combines long-tail niche keywords (소형 키워드), city-specific travel anchors,
psychological curiosity/loss-aversion triggers, and SERP-friendly bracket formatting.
"""
import re
import random
from typing import Dict, List, Optional


class TitleGenerator:
    """Advanced Marketing & SEO Title Generator for Travel Guides."""

    MAX_LENGTH = 50  # Optimal for mobile/desktop search results without truncation

    EMOJIS = ["✨", "\U0001F31F", "\U0001F44D", "\U0001F525", "✈️", "💡", "📍", "🎯"]
    POWER_WORDS = [
        "필수", "핵심", "최고", "완벽", "인생", "베스트", "추천",
        "꿀팁", "실패 없는", "알짜배기", "총정리", "실속", "초가성비"
    ]

    # City-specific high-search-intent niche long-tail keywords (소형 황금 키워드)
    CITY_NICHE_KEYWORDS: Dict[str, List[str]] = {
        "오사카": [
            "주유패스 뽕뽑는 동선",
            "USJ 닌텐도월드 공략",
            "총경비 60만원 컷 뚜벅이",
            "도톤보리·난바 먹방 투어",
            "교토 근교 당일치기 포함 코스",
            "동선 낭비 0% 꿀팁"
        ],
        "후쿠오카": [
            "공항 5분 컷 뚜벅이",
            "유후인 료칸 온천 힐링",
            "총경비 40만원대 실속",
            "하카타 텐진 미식 투어",
            "부모님 효도 온천 코스",
            "나카스 야타이 포차 꿀팁"
        ],
        "도쿄": [
            "지하철 패스 뽕뽑는 동선",
            "시부야 신주쿠 알짜배기",
            "총경비 절약 뚜벅이 코스",
            "가기 전 필수 체크",
            "디즈니 & 도심 완벽 코스",
            "실패 없는 인생 코스"
        ],
        "다낭": [
            "가성비 5성급 풀빌라 호캉스",
            "바나힐 & 호이안 감성 야경",
            "1인 50만원대 실속 경비",
            "가족·부모님 맞춤 힐링",
            "바가지 없는 필수 꿀팁",
            "미케비치 힐링 코스"
        ],
        "호이안": [
            "올드타운 소원배 & 야경",
            "가성비 감성 투어 꿀팁"
        ],
        "방콕": [
            "왓아룬 선셋 야경 명소",
            "가성비 5성급 호캉스 & 마사지",
            "1인 60만원대 알짜 경비",
            "아이콘시암 & 야시장 먹방",
            "동선 낭비 없는 알짜 코스",
            "바가지 피하는 필수 꿀팁"
        ],
        "제주도": [
            "렌트카 동선 낭비 0% 코스",
            "부모님도 극찬한 힐링 명소",
            "오션뷰 감성 카페 & 찐맛집",
            "동쪽 vs 서쪽 알짜배기 일정",
            "실패 없는 가성비 코스",
            "현지인 추천 숨은 명소"
        ],
        "부산": [
            "차 없이 떠나는 뚜벅이 코스",
            "해변열차 & 스카이캡슐 꿀팁",
            "광안리 해운대 오션뷰 감성",
            "로컬 국밥 & 미식 투어",
            "동선 완벽한 힐링 여행",
            "실패 없는 필수 코스"
        ],
        "타이베이": [
            "예스진지 알짜배기 투어",
            "시먼딩 야시장 먹방 정복",
            "이지카드 뽕뽑는 뚜벅이",
            "총경비 50만원 컷 일정"
        ]
    }

    BENEFITS = [
        "필수 꿀팁",
        "핵심 코스",
        "완벽 총정리",
        "실속 가이드",
        "알짜배기 정리",
        "실패 없는 팁",
        "최고의 코스",
        "인생 명소"
    ]

    @classmethod
    def generate_ctr_title(cls, item) -> str:
        """Generate a high-converting, long-tail keyword rich title."""
        raw_dest = getattr(item, "destination", "인기 여행지")
        # Strip foreign parentheses like (Tokyo), (Osaka) to keep title clean & natural in Korean
        clean_dest = re.sub(r'\(.*?\)', '', raw_dest).strip()
        raw_dur = getattr(item, "duration", "2박 3일").strip()

        # Find matching niche keywords for the city
        niche_list: Optional[List[str]] = None
        for city_key, kw_list in cls.CITY_NICHE_KEYWORDS.items():
            if city_key in clean_dest:
                niche_list = kw_list
                break

        if not niche_list:
            niche_list = [
                "동선 낭비 0% 뚜벅이 코스",
                "총경비 절약 실속 일정",
                "현지인 찐맛집 & 명소",
                "부모님도 만족한 힐링 코스",
                "가기 전 필수 체크 꿀팁"
            ]

        niche = random.choice(niche_list)
        benefit = random.choice(cls.BENEFITS)
        emoji = random.choice(cls.EMOJIS)

        templates = [
            f"[{clean_dest} {raw_dur}] {niche} & {benefit} {emoji}",
            f"{emoji} [{clean_dest} {raw_dur}] {niche} ({benefit})",
            f"[{clean_dest} {raw_dur}] {niche} - {benefit} {emoji}"
        ]
        title = random.choice(templates)

        if len(title) > cls.MAX_LENGTH:
            title = title[:cls.MAX_LENGTH - 1] + "…"

        return title

