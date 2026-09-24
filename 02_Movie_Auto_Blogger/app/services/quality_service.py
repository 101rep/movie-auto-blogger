"""Deterministic quality gate for AI-generated movie articles."""
import re
from typing import Any, Dict, List, Optional, Tuple
from app.ai.schemas import ArticleOutput
from app.database.models import QualityStatusEnum
from app.services.fact_check_service import FactCheckService, FactCheckStatus, TravelFactCheckService
from app.utils.logging import get_logger
from app.utils.security import SENSITIVE_PATTERNS

logger = get_logger("quality_gate")

FORBIDDEN_PLACEHOLDERS = [
    "[여기에", "[입력", "TODO", "TBD", "N/A", "내용을 입력하세요",
    "[작성자", "미정입니다", "작성 중", "인용구 입력"
]

JSON_LEAKAGE_PATTERNS = [
    re.compile(r"```json", re.IGNORECASE),
    re.compile(r"\{\s*\"title\":"),
    re.compile(r"\"slug_hint\":"),
    re.compile(r"\"faq\":\s*\[")
]


class QualityGateService:
    """Evaluates article content quality and returns PASS, REVIEW, or FAIL."""

    @staticmethod
    def evaluate(
        article: ArticleOutput,
        expected_movie_title: str,
        movie: Optional[Any] = None
    ) -> Tuple[QualityStatusEnum, List[str]]:
        """Run deterministic checks and factual verification, returning status with issues."""
        issues: List[str] = []
        is_fatal = False

        # 1. Title validation
        if not article.title or len(article.title.strip()) < 10:
            issues.append("제목이 너무 짧거나 비어있습니다 (최소 10자 이상).")
            is_fatal = True

        # 2. Excerpt validation
        if not article.excerpt or len(article.excerpt.strip()) < 40:
            issues.append("발췌 요약문(excerpt)이 누락되었거나 너무 짧습니다 (최소 40자 이상).")

        # 3. Essential sections presence
        sections = {
            "도입부(introduction)": article.introduction,
            "기본정보(basic_info_summary)": article.basic_info_summary,
            "줄거리(spoiler_free_synopsis)": article.spoiler_free_synopsis,
            "출연진/감독(cast_and_director)": article.cast_and_director,
            "마무리(conclusion)": article.conclusion,
        }

        for name, content in sections.items():
            if not content or len(content.strip()) < 50:
                issues.append(f"필수 섹션 '{name}'의 내용이 너무 짧거나 비어있습니다.")
                is_fatal = True

        # 4. Total body length check (Korean characters >= 600 characters minimum)
        full_text = " ".join([
            article.introduction,
            article.basic_info_summary,
            article.spoiler_free_synopsis,
            article.cast_and_director,
            article.conclusion,
            " ".join(article.viewing_points),
            " ".join(article.recommended_for),
            " ".join(article.similar_movie_notes),
            " ".join([f"{f.question} {f.answer}" for f in article.faq])
        ])

        if len(full_text.strip()) < 600:
            issues.append(f"전체 본문 분량이 부족합니다 (현재 {len(full_text.strip())}자 / 최소 600자 권장).")

        # 5. Placeholders check
        for placeholder in FORBIDDEN_PLACEHOLDERS:
            if placeholder.lower() in full_text.lower():
                issues.append(f"작성 미완료 플레이스홀더 문자열('{placeholder}')이 감지되었습니다.")
                is_fatal = True

        # 6. Raw JSON leakage check
        for pattern in JSON_LEAKAGE_PATTERNS:
            if pattern.search(full_text):
                issues.append("AI 응답에 원본 JSON 마크다운이나 태그가 누출되었습니다.")
                is_fatal = True

        # 7. Secret / API key leakage check
        for pattern, _ in SENSITIVE_PATTERNS:
            if pattern.search(full_text):
                issues.append("본문에 API 키 또는 인증 토큰 형식의 민감 문자열이 누출되었습니다.")
                is_fatal = True

        # 8. Movie title consistency check
        # Check if the movie title or a substantial keyword appears in the title or introduction
        clean_movie_title = expected_movie_title.split("(")[0].strip()
        if clean_movie_title.lower() not in full_text.lower() and clean_movie_title.lower() not in article.title.lower():
            issues.append(f"생성된 글에 대상 영화 제목('{clean_movie_title}')이 언급되지 않았습니다.")

        # 9. List sections sanity checks
        if not article.viewing_points or len(article.viewing_points) < 2:
            issues.append("관람 포인트가 부족합니다 (최소 2개 이상 필요).")
        if not article.faq or len(article.faq) < 1:
            issues.append("자주 묻는 질문(FAQ)이 비어있습니다.")

        # 10. Fact checking against authoritative metadata
        if movie is not None:
            try:
                report = FactCheckService.extract_and_verify(article, movie)
                if report.has_fatal_conflict:
                    issues.append(f"치명적 팩트 불일치 감지: {report.summary}")
                    is_fatal = True
                elif report.conflict_count > 0:
                    for item in report.items:
                        if item.status == FactCheckStatus.CONFLICT:
                            issues.append(f"팩트체크 주의: {item.detail}")
            except Exception as fe:
                logger.warning("Fact check evaluation exception: %s", str(fe))

        # Determine status
        if is_fatal:
            status = QualityStatusEnum.FAIL
        elif len(issues) > 0:
            status = QualityStatusEnum.REVIEW
        else:
            status = QualityStatusEnum.PASS

        logger.info(
            "Quality gate evaluated article '%s': Status=%s, Issues=%d",
            article.title,
            status.value,
            len(issues)
        )
        return status, issues

    @staticmethod
    def evaluate_travel(
        article: Any,
        expected_destination: str,
        travel_item: Optional[Any] = None
    ) -> Tuple[QualityStatusEnum, List[str]]:
        """Run deterministic quality checks and fact verification on travel articles."""
        issues: List[str] = []
        is_fatal = False

        title = getattr(article, "title", "")
        excerpt = getattr(article, "excerpt", "")

        # 1. Title validation
        if not title or len(title.strip()) < 10:
            issues.append("여행 기사 제목이 너무 짧거나 비어있습니다 (최소 10자 이상).")
            is_fatal = True

        # 2. Excerpt validation
        if not excerpt or len(excerpt.strip()) < 30:
            issues.append("여행 발췌 요약문이 누락되었거나 너무 짧습니다 (최소 30자 이상).")

        # 3. Essential sections
        sections = {
            "도입부(introduction)": getattr(article, "introduction", ""),
            "개요(destination_overview)": getattr(article, "destination_overview", ""),
            "날씨/옷차림(weather_and_clothing)": getattr(article, "weather_and_clothing", ""),
            "경비(exchange_and_budget)": getattr(article, "exchange_and_budget", ""),
            "교통팁(transport_tips)": getattr(article, "transport_tips", ""),
            "총평(conclusion)": getattr(article, "conclusion", ""),
        }

        for name, content in sections.items():
            if not content or len(str(content).strip()) < 30:
                issues.append(f"여행 필수 섹션 '{name}'의 내용이 너무 짧거나 누락되었습니다.")
                is_fatal = True

        # 4. Total text length
        itinerary = getattr(article, "itinerary_days", [])
        spots = getattr(article, "must_visit_spots", [])
        faq = getattr(article, "faq", [])

        full_text = " ".join([
            title,
            excerpt,
            " ".join(str(v) for v in sections.values()),
            " ".join([f"{getattr(d, 'theme', '')} {' '.join(getattr(d, 'schedule', []))}" for d in itinerary]),
            " ".join([f"{getattr(s, 'name', '')} {getattr(s, 'description', '')}" for s in spots]),
            " ".join([f"{getattr(f, 'question', '')} {getattr(f, 'answer', '')}" for f in faq])
        ])

        if len(full_text.strip()) < 500:
            issues.append(f"여행 전체 본문 분량이 부족합니다 (현재 {len(full_text.strip())}자 / 최소 500자 권장).")

        # 5. Placeholders check
        for placeholder in FORBIDDEN_PLACEHOLDERS:
            if placeholder.lower() in full_text.lower():
                issues.append(f"미완성 플레이스홀더('{placeholder}')가 감지되었습니다.")
                is_fatal = True

        # 6. JSON leakage check
        for pattern in JSON_LEAKAGE_PATTERNS:
            if pattern.search(full_text):
                issues.append("AI 응답에 원본 JSON 마크다운/태그가 누출되었습니다.")
                is_fatal = True

        # 7. Secret / API key leakage check
        for pattern, _ in SENSITIVE_PATTERNS:
            if pattern.search(full_text):
                issues.append("본문에 API 키 또는 민감 문자열이 누출되었습니다.")
                is_fatal = True

        # 8. Destination name check (Robust extraction)
        clean_dest = re.sub(r'\[.*?\]', '', expected_destination)
        clean_dest = re.sub(r'\(.*?\)', '', clean_dest).strip().lower()
        bracket_match = re.search(r'\[(.*?)\]', expected_destination)
        bracket_word = bracket_match.group(1).split()[0].lower() if bracket_match else ""
        
        found = False
        candidates_to_check = [clean_dest]
        if bracket_word:
            candidates_to_check.append(bracket_word)
        if travel_item and hasattr(travel_item, "city") and travel_item.city:
            candidates_to_check.append(str(travel_item.city).lower())
        if travel_item and hasattr(travel_item, "destination") and travel_item.destination:
            candidates_to_check.append(str(travel_item.destination).lower())

        for c_word in candidates_to_check:
            if c_word and (c_word in full_text.lower() or c_word in title.lower()):
                found = True
                break

        if not found and (clean_dest or bracket_word):
            issues.append(f"여행지 핵심 키워드('{bracket_word or clean_dest}')가 본문에 충분히 반영되지 않았습니다.")

        # 9. Structure sanity checks
        if not itinerary or len(itinerary) < 2:
            issues.append("일정(itinerary) 일차가 부족합니다 (최소 2일차 이상 필요).")
        if not spots or len(spots) < 2:
            issues.append("추천 명소(spots)가 부족합니다 (최소 2개 이상 필요).")
        if not faq or len(faq) < 1:
            issues.append("자주 묻는 질문(FAQ)이 비어있습니다.")

        # 10. Travel Fact Checking
        if travel_item is not None:
            try:
                report = TravelFactCheckService.extract_and_verify(article, travel_item)
                if report.has_fatal_conflict:
                    issues.append(f"치명적 여행 팩트 불일치: {report.summary}")
                    is_fatal = True
                elif report.conflict_count > 0:
                    for item in report.items:
                        if item.status == FactCheckStatus.CONFLICT:
                            issues.append(f"여행 팩트 주의: {item.detail}")
            except Exception as e:
                logger.warning("Travel fact check exception: %s", str(e))

        if is_fatal:
            status = QualityStatusEnum.FAIL
        elif len(issues) > 0:
            status = QualityStatusEnum.REVIEW
        else:
            status = QualityStatusEnum.PASS

        logger.info("Travel quality gate evaluated '%s': Status=%s, Issues=%d", title, status.value, len(issues))
        return status, issues
