# -*- coding: utf-8 -*-
"""
EnterPick24 4-Level Duplicate Detection Engine & Duplicate Risk Scorer (V4).
Enforces strict 4-level duplication screening and 0-100 Risk Score.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from movie_content_skills.fingerprint import ContentFingerprint, normalize_title, normalize_entity_name


class DuplicateCheckResult:
    """Encapsulates the verdict of a duplicate check."""

    def __init__(
        self,
        is_blocked: bool,
        risk_level: str,  # "LOW", "MEDIUM", "HIGH"
        risk_score: float,  # 0 ~ 100
        block_reason: Optional[str] = None,
        conflicting_post_id: Optional[str] = None,
        level_triggered: Optional[int] = None
    ):
        self.is_blocked = is_blocked
        self.risk_level = risk_level
        self.risk_score = risk_score
        self.block_reason = block_reason
        self.conflicting_post_id = conflicting_post_id
        self.level_triggered = level_triggered

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_blocked": self.is_blocked,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "block_reason": self.block_reason,
            "conflicting_post_id": self.conflicting_post_id,
            "level_triggered": self.level_triggered
        }


class DuplicateEngine:
    """Executes 4-level duplicate inspection against existing corpus."""

    def __init__(self, existing_corpus: Optional[List[ContentFingerprint]] = None):
        self.corpus = existing_corpus or []

    def add_to_corpus(self, fp: ContentFingerprint):
        self.corpus.append(fp)

    def _days_between(self, dt1_str: str, dt2_str: str) -> int:
        """Calculates days between two ISO date strings."""
        try:
            d1 = datetime.fromisoformat(dt1_str[:10])
            d2 = datetime.fromisoformat(dt2_str[:10])
            return abs((d1 - d2).days)
        except Exception:
            return 999

    def _ngram_similarity(self, s1: str, s2: str, n: int = 2) -> float:
        """Computes character n-gram Jaccard similarity."""
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0
        n1 = {s1[i:i+n] for i in range(len(s1) - n + 1)}
        n2 = {s2[i:i+n] for i in range(len(s2) - n + 1)}
        if not n1 or not n2:
            return 0.0
        intersection = len(n1 & n2)
        union = len(n1 | n2)
        return intersection / union if union > 0 else 0.0

    def evaluate(self, candidate: ContentFingerprint) -> DuplicateCheckResult:
        """
        Runs candidate through 4 levels:
        Level 1: Exact Duplicate
        Level 2: Entity Duplicate (30d deep dive / 14d curation)
        Level 3: Search Intent Duplicate
        Level 4: Semantic Similarity (>= 0.88 BLOCK)
        """
        highest_risk = 0.0
        block_reason = None
        conflict_id = None
        level_hit = None

        for existing in self.corpus:
            # Skip comparing post with itself
            if existing.content_id == candidate.content_id:
                continue

            days_diff = self._days_between(candidate.published_at, existing.published_at)

            # -----------------------------------------------------------------
            # LEVEL 1: Exact Duplicate
            # -----------------------------------------------------------------
            if candidate.title_normalized and existing.title_normalized:
                if candidate.title_normalized == existing.title_normalized:
                    return DuplicateCheckResult(
                        is_blocked=True,
                        risk_level="HIGH",
                        risk_score=100.0,
                        block_reason=f"Level 1: 정확히 동일한 정규화 제목 ('{existing.title}')",
                        conflicting_post_id=existing.content_id,
                        level_triggered=1
                    )

            # -----------------------------------------------------------------
            # LEVEL 2: Entity Duplicate
            # -----------------------------------------------------------------
            is_same_entity = (candidate.primary_entity == existing.primary_entity)
            if is_same_entity:
                # Single Title Deep Dive: 30 days cooldown
                if candidate.content_type == "single_review" or existing.content_type == "single_review":
                    if days_diff < 30:
                        return DuplicateCheckResult(
                            is_blocked=True,
                            risk_level="HIGH",
                            risk_score=95.0,
                            block_reason=f"Level 2: 단일 작품 30일 이내 중복 ({candidate.primary_entity}, {days_diff}일 전 발행 ID {existing.content_id})",
                            conflicting_post_id=existing.content_id,
                            level_triggered=2
                        )
                # Curation: 14 days cooldown
                elif days_diff < 14:
                    return DuplicateCheckResult(
                        is_blocked=True,
                        risk_level="HIGH",
                        risk_score=85.0,
                        block_reason=f"Level 2: 큐레이션/테마 14일 이내 주요 엔티티 중복 ({candidate.primary_entity}, {days_diff}일 전 발행 ID {existing.content_id})",
                        conflicting_post_id=existing.content_id,
                        level_triggered=2
                    )

            # -----------------------------------------------------------------
            # LEVEL 3: Search Intent Duplicate
            # -----------------------------------------------------------------
            if is_same_entity and (candidate.search_intent == existing.search_intent):
                if days_diff < 45:
                    return DuplicateCheckResult(
                        is_blocked=True,
                        risk_level="HIGH",
                        risk_score=90.0,
                        block_reason=f"Level 3: 동일 엔티티 및 동일 검색 의도 중복 ({candidate.primary_entity} / {candidate.search_intent})",
                        conflicting_post_id=existing.content_id,
                        level_triggered=3
                    )

            # -----------------------------------------------------------------
            # LEVEL 4: Semantic Duplicate
            # -----------------------------------------------------------------
            cand_text = f"{candidate.title} {candidate.summary} {candidate.primary_entity} {candidate.primary_topic}"
            exist_text = f"{existing.title} {existing.summary} {existing.primary_entity} {existing.primary_topic}"
            sim = self._ngram_similarity(cand_text, exist_text, n=2)

            score_contribution = sim * 100
            if score_contribution > highest_risk:
                highest_risk = score_contribution

            if sim >= 0.88:
                return DuplicateCheckResult(
                    is_blocked=True,
                    risk_level="HIGH",
                    risk_score=min(100.0, sim * 100),
                    block_reason=f"Level 4: 문맥 및 시맨틱 유사도 {sim:.2f} 초과 (기준 0.88 이상 차단)",
                    conflicting_post_id=existing.content_id,
                    level_triggered=4
                )
            elif sim >= 0.78:
                block_reason = f"Level 4: 시맨틱 유사도 {sim:.2f} (검토 요망 범위 0.78 ~ 0.879)"
                conflict_id = existing.content_id
                level_hit = 4

        # Calculate final risk level
        if highest_risk >= 60.0:
            risk_level = "HIGH"
            is_blocked = True
        elif highest_risk >= 30.0:
            risk_level = "MEDIUM"
            is_blocked = False
        else:
            risk_level = "LOW"
            is_blocked = False

        return DuplicateCheckResult(
            is_blocked=is_blocked,
            risk_level=risk_level,
            risk_score=round(highest_risk, 1),
            block_reason=block_reason,
            conflicting_post_id=conflict_id,
            level_triggered=level_hit
        )
