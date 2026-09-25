# -*- coding: utf-8 -*-
"""
EnterPick24 Content Fingerprint Engine (V4).
Provides bilingual entity normalization, semantic hashing, and metadata fingerprinting.
"""

import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime


# Canonical Entity Mapping for Korean and English variations
CANONICAL_ENTITY_MAP = {
    # Squid Game
    "squid game": "SQUID_GAME",
    "오징어 게임": "SQUID_GAME",
    "오징어게임": "SQUID_GAME",

    # Stranger Things
    "stranger things": "STRANGER_THINGS",
    "기묘한 이야기": "STRANGER_THINGS",
    "기묘한이야기": "STRANGER_THINGS",

    # All of Us Are Dead
    "all of us are dead": "ALL_OF_US_ARE_DEAD",
    "지금 우리 학교는": "ALL_OF_US_ARE_DEAD",
    "지금우리학교는": "ALL_OF_US_ARE_DEAD",
    "지우학": "ALL_OF_US_ARE_DEAD",

    # The Glory
    "the glory": "THE_GLORY",
    "더 글로리": "THE_GLORY",
    "더글로리": "THE_GLORY",

    # Moving
    "moving": "MOVING",
    "무빙": "MOVING",

    # Severance
    "severance": "SEVERANCE",
    "세브란스": "SEVERANCE",
    "단절": "SEVERANCE",

    # 3 Body Problem
    "3 body problem": "THREE_BODY_PROBLEM",
    "three body problem": "THREE_BODY_PROBLEM",
    "삼체": "THREE_BODY_PROBLEM",

    # Parasite
    "parasite": "PARASITE",
    "기생충": "PARASITE",

    # Oldboy
    "oldboy": "OLDBOY",
    "올드보이": "OLDBOY",

    # Memories of Murder
    "memories of murder": "MEMORIES_OF_MURDER",
    "살인의 추억": "MEMORIES_OF_MURDER",
    "살인의추억": "MEMORIES_OF_MURDER",

    # Decision to Leave
    "decision to leave": "DECISION_TO_LEAVE",
    "헤어질 결심": "DECISION_TO_LEAVE",
    "헤어질결심": "DECISION_TO_LEAVE",

    # Mindhunter
    "mindhunter": "MINDHUNTER",
    "마인드헌터": "MINDHUNTER",

    # Ozark
    "ozark": "OZARK",
    "오자크": "OZARK",

    # Dark
    "dark": "DARK",
    "다크": "DARK",

    # Narcos
    "narcos": "NARCOS",
    "나르코스": "NARCOS",

    # Wednesday
    "wednesday": "WEDNESDAY",
    "웬즈데이": "WEDNESDAY",

    # One Piece
    "one piece": "ONE_PIECE",
    "원피스": "ONE_PIECE",

    # Sweet Home
    "sweet home": "SWEET_HOME",
    "스위트홈": "SWEET_HOME",

    # Gyeongseong Creature
    "gyeongseong creature": "GYEONGSEONG_CREATURE",
    "경성크리처": "GYEONGSEONG_CREATURE",
    "경성 크리처": "GYEONGSEONG_CREATURE",
}


def normalize_entity_name(name: str) -> str:
    """Normalizes any movie/series name into a canonical uppercase ID."""
    if not name:
        return "UNKNOWN_ENTITY"
    cleaned = re.sub(r"[\s\-_·:()\[\],.'\"]+", " ", name).strip().lower()
    if cleaned in CANONICAL_ENTITY_MAP:
        return CANONICAL_ENTITY_MAP[cleaned]

    # Check substring matches
    for k, v in CANONICAL_ENTITY_MAP.items():
        if k in cleaned:
            return v

    # Fallback: clean ASCII / uppercase representation
    fallback = re.sub(r"[^\w\s]", "", cleaned).strip().replace(" ", "_").upper()
    return fallback if fallback else "UNKNOWN_ENTITY"


def normalize_title(title: str) -> str:
    """Normalizes title string for exact title collision check."""
    if not title:
        return ""
    # Strip HTML entities, brackets, special punctuation, spaces
    cleaned = re.sub(r"&[a-z0-9]+;", "", title)
    cleaned = re.sub(r"[\s\-_·:()\[\],.'\"’‘!?]+", "", cleaned)
    return cleaned.lower()


class ContentFingerprint:
    """Encapsulates content metadata fingerprint and semantic identity."""

    def __init__(
        self,
        content_id: Any,
        content_type: str,
        title: str,
        primary_entity: str,
        secondary_entities: Optional[List[str]] = None,
        franchise: Optional[str] = None,
        primary_topic: str = "",
        genre: str = "",
        ott_provider: str = "Netflix",
        search_intent: str = "general",
        keywords: Optional[List[str]] = None,
        summary: str = "",
        published_at: Optional[str] = None
    ):
        self.content_id = str(content_id)
        self.content_type = content_type
        self.title = title
        self.title_normalized = normalize_title(title)
        self.primary_entity = normalize_entity_name(primary_entity)
        self.secondary_entities = [normalize_entity_name(e) for e in (secondary_entities or [])]
        self.franchise = franchise or self.primary_entity
        self.primary_topic = primary_topic
        self.genre = genre
        self.ott_provider = ott_provider
        self.search_intent = search_intent
        self.keywords = keywords or []
        self.summary = summary
        self.published_at = published_at or datetime.now().isoformat()

        # Compute cryptographic fingerprints
        self.fingerprint = self._calculate_fingerprint()
        self.semantic_hash = self._calculate_semantic_hash()

    def _calculate_fingerprint(self) -> str:
        raw = f"{self.primary_entity}|{self.title_normalized}|{self.search_intent}|{self.ott_provider}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _calculate_semantic_hash(self) -> str:
        raw = f"{self.primary_entity}|{','.join(sorted(self.secondary_entities))}|{self.genre}|{self.primary_topic}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "content_type": self.content_type,
            "title": self.title,
            "title_normalized": self.title_normalized,
            "primary_entity": self.primary_entity,
            "secondary_entities": self.secondary_entities,
            "franchise": self.franchise,
            "primary_topic": self.primary_topic,
            "genre": self.genre,
            "ott_provider": self.ott_provider,
            "search_intent": self.search_intent,
            "keywords": self.keywords,
            "summary": self.summary,
            "published_at": self.published_at,
            "fingerprint": self.fingerprint,
            "semantic_hash": self.semantic_hash
        }
