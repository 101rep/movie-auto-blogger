"""Universal Duplicate Prevention Guard for Multi-Site Blog System.

Provides multi-layer protection against duplicate titles and duplicate content:
1. Exact Title Deduplication (normalized text)
2. Fuzzy Title Similarity Check (Jaccard + SequenceMatcher threshold)
3. Topic/Entity Historical Exclusion (Cities, Products, Movies, Policies)
4. Dynamic Candidate Filtering with Zero Repetition
5. AI Prompt Anti-Repetition Hard Constraints
6. Pre-Publish Guard Interceptor
"""
import re
import difflib
from typing import Any, Dict, List, Optional, Tuple, Set
from sqlalchemy.orm import Session

from app.database.models import Post, PostStatusEnum
from app.utils.logging import get_logger

logger = get_logger("duplicate_guard")


class DuplicateGuardService:
    """Enterprise-grade service to prevent duplicate titles and content across all blogs."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Strip HTML tags/entities, punctuation, and normalize whitespace."""
        if not text:
            return ""
        import html
        cleaned = re.sub(r"<[^>]+>", " ", text)
        cleaned = html.unescape(cleaned)
        # Remove emojis, brackets, symbols, keep Korean, English, numbers
        cleaned = re.sub(r"[^\w\s가-힣0-9a-zA-Z]", " ", cleaned)
        return " ".join(cleaned.lower().split())

    @classmethod
    def calculate_similarity(cls, title1: str, title2: str) -> float:
        """Compute hybrid similarity between two titles:
        - SequenceMatcher ratio (character sequence)
        - Jaccard similarity (word set overlap)
        - Containment ratio (subset overlap)
        """
        n1 = cls.normalize_text(title1)
        n2 = cls.normalize_text(title2)
        if not n1 or not n2:
            return 0.0
        if n1 == n2:
            return 1.0

        # 1. SequenceMatcher character ratio
        seq_ratio = difflib.SequenceMatcher(None, n1, n2).ratio()

        # 2. Word-level sets
        words1 = set(n1.split())
        words2 = set(n2.split())
        if not words1 or not words2:
            return round(seq_ratio, 3)

        # 3. Filter out generic Korean template/boilerplate stop words
        STOP_WORDS = {
            "솔직", "스펙", "비교", "및", "실사용자", "실사용", "장단점", "총정리",
            "리뷰", "후기", "추천", "가이드", "정리", "총괄", "완벽", "정보",
            "방법", "신청", "안내", "소개", "내돈내산", "총평", "특징", "포인트",
            # 영화 관련
            "영화", "줄거리", "결말", "출연진", "관람평", "등장인물", "해석", "쿠키",
            "평점", "관객수", "시리즈", "다시보기", "예고편", "감상평", "개봉일",
            # 여행 관련
            "여행", "일정", "코스", "경비", "숙소", "호텔", "맛집", "가볼만한곳",
            "명소", "비용", "꿀팁", "지도", "준비물", "예약", "패스", "투어",
            # 복지/정책 관련
            "지원금", "신청방법", "자격조건", "지급일", "혜택", "지원", "정책",
            "개정판", "최신", "개정", "대상", "금액", "기준", "조건",
            # 시사/뉴스 관련
            "속보", "이슈", "전망", "영향", "이유", "해설", "현황", "분석"
        }
        cw1 = words1 - STOP_WORDS
        cw2 = words2 - STOP_WORDS

        # If both titles have identifiable content words
        if cw1 and cw2:
            common_cw = cw1 & cw2
            # Zero overlap in content words => completely different subject!
            if not common_cw:
                return round(min(seq_ratio * 0.25, 0.25), 3)
            # When content words overlap, compute similarity strictly on content words
            cw_jaccard = len(common_cw) / len(cw1 | cw2)
            cw_seq = difflib.SequenceMatcher(None, " ".join(sorted(cw1)), " ".join(sorted(cw2))).ratio()
            return round(max(cw_jaccard, cw_seq), 3)

        common_count = len(words1 & words2)
        union_count = len(words1 | words2)
        min_count = min(len(words1), len(words2))

        jaccard = common_count / union_count if union_count > 0 else 0.0
        containment = common_count / min_count if min_count > 0 else 0.0

        # Hybrid score captures sequence, word overlap, and concept containment
        score = max(
            seq_ratio,
            0.35 * seq_ratio + 0.65 * jaccard,
            0.85 * containment
        )
        return round(score, 3)

    @staticmethod
    def get_existing_titles(db: Session, site_id: int) -> List[str]:
        """Fetch all active, scheduled, and published post titles for a site (including legacy unassigned posts)."""
        from sqlalchemy import or_
        posts = db.query(Post.title).filter(
            or_(Post.site_id == site_id, Post.site_id.is_(None)),
            Post.status.in_([
                PostStatusEnum.PUBLISHED.value,
                PostStatusEnum.SCHEDULED.value,
                PostStatusEnum.APPROVED.value,
                PostStatusEnum.REVIEW.value
            ])
        ).all()
        return [p[0] for p in posts if p[0]]

    @classmethod
    def is_title_duplicate(
        cls,
        db: Session,
        site_id: int,
        new_title: str,
        threshold: float = 0.55
    ) -> Tuple[bool, Optional[str], float]:
        """Check if `new_title` is too similar to any existing post on this site.
        
        Returns:
            (is_duplicate, matching_existing_title, similarity_score)
        """
        existing_titles = cls.get_existing_titles(db, site_id)
        norm_new = cls.normalize_text(new_title)

        # Core movie entity check for immediate duplicate detection
        core_new_movie = cls.extract_core_entity("MOVIE", new_title)

        highest_score = 0.0
        matched_title = None

        for ex_title in existing_titles:
            norm_ex = cls.normalize_text(ex_title)
            # Exact normalized match
            if norm_new == norm_ex:
                return True, ex_title, 1.0

            # Movie entity match: if both contain the exact same movie title
            if core_new_movie and len(core_new_movie) >= 2:
                core_ex_movie = cls.extract_core_entity("MOVIE", ex_title)
                if core_ex_movie and (core_new_movie == core_ex_movie or (len(core_new_movie) >= 3 and core_new_movie in core_ex_movie)):
                    return True, ex_title, 1.0

            score = cls.calculate_similarity(new_title, ex_title)
            if score > highest_score:
                highest_score = score
                matched_title = ex_title

        if highest_score >= threshold:
            return True, matched_title, highest_score

        return False, None, highest_score

    @classmethod
    def extract_core_entity(cls, vertical: str, text: str) -> Optional[str]:
        """Extract primary entity/topic from candidate (e.g., city name, movie name, product name)."""
        v = vertical.upper()
        norm = cls.normalize_text(text)

        if v == "MOVIE":
            cleaned_movie = re.sub(r"^(영화|극영화|신작|개봉작|인기작|넷플릭스|디즈니\+?|디즈니플러스|극장판)\s*", "", text).strip()
            boilerplate_keywords = [
                "개봉일", "줄거리", "출연진", "등장인물", "정보", "총정리", "평점", 
                "관람평", "솔직 후기", "후기", "리뷰", "결말", "쿠키", "포인트", "예고편", "기본정보"
            ]
            pattern = r"[\s,\-_|:]+(" + "|".join(boilerplate_keywords) + r")(?:[과와의은는이가을를및\s]|$).*$"
            cleaned_movie = re.sub(pattern, "", cleaned_movie, flags=re.IGNORECASE).strip()
            cleaned_movie = re.sub(r"[,:\-–—\(\)\[\]]", " ", cleaned_movie).strip()
            core = " ".join(cleaned_movie.split())
            if len(core) >= 2:
                return core

        if v == "TRAVEL":
            # Common major destinations
            known_destinations = [
                "오사카", "도쿄", "후쿠오카", "교토", "삿포로", "오키나와", "나고야",
                "다낭", "방콕", "나트랑", "푸꾸옥", "싱가포르", "타이베이", "가오슝",
                "홍콩", "마카오", "발리", "세부", "보라카이", "괌", "사이판", "하와이",
                "제주도", "부산", "강릉", "속초", "여수", "경주", "전주", "통영", "포항"
            ]
            for dest in known_destinations:
                if dest in text or dest in norm:
                    return dest

        elif v == "PRODUCT":
            known_products = [
                "버티컬 마우스", "모니터 조명", "스크린바", "스탠바이미", "로봇청소기",
                "에어프라이어", "가습기", "제습기", "무선청소기", "헤어드라이기", "블루투스 스피커"
            ]
            for prod in known_products:
                if prod in text or prod in norm:
                    return prod

        elif v == "NEWS":
            known_news = [
                "기준금리", "금리", "환율", "가계부채", "스트레스 DSR", "주택담보대출",
                "청약", "부동산", "신생아 특례대출", "전세사기", "재건축", "인공지능",
                "AI", "반도체", "온디바이스", "건강보험", "실손보험", "국민연금",
                "연말정산", "부가세", "종부세", "취득세", "전기요금"
            ]
            for news_topic in known_news:
                if news_topic in text or news_topic in norm:
                    return news_topic

        elif v == "WELFARE":
            known_welfare = [
                "청년도약계좌", "청년월세", "국민취업지원제도", "K-패스", "기후동행카드",
                "국민연금", "기초연금", "부모급여", "아동수당", "소상공인", "새출발기금",
                "전기요금 특별지원", "에너지바우처", "디딤돌대출", "버팀목전세대출",
                "신생아 특례대출", "희망리턴패키지", "내일채움공제", "알뜰교통카드"
            ]
            for wel_topic in known_welfare:
                if wel_topic in text or wel_topic in norm:
                    return wel_topic

        return None

    @classmethod
    def is_topic_already_covered(
        cls,
        db: Session,
        site_id: int,
        vertical: str,
        title_or_topic: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if the core entity/city has already been posted to prevent repetitive destination/product posts."""
        entity = cls.extract_core_entity(vertical, title_or_topic)
        if not entity:
            return False, None

        existing_titles = cls.get_existing_titles(db, site_id)
        for ex in existing_titles:
            if entity in ex:
                return True, f"'{entity}' 관련 글이 이미 존재합니다: [{ex}]"

        return False, None

    @classmethod
    def filter_unique_candidates(
        cls,
        db: Session,
        site_id: int,
        vertical: str,
        candidates: List[Any],
        limit: int = 4
    ) -> List[Any]:
        """Filter candidate list ensuring ZERO duplication of titles, external_ids, or core entities."""
        existing_posts = db.query(Post.external_id, Post.title).filter(
            Post.site_id == site_id,
            Post.status.in_([
                PostStatusEnum.PUBLISHED.value,
                PostStatusEnum.SCHEDULED.value,
                PostStatusEnum.APPROVED.value,
                PostStatusEnum.REVIEW.value
            ])
        ).all()

        existing_ext_ids: Set[str] = {str(p[0]) for p in existing_posts if p[0]}
        existing_titles = [p[1] for p in existing_posts if p[1]]

        eligible: List[Any] = []
        covered_entities_in_batch: Set[str] = set()

        for cand in candidates:
            c_ext_id = str(getattr(cand, "external_id", getattr(cand, "id", "")))
            c_title = getattr(cand, "title", str(cand))

            # 1. Check external ID
            if c_ext_id and c_ext_id in existing_ext_ids:
                logger.info("Discarding candidate '%s' (External ID %s already used)", c_title, c_ext_id)
                continue

            # 2. Check title similarity
            is_dup, matched_title, score = cls.is_title_duplicate(db, site_id, c_title, threshold=0.55)
            if is_dup:
                logger.info("Discarding candidate '%s' (Similar to existing '%s', score=%.2f)", c_title, matched_title, score)
                continue

            # 3. Check core entity (e.g. city/destination)
            entity = cls.extract_core_entity(vertical, c_title)
            if entity:
                # Check against historical posts
                is_covered, reason = cls.is_topic_already_covered(db, site_id, vertical, c_title)
                if is_covered:
                    logger.info("Discarding candidate '%s' (%s)", c_title, reason)
                    continue
                # Check within this current batch
                if entity in covered_entities_in_batch:
                    logger.info("Discarding candidate '%s' (Entity '%s' already in current batch)", c_title, entity)
                    continue
                covered_entities_in_batch.add(entity)

            eligible.append(cand)
            if len(eligible) >= limit:
                break

        logger.info(
            "DuplicateGuard: Screened %d candidates for site [%d] -> %d eligible unique candidates.",
            len(candidates), site_id, len(eligible)
        )
        return eligible

    @classmethod
    def get_anti_duplication_prompt_constraint(cls, db: Session, site_id: int, limit: int = 15) -> str:
        """Generate a strict negative constraint section for the LLM prompt with recent titles."""
        titles = cls.get_existing_titles(db, site_id)
        if not titles:
            return ""

        recent = titles[-limit:]
        titles_formatted = "\n".join([f"- {t}" for t in reversed(recent)])

        return f"""
[⚠️ 절대 준수: 기존 포스팅 중복 및 기시감 방지 가드레일 (Anti-Duplication Guard)]
다음은 이 블로그에 이미 작성되어 발행/예약된 최근 글 제목 목록입니다:
{titles_formatted}

[중복 방지 4대 필수 지침]:
1. 위 목록에 등장하는 핵심 소재, 특정 여행지(도시/국가), 상품 모델, 영화, 정책 주제는 절대로 다시 반복하지 마십시오.
2. 만약 동일한 카테고리를 다루더라도, 기존 글과 100% 다른 전혀 새로운 세부 장소, 새로운 관점, 독창적인 소제목을 구성하십시오.
3. 제목 생성 시 기존 제목의 어휘나 문장 구조를 모방하지 말고 독창적인 검색 후킹 타이틀을 작성하십시오.
4. 본문 내용 역시 기존 글과 표현이나 추천 코스가 겹치지 않도록 신선한 정보를 풍성하게 담으십시오.
"""

    @classmethod
    def validate_pre_publish(
        cls,
        db: Session,
        site_id: int,
        title: str,
        content: str
    ) -> Tuple[bool, Optional[str]]:
        """Pre-publish hard check right before calling WordPress REST API."""
        is_dup, match, score = cls.is_title_duplicate(db, site_id, title, threshold=0.60)
        if is_dup:
            return False, f"중복 제목 감지: 기존 글 '{match}' (유사도: {score*100:.1f}%)와 중복되어 발행이 중단되었습니다."

        return True, None


duplicate_guard = DuplicateGuardService()
