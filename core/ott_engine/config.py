# -*- coding: utf-8 -*-
"""
Configuration for EnterPick24 OTT Automation Engine.
Integrates TVmaze API, Fanart.tv API, and EnterPick24 WordPress REST API.
"""

import os
from typing import Dict, Any

TVMAZE_API_KEY = os.getenv("TVMAZE_API_KEY", "SScd32qJcRIXTXpPu1dULzsLrJYCsP2C")
FANART_API_KEY = os.getenv("FANART_API_KEY", "84fb0957df6b7a511cdb10b3025e4755")

# EnterPick24 WordPress Credentials
WP_URL = os.getenv("ENTERPICK_WP_URL", "https://enter.trendspot24.com")
WP_USER = os.getenv("ENTERPICK_WP_USER", "ktaehoon80@gmail.com")
WP_PASS = os.getenv("ENTERPICK_WP_PASS", "aUma6aotA2Q5ugxkohI5PnKd")
WP_SITE_ID = 4

# API Base Endpoints
TVMAZE_BASE_URL = "https://api.tvmaze.com"
FANART_BASE_URL = "https://webservice.fanart.tv/v3"

# Major Streaming Platforms Mapping
STREAMING_PLATFORMS = {
    "Netflix": {"color": "#E50914", "badge": "NETFLIX", "tag": "넷플릭스"},
    "Disney+": {"color": "#113CCF", "badge": "DISNEY+", "tag": "디즈니+"},
    "Apple TV+": {"color": "#4A4A4A", "badge": "APPLE TV+", "tag": "애플TV+"},
    "HBO Max": {"color": "#5822B4", "badge": "HBO MAX", "tag": "HBO맥스"},
    "Max": {"color": "#002BE7", "badge": "MAX", "tag": "맥스"},
    "Amazon Prime Video": {"color": "#00A8E1", "badge": "PRIME VIDEO", "tag": "아마존프라임"},
    "TVING": {"color": "#FF153C", "badge": "TVING", "tag": "티빙"},
    "Wavve": {"color": "#1351F9", "badge": "WAVVE", "tag": "웨이브"},
    "Coupang Play": {"color": "#1E88E5", "badge": "COUPANG PLAY", "tag": "쿠팡플레이"},
}

# Commercial Affiliate Links & Call-to-Actions
COMMERCIAL_CONFIG = {
    "vpn": {
        "title": "한국 넷플릭스 미공개작 안전 시청 가이드 (VPN 우회)",
        "desc": "본 작품은 미국/영국 등 해외 OTT 서비스에서 우선 스트리밍 중입니다. 공식 검증된 고속 스트리밍 전용 VPN을 통해 안전하게 초고화질(4K HDR)로 시청하실 수 있습니다.",
        "button_text": "🛡️ 초고속 스트리밍 VPN 특별 할인 혜택 확인",
        "url": "https://enter.trendspot24.com/recommend/vpn"
    },
    "ott_sub": {
        "title": "공식 스트리밍 플랫폼 바로가기 및 구독 혜택",
        "desc": "최고 화질과 돌비 애트모스 입체 사운드로 감상하세요. 플랫폼별 첫 달 무료 및 통신사 결합 할인 혜택을 확인하실 수 있습니다.",
        "button_text": "🍿 공식 플랫폼 최저가 시청 링크",
        "url": "https://enter.trendspot24.com/recommend/ott"
    },
    "cinema": {
        "title": "몰입감을 극대화하는 홈시네마 추천 기기",
        "desc": "영상미와 사운드가 핵심인 대작입니다. 돌비 애트모스 사운드바 및 4K 스마트 프로젝터로 나만의 전용 영화관을 완성해보세요.",
        "button_text": "🔊 4K 홈시네마 디바이스 큐레이션",
        "url": "https://enter.trendspot24.com/recommend/gear"
    }
}
