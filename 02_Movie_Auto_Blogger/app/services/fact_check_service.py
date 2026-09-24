"""AI Fact Checker service verifying factual claims against authoritative movie metadata."""
from enum import Enum
import json
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.ai.schemas import ArticleOutput
from app.database.models import Movie
from app.utils.logging import get_logger

logger = get_logger("fact_check_service")


class FactCheckStatus(str, Enum):
    """Factual claim verification status."""
    VERIFIED = "VERIFIED"        # Explicitly matched with ground truth metadata
    LIKELY = "LIKELY"            # Highly probable / partial match
    UNVERIFIED = "UNVERIFIED"    # Ground truth not available or subjective expression
    CONFLICT = "CONFLICT"        # Directly contradicts ground truth metadata


class ClaimType(str, Enum):
    """Category of factual claim."""
    TITLE = "TITLE"
    DIRECTOR = "DIRECTOR"
    RELEASE_YEAR = "RELEASE_YEAR"
    CAST = "CAST"
    RUNTIME = "RUNTIME"
    GENRE = "GENRE"


class FactCheckItem(BaseModel):
    """Individual factual claim check result."""
    claim_type: ClaimType
    claimed_text: str
    ground_truth: Optional[str] = None
    status: FactCheckStatus
    confidence: float = 1.0
    detail: str


class FactCheckReport(BaseModel):
    """Aggregate fact-checking report for an article."""
    movie_title: str
    total_claims: int = 0
    verified_count: int = 0
    likely_count: int = 0
    unverified_count: int = 0
    conflict_count: int = 0
    has_fatal_conflict: bool = False
    items: List[FactCheckItem] = Field(default_factory=list)
    summary: str = ""


class FactCheckService:
    """Verifies article content against authoritative metadata to prevent AI hallucinations."""

    @staticmethod
    def extract_and_verify(article: ArticleOutput, movie: Movie) -> FactCheckReport:
        """Extract claims from article text and verify against movie metadata."""
        items: List[FactCheckItem] = []
        full_text = " ".join([
            article.title,
            article.basic_info_summary,
            article.cast_and_director,
            article.spoiler_free_synopsis,
            article.conclusion
        ])

        # 1. Verify Movie Title
        expected_clean = movie.title.split("(")[0].strip().lower()
        if expected_clean in full_text.lower():
            items.append(FactCheckItem(
                claim_type=ClaimType.TITLE,
                claimed_text=expected_clean,
                ground_truth=movie.title,
                status=FactCheckStatus.VERIFIED,
                confidence=1.0,
                detail=f"영화 제목 '{movie.title}'이 본문 및 제목에 정상 반영됨."
            ))
        else:
            items.append(FactCheckItem(
                claim_type=ClaimType.TITLE,
                claimed_text=article.title,
                ground_truth=movie.title,
                status=FactCheckStatus.CONFLICT,
                confidence=0.9,
                detail=f"영화 제목 '{movie.title}'이 본문 어디에도 명시되지 않음."
            ))

        # 2. Verify Director
        if movie.director:
            director_clean = movie.director.strip().lower()
            # Check if director is mentioned in cast_and_director or text
            if director_clean in full_text.lower():
                items.append(FactCheckItem(
                    claim_type=ClaimType.DIRECTOR,
                    claimed_text=movie.director,
                    ground_truth=movie.director,
                    status=FactCheckStatus.VERIFIED,
                    confidence=1.0,
                    detail=f"감독 '{movie.director}' 정보 일치 확인."
                ))
            else:
                # Check if an incorrect director is explicitly claimed
                director_pattern = re.findall(r"([가-힣a-zA-Z\s]{2,15})\s*감독", article.cast_and_director + " " + article.basic_info_summary)
                conflicting_directors = [d.strip() for d in director_pattern if d.strip() and director_clean not in d.strip().lower()]
                if conflicting_directors:
                    items.append(FactCheckItem(
                        claim_type=ClaimType.DIRECTOR,
                        claimed_text=", ".join(conflicting_directors),
                        ground_truth=movie.director,
                        status=FactCheckStatus.CONFLICT,
                        confidence=0.85,
                        detail=f"실제 감독('{movie.director}')과 다른 감독('{', '.join(conflicting_directors)}')이 명시됨."
                    ))
                else:
                    items.append(FactCheckItem(
                        claim_type=ClaimType.DIRECTOR,
                        claimed_text="미언급",
                        ground_truth=movie.director,
                        status=FactCheckStatus.UNVERIFIED,
                        confidence=0.5,
                        detail=f"감독 '{movie.director}'이 본문에 구체적으로 언급되지 않음."
                    ))

        # 3. Verify Release Year
        if movie.release_date and len(movie.release_date) >= 4:
            true_year = movie.release_date[:4]
            year_matches = re.findall(r"\b(19\d{2}|20\d{2})년", full_text)
            if true_year in year_matches or true_year in full_text:
                items.append(FactCheckItem(
                    claim_type=ClaimType.RELEASE_YEAR,
                    claimed_text=true_year,
                    ground_truth=true_year,
                    status=FactCheckStatus.VERIFIED,
                    confidence=1.0,
                    detail=f"개봉 연도 '{true_year}' 일치 확인."
                ))
            elif year_matches:
                # Has years mentioned, but not true_year
                items.append(FactCheckItem(
                    claim_type=ClaimType.RELEASE_YEAR,
                    claimed_text=", ".join(set(year_matches)),
                    ground_truth=true_year,
                    status=FactCheckStatus.LIKELY,
                    confidence=0.6,
                    detail=f"개봉 연도({true_year}) 대신 다른 연도 언급됨: {', '.join(set(year_matches))}"
                ))

        # 4. Verify Major Cast
        if movie.cast_json:
            try:
                cast_list = json.loads(movie.cast_json)
                if isinstance(cast_list, list) and cast_list:
                    matched_cast = [actor for actor in cast_list[:5] if actor.lower() in full_text.lower()]
                    if len(matched_cast) >= 1:
                        items.append(FactCheckItem(
                            claim_type=ClaimType.CAST,
                            claimed_text=", ".join(matched_cast),
                            ground_truth=", ".join(cast_list[:5]),
                            status=FactCheckStatus.VERIFIED,
                            confidence=0.95,
                            detail=f"주요 출연진 {len(matched_cast)}명 일치 ({', '.join(matched_cast)})."
                        ))
                    else:
                        items.append(FactCheckItem(
                            claim_type=ClaimType.CAST,
                            claimed_text="불일치/누락",
                            ground_truth=", ".join(cast_list[:5]),
                            status=FactCheckStatus.UNVERIFIED,
                            confidence=0.7,
                            detail="주요 출연진 메타데이터가 본문에 언급되지 않음."
                        ))
            except Exception:
                pass

        # 5. Verify Runtime
        if movie.runtime and movie.runtime > 0:
            runtime_str = str(movie.runtime)
            runtime_matches = re.findall(r"(\d+)\s*분", full_text)
            if runtime_str in runtime_matches:
                items.append(FactCheckItem(
                    claim_type=ClaimType.RUNTIME,
                    claimed_text=f"{runtime_str}분",
                    ground_truth=f"{runtime_str}분",
                    status=FactCheckStatus.VERIFIED,
                    confidence=1.0,
                    detail=f"상영시간 '{runtime_str}분' 정확히 일치."
                ))
            elif runtime_matches:
                mentioned_mins = [int(m) for m in runtime_matches]
                # If difference is > 30 minutes, conflict
                severe_diff = any(abs(m - movie.runtime) > 30 for m in mentioned_mins)
                if severe_diff:
                    items.append(FactCheckItem(
                        claim_type=ClaimType.RUNTIME,
                        claimed_text=f"{mentioned_mins}분",
                        ground_truth=f"{movie.runtime}분",
                        status=FactCheckStatus.CONFLICT,
                        confidence=0.8,
                        detail=f"상영시간 대폭 불일치 (실제 {movie.runtime}분 vs 본문 {mentioned_mins}분)."
                    ))

        # Tally counts
        verified = sum(1 for i in items if i.status == FactCheckStatus.VERIFIED)
        likely = sum(1 for i in items if i.status == FactCheckStatus.LIKELY)
        unverified = sum(1 for i in items if i.status == FactCheckStatus.UNVERIFIED)
        conflicts = sum(1 for i in items if i.status == FactCheckStatus.CONFLICT)

        # Fatal conflict is defined as wrong title or wrong director
        has_fatal = any(
            i.status == FactCheckStatus.CONFLICT and i.claim_type in (ClaimType.TITLE, ClaimType.DIRECTOR)
            for i in items
        )

        summary = f"검증 완료: {verified}건, 개연성: {likely}건, 미검증: {unverified}건, 충돌: {conflicts}건"

        report = FactCheckReport(
            movie_title=movie.title,
            total_claims=len(items),
            verified_count=verified,
            likely_count=likely,
            unverified_count=unverified,
            conflict_count=conflicts,
            has_fatal_conflict=has_fatal,
            items=items,
            summary=summary
        )

        logger.info("Fact check completed for '%s': %s (Fatal=%s)", movie.title, summary, has_fatal)
        return report


class TravelFactCheckService:
    """Verifies travel article claims against authoritative catalog metadata."""

    @staticmethod
    def extract_and_verify(article: Any, item: Any) -> FactCheckReport:
        """Verify destination, country, and duration in travel article."""
        items: List[FactCheckItem] = []
        full_text = " ".join([
            getattr(article, "title", ""),
            getattr(article, "introduction", ""),
            getattr(article, "destination_overview", ""),
            getattr(article, "conclusion", "")
        ])

        raw_dest = getattr(item, "destination", "")
        clean_dest = re.sub(r'\(.*?\)', '', raw_dest).strip()
        country = getattr(item, "country", "")
        duration = getattr(item, "duration", "")

        # 1. Verify Destination
        if clean_dest.lower() in full_text.lower():
            items.append(FactCheckItem(
                claim_type=ClaimType.TITLE,
                claimed_text=clean_dest,
                ground_truth=raw_dest,
                status=FactCheckStatus.VERIFIED,
                confidence=1.0,
                detail=f"여행 목적지 '{clean_dest}'가 본문에 정확히 명시됨."
            ))
        else:
            items.append(FactCheckItem(
                claim_type=ClaimType.TITLE,
                claimed_text=getattr(article, "title", ""),
                ground_truth=raw_dest,
                status=FactCheckStatus.CONFLICT,
                confidence=0.9,
                detail=f"여행 목적지 '{clean_dest}'가 본문에 명시되지 않음."
            ))

        # 2. Verify Country
        if country and country.lower() in full_text.lower():
            items.append(FactCheckItem(
                claim_type=ClaimType.GENRE,
                claimed_text=country,
                ground_truth=country,
                status=FactCheckStatus.VERIFIED,
                confidence=1.0,
                detail=f"국가 정보 '{country}' 일치 확인."
            ))
        elif country:
            items.append(FactCheckItem(
                claim_type=ClaimType.GENRE,
                claimed_text="미확인",
                ground_truth=country,
                status=FactCheckStatus.UNVERIFIED,
                confidence=0.6,
                detail=f"국가 '{country}' 정보가 본문에서 명시적으로 언급되지 않음."
            ))

        # 3. Verify Duration
        if duration and duration in full_text:
            items.append(FactCheckItem(
                claim_type=ClaimType.RUNTIME,
                claimed_text=duration,
                ground_truth=duration,
                status=FactCheckStatus.VERIFIED,
                confidence=1.0,
                detail=f"여행 일정 기간 '{duration}' 일치 확인."
            ))

        verified = sum(1 for i in items if i.status == FactCheckStatus.VERIFIED)
        likely = sum(1 for i in items if i.status == FactCheckStatus.LIKELY)
        unverified = sum(1 for i in items if i.status == FactCheckStatus.UNVERIFIED)
        conflicts = sum(1 for i in items if i.status == FactCheckStatus.CONFLICT)
        has_fatal = any(i.status == FactCheckStatus.CONFLICT and i.claim_type == ClaimType.TITLE for i in items)

        summary = f"검증 완료: {verified}건, 개연성: {likely}건, 미검증: {unverified}건, 충돌: {conflicts}건"

        report = FactCheckReport(
            movie_title=raw_dest,
            total_claims=len(items),
            verified_count=verified,
            likely_count=likely,
            unverified_count=unverified,
            conflict_count=conflicts,
            has_fatal_conflict=has_fatal,
            items=items,
            summary=summary
        )

        logger.info("Travel fact check completed for '%s': %s (Fatal=%s)", raw_dest, summary, has_fatal)
        return report

