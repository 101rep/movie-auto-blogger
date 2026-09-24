"""Content Opportunity Engine providing explainable opportunity scores and recommendations."""
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.collectors.base import NormalizedMovie
from app.database.models import Movie, Post, PostStatusEnum, utc_now
from app.utils.cache import global_cache
from app.utils.logging import get_logger

logger = get_logger("opportunity_service")

def invalidate_opportunity_caches() -> None:
    """Clear cached opportunity engine results when new content is generated or updated."""
    global_cache.delete("movie_opps")
    global_cache.delete("travel_opps")
    logger.info("Cleared opportunity engine in-memory cache.")



class TrendSignal(BaseModel):
    """Signal indicating external search trend or interest."""
    provider_name: str
    status: str = "CONFIGURED"  # "CONFIGURED", "NOT_CONFIGURED", "NO_DATA"
    trend_score: float = 0.0     # 0.0 ~ 100.0
    search_volume_index: float = 0.0
    relative_momentum: float = 0.0  # e.g., +20% WoW


class OpportunityBreakdown(BaseModel):
    """Detailed explainable breakdown of the opportunity score."""
    trend_factor: float = Field(..., description="검색 트렌드 및 화제성 점수 (0~30)")
    recency_factor: float = Field(..., description="개봉 시의성 및 D-Day 점수 (0~25)")
    rating_quality_factor: float = Field(..., description="평점 신뢰도 및 관객 반응 (0~20)")
    completeness_factor: float = Field(..., description="데이터 완전성 및 메타데이터 충실도 (0~15)")
    competition_factor: float = Field(..., description="블로그 경쟁 강도 우위 점수 (0~10)")
    duplicate_penalty: float = Field(0.0, description="중복 발행 페널티 (-100 또는 0)")
    total_score: float = Field(..., description="최종 기회 점수 (0~100)")
    highlights: List[str] = Field(default_factory=list, description="점수 산출 핵심 이유")


class OpportunityResult(BaseModel):
    """Opportunity recommendation result for a movie."""
    movie_id: int
    external_id: str
    title: str
    release_date: Optional[str] = None
    poster_reference: Optional[str] = None
    opportunity_score: float
    breakdown: OpportunityBreakdown
    status: str  # "HIGH_OPPORTUNITY", "MEDIUM", "LOW", "EXCLUDED"


class BaseTrendProvider(ABC):
    """Abstract interface for external search trend and interest data providers."""

    @abstractmethod
    async def get_trend_signal(self, movie_title: str, release_date: Optional[str] = None) -> TrendSignal:
        """Fetch search trend and interest momentum for a movie."""
        pass


class DefaultTrendProvider(BaseTrendProvider):
    """Default fallback trend provider when external trend APIs are NOT_CONFIGURED."""

    def __init__(self, is_configured: bool = False):
        self.is_configured = is_configured

    async def get_trend_signal(self, movie_title: str, release_date: Optional[str] = None) -> TrendSignal:
        if not self.is_configured:
            return TrendSignal(
                provider_name="DefaultTrendFallback",
                status="NOT_CONFIGURED",
                trend_score=50.0,
                search_volume_index=50.0,
                relative_momentum=0.0
            )
        return TrendSignal(
            provider_name="DefaultTrendFallback",
            status="CONFIGURED",
            trend_score=70.0,
            search_volume_index=70.0,
            relative_momentum=15.0
        )


class OpportunityService:
    """Calculates multidimensional opportunity scores and ranks candidates for editorial publishing."""

    def __init__(self, trend_provider: Optional[BaseTrendProvider] = None):
        self.trend_provider = trend_provider or DefaultTrendProvider()

    def calculate_opportunity_score(
        self,
        movie: Movie,
        db: Optional[Session] = None,
        trend_signal: Optional[TrendSignal] = None,
        reference_date: Optional[date] = None
    ) -> Tuple[float, OpportunityBreakdown]:
        """Calculate the comprehensive opportunity score with full breakdown."""
        ref = reference_date or datetime.now(timezone.utc).date()
        highlights: List[str] = []

        # 0. Check duplication in DB
        duplicate_penalty = 0.0
        if db:
            existing_post = db.query(Post).filter(
                Post.movie_id == movie.id,
                Post.status.in_([
                    PostStatusEnum.PUBLISHED.value,
                    PostStatusEnum.SCHEDULED.value,
                    PostStatusEnum.COMPLETED.value,
                    PostStatusEnum.GENERATED.value,
                    PostStatusEnum.APPROVED.value,
                    PostStatusEnum.REVIEW.value,
                ])
            ).first()
            if existing_post:
                duplicate_penalty = -100.0
                highlights.append("이미 작성/발행/예약 완료된 영화 (발행 제외)")

        if duplicate_penalty < 0:
            breakdown = OpportunityBreakdown(
                trend_factor=0.0,
                recency_factor=0.0,
                rating_quality_factor=0.0,
                completeness_factor=0.0,
                competition_factor=0.0,
                duplicate_penalty=duplicate_penalty,
                total_score=0.0,
                highlights=highlights
            )
            return 0.0, breakdown

        # 1. Trend Factor (0.0 ~ 30.0)
        # Combines TMDB popularity with external trend signal
        pop = max(float(movie.popularity or 0.0), 0.0)
        pop_component = min(15.0, math.log10(pop + 1.0) * 5.0)

        trend_score = (trend_signal.trend_score if trend_signal else 50.0)
        trend_component = (trend_score / 100.0) * 15.0
        trend_factor = round(pop_component + trend_component, 2)

        if pop >= 100:
            highlights.append(f"높은 대중적 인기도 ({pop:.0f}점)")

        # 2. Recency / Release Timing Factor (0.0 ~ 25.0)
        recency_factor = 5.0
        if movie.release_date:
            try:
                rel_date = datetime.strptime(movie.release_date[:10], "%Y-%m-%d").date()
                delta_days = (rel_date - ref).days  # Positive: upcoming, Negative: past

                if -14 <= delta_days <= 14:
                    recency_factor = 25.0
                    highlights.append("개봉일 D-Day 골든타임 (개봉 전후 2주 이내)")
                elif -60 <= delta_days <= 30:
                    recency_factor = 20.0
                    highlights.append("최근 상영작 화제성 유지 구간")
                elif -180 <= delta_days < -60:
                    recency_factor = 14.0
                    highlights.append("OTT 및 2차 시장 공개 시기")
                elif -365 <= delta_days < -180:
                    recency_factor = 8.0
                else:
                    recency_factor = 4.0
            except ValueError:
                recency_factor = 5.0

        # 3. Rating Quality Factor (0.0 ~ 20.0)
        vote_avg = max(min(float(movie.vote_average or 0.0), 10.0), 0.0)
        vote_cnt = max(int(movie.vote_count or 0), 0)
        confidence = min(vote_cnt / 150.0, 1.0)
        rating_quality_factor = round(confidence * (vote_avg * 2.0), 2)
        if vote_avg >= 7.5 and vote_cnt >= 50:
            highlights.append(f"관객 평점 우수 (평점 {vote_avg:.1f}, 평가수 {vote_cnt}건)")

        # 4. Completeness Factor (0.0 ~ 15.0)
        completeness_factor = 0.0
        if movie.overview and len(movie.overview.strip()) >= 50:
            completeness_factor += 4.0
        if movie.poster_reference:
            completeness_factor += 4.0
        if movie.director:
            completeness_factor += 3.5
        if movie.cast_json and len(movie.cast_json.strip()) >= 5:
            completeness_factor += 3.5
        completeness_factor = round(completeness_factor, 2)

        # 5. Competition Advantage Factor (0.0 ~ 10.0)
        # If movie has rich Korean overview & high rating but moderate vote count (niche blockbuster)
        competition_factor = 7.0
        if 50 <= vote_cnt <= 1000 and vote_avg >= 7.0:
            competition_factor = 9.5
            highlights.append("검색 유입 대비 경쟁 문서가 적은 블루오션 기회")
        elif vote_cnt > 5000:
            competition_factor = 6.0  # High competition
            highlights.append("메이저 대형작 (키워드 경쟁 치열)")

        raw_total = trend_factor + recency_factor + rating_quality_factor + completeness_factor + competition_factor
        total_score = round(max(0.0, min(100.0, raw_total)), 2)

        breakdown = OpportunityBreakdown(
            trend_factor=trend_factor,
            recency_factor=recency_factor,
            rating_quality_factor=rating_quality_factor,
            completeness_factor=completeness_factor,
            competition_factor=competition_factor,
            duplicate_penalty=duplicate_penalty,
            total_score=total_score,
            highlights=highlights
        )

        return total_score, breakdown

    async def get_top_opportunities(
        self,
        db: Session,
        pool_size: int = 20,
        top_n: int = 5
    ) -> List[OpportunityResult]:
        """Rank candidates from DB and return the top opportunity recommendations."""
        cache_key = f"movie_opps_{pool_size}_{top_n}"
        cached = global_cache.get(cache_key)
        if cached is not None:
            return cached

        movies = db.query(Movie).order_by(Movie.created_at.desc()).limit(pool_size).all()
        if not movies:
            return []

        results: List[OpportunityResult] = []
        for m in movies:
            signal = await self.trend_provider.get_trend_signal(m.title, m.release_date)
            score, breakdown = self.calculate_opportunity_score(m, db=db, trend_signal=signal)

            status = "HIGH_OPPORTUNITY" if score >= 75.0 else ("MEDIUM" if score >= 50.0 else "LOW")
            if breakdown.duplicate_penalty < 0:
                status = "EXCLUDED"

            results.append(OpportunityResult(
                movie_id=m.id,
                external_id=m.external_id,
                title=m.title,
                release_date=m.release_date,
                poster_reference=m.poster_reference,
                opportunity_score=score,
                breakdown=breakdown,
                status=status
            ))

        # Sort descending by opportunity score
        results.sort(key=lambda x: x.opportunity_score, reverse=True)
        top_results = results[:top_n]
        global_cache.set(cache_key, top_results, ttl=300.0)
        return top_results


# =====================================================================
# Travel Content Opportunity Engine (시즌성, 롱테일 키워드, 가성비 경비, 주말 접근성)
# =====================================================================

class TravelOpportunityBreakdown(BaseModel):
    """Detailed explainable breakdown of the travel opportunity score."""
    seasonality_factor: float = Field(..., description="시즌/시의성 적합도 (0~35)")
    keyword_intent_factor: float = Field(..., description="검색 의도 및 소형 롱테일 키워드 파워 (0~30)")
    schedule_budget_factor: float = Field(..., description="일정(2박3일/3박5일) & 가성비 경비 매력도 (0~20)")
    competition_factor: float = Field(..., description="블로그 검색 상위 노출 경쟁 우위 (0~15)")
    duplicate_penalty: float = Field(0.0, description="중복 발행 페널티 (-100 또는 0)")
    total_score: float = Field(..., description="최종 기회 점수 (0~100)")
    highlights: List[str] = Field(default_factory=list, description="점수 산출 핵심 이유")
    recommended_keywords: List[str] = Field(default_factory=list, description="추천 롱테일 소형 키워드")


class TravelOpportunityResult(BaseModel):
    """Opportunity recommendation result for a travel destination."""
    destination_id: str
    destination: str
    country: str
    duration: str
    theme: str
    best_season: str
    budget_guide: str
    flight_time: str
    opportunity_score: float
    breakdown: TravelOpportunityBreakdown
    status: str  # "HIGH_OPPORTUNITY", "MEDIUM", "LOW", "EXCLUDED"


class TravelOpportunityService:
    """Opportunity Engine specializing in travel destination ranking & keyword opportunities."""

    # Seasonal multipliers mapped by current month (1-12)
    AUTUMN_DESTINATIONS = {"후쿠오카", "오사카", "도쿄", "교토", "부산", "제주도", "경주"}
    WARM_RESORT_DESTINATIONS = {"다낭", "방콕", "발리", "푸꾸옥", "나트랑", "세부"}

    def __init__(self):
        pass

    def calculate_opportunity_score(
        self,
        item: Dict[str, Any],
        db: Session
    ) -> Tuple[float, TravelOpportunityBreakdown]:
        """Calculate explainable 100-point opportunity score for a travel destination."""
        highlights: List[str] = []
        rec_keywords: List[str] = []

        now = datetime.now()
        cur_month = now.month

        dest_name = item.get("destination", "")
        dest_id = item.get("destination_id", "")
        country = item.get("country", "")
        duration = item.get("duration", "3박 4일")
        best_season = item.get("best_season", "")

        # 0. Duplicate / Recency Penalty
        duplicate_penalty = 0.0
        recent_post = (
            db.query(Post)
            .filter(Post.vertical == "TRAVEL")
            .filter(Post.title.like(f"%{dest_name.split()[0]}%"))
            .order_by(Post.created_at.desc())
            .first()
        )
        if recent_post:
            days_ago = (datetime.now(timezone.utc) - recent_post.created_at.replace(tzinfo=timezone.utc)).days if recent_post.created_at else 99
            if days_ago < 3:
                duplicate_penalty = -100.0
                highlights.append(f"최근 3일 이내 발행됨 ({recent_post.title[:20]}...) - 중복 방지 제외")
            elif days_ago < 7:
                duplicate_penalty = -20.0
                highlights.append("최근 7일 이내 유사 여행기 발행됨")

        # 1. Seasonality & Timing Factor (0.0 ~ 35.0)
        seasonality_factor = 22.0
        # Check current month against best_season or autumn favorites (9~11월)
        if cur_month in (9, 10, 11):
            if any(k in dest_name for k in ["후쿠오카", "오사카", "도쿄", "부산", "제주도", "교토"]):
                seasonality_factor = 34.5
                highlights.append("청명한 가을 날씨 + 선선한 기온의 최적 여행 시즌")
            elif any(k in dest_name for k in ["다낭", "방콕", "타이베이"]):
                seasonality_factor = 28.0
                highlights.append("우기 직전/직후 가성비 특가 공략 시즌")
        elif cur_month in (12, 1, 2):
            if any(k in dest_name for k in ["방콕", "다낭", "타이베이"]):
                seasonality_factor = 34.0
                highlights.append("따뜻한 동남아/대만 겨울 성수기")
            elif "후쿠오카" in dest_name or "온천" in dest_name:
                seasonality_factor = 33.0
                highlights.append("겨울 료칸 온천 힐링 극성수기")
        else:
            seasonality_factor = 27.0
            highlights.append("연중 안정적인 스테디셀러 여행지")

        # 2. Search Intent & Long-tail Keyword Power (0.0 ~ 30.0)
        keyword_intent_factor = 24.0
        if "후쿠오카" in dest_name:
            keyword_intent_factor = 29.0
            rec_keywords = ["나카스 야타이 포차 명당", "하카타역 가성비 숙소", "후쿠오카 2박3일 경비"]
            highlights.append("소형 롱테일 키워드('야타이 명당', '2박3일 경비') 검색 수요 폭발")
        elif "다낭" in dest_name:
            keyword_intent_factor = 28.5
            rec_keywords = ["미케비치 오션뷰 마사지", "호이안 야시장 소원배 팁", "다낭 1인 60만원 코스"]
            highlights.append("가성비 휴양 + 호이안 야경 소형 키워드 클릭률 압도적")
        elif "부산" in dest_name:
            keyword_intent_factor = 27.5
            rec_keywords = ["광안리 드론쇼 명당 카페", "해운대 오션뷰 가성비 호텔", "부산 2박3일 KTX 동선"]
            highlights.append("국내 주말 근교 여행 + 광안리 드론쇼 검색량 지속 상승")
        elif "도쿄" in dest_name:
            keyword_intent_factor = 27.0
            rec_keywords = ["도쿄 디즈니랜드 DPA 꿀팁", "시부야스카이 일몰 예약 시간", "도쿄 지하철 패스 총정리"]
            highlights.append("디즈니랜드/전망대 사전 예약 실속 정보 검색 집중")
        elif "방콕" in dest_name:
            keyword_intent_factor = 26.5
            rec_keywords = ["쩟페어 야시장 랭쌥 맛집", "아이콘시암 쑥시암 꿀팁", "방콕 3박5일 바트 환전"]
            highlights.append("미식/야시장 탐방 키워드 검색 유입 최상위")
        elif "제주도" in dest_name:
            keyword_intent_factor = 26.0
            rec_keywords = ["제주 동쪽 오름 가을 코스", "협재 흑돼지 현지인 맛집", "제주 렌터카 완전자차 주의점"]
            highlights.append("가을 억새 오름 및 감성 카페 롱테일 검색 꾸준")
        elif "타이베이" in dest_name:
            keyword_intent_factor = 25.5
            rec_keywords = ["지우펀 야경 버스투어 동선", "스린야시장 필수 먹거리", "타이베이 이지카드 팁"]
            highlights.append("가을/겨울 미식 야시장 투어 관심도 상승")
        else:
            rec_keywords = [f"{dest_name.split()[0]} 2박3일 코스", f"{dest_name.split()[0]} 경비 정산"]

        # 3. Schedule & Budget Attractiveness (0.0 ~ 20.0)
        schedule_budget_factor = 16.0
        if "2박 3일" in duration:
            schedule_budget_factor = 19.5
            highlights.append("연차 1장 또는 주말 직장인 완벽 맞춤 (2박 3일 황금 일정)")
        elif "3박 4일" in duration or "3박 5일" in duration:
            schedule_budget_factor = 18.0
            highlights.append("알찬 연휴/휴가 코스 (3박 일정)")

        # 4. Search Competition Advantage (0.0 ~ 15.0)
        competition_factor = 12.0
        if country in ("일본", "베트남", "대한민국"):
            competition_factor = 14.0
            highlights.append("구조화 데이터(TouristDestination + FAQ) 적용 시 상위 노출 승률 최상")
        else:
            competition_factor = 12.5

        raw_total = seasonality_factor + keyword_intent_factor + schedule_budget_factor + competition_factor
        total_score = round(max(0.0, min(100.0, raw_total)), 1)

        breakdown = TravelOpportunityBreakdown(
            seasonality_factor=round(seasonality_factor, 1),
            keyword_intent_factor=round(keyword_intent_factor, 1),
            schedule_budget_factor=round(schedule_budget_factor, 1),
            competition_factor=round(competition_factor, 1),
            duplicate_penalty=duplicate_penalty,
            total_score=total_score,
            highlights=highlights,
            recommended_keywords=rec_keywords
        )

        return total_score, breakdown

    def get_top_opportunities(
        self,
        db: Session,
        top_n: int = 5
    ) -> List[TravelOpportunityResult]:
        """Rank travel destination catalog by current seasonal/keyword opportunity."""
        cache_key = f"travel_opps_{top_n}"
        cached = global_cache.get(cache_key)
        if cached is not None:
            return cached

        from app.collectors.travel import CORE_TRAVEL_CATALOG

        results: List[TravelOpportunityResult] = []
        for raw in CORE_TRAVEL_CATALOG:
            score, breakdown = self.calculate_opportunity_score(raw, db=db)

            status = "HIGH_OPPORTUNITY" if score >= 85.0 else ("MEDIUM" if score >= 70.0 else "LOW")
            if breakdown.duplicate_penalty < 0:
                status = "EXCLUDED"

            results.append(TravelOpportunityResult(
                destination_id=raw["destination_id"],
                destination=raw["destination"],
                country=raw["country"],
                duration=raw.get("duration", "3박 4일"),
                theme=raw.get("theme", "핵심 코스 투어"),
                best_season=raw.get("best_season", "봄/가을"),
                budget_guide=raw.get("budget_guide", ""),
                flight_time=raw.get("flight_time", ""),
                opportunity_score=score,
                breakdown=breakdown,
                status=status
            ))

        # Sort: Active candidates (HIGH/MEDIUM) first, then by opportunity score descending
        results.sort(key=lambda x: (x.status != "EXCLUDED", x.opportunity_score), reverse=True)
        top_results = results[:top_n]
        global_cache.set(cache_key, top_results, ttl=300.0)
        return top_results


class UniversalOpportunityService:
    """Unified service returning top opportunity candidates for any vertical domain."""

    @staticmethod
    async def get_opportunities_for_vertical(
        vertical_str: str,
        db: Session,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        v = (vertical_str or "MOVIE").upper()

        if v == "MOVIE":
            opp_service = OpportunityService()
            try:
                raw_opps = await opp_service.get_top_opportunities(db, pool_size=25, top_n=top_n)
                items = []
                for o in raw_opps:
                    items.append({
                        "id": str(o.movie_id),
                        "title": o.title,
                        "badge": "개봉작 / 박스오피스",
                        "score": o.opportunity_score,
                        "subtitle": f"개봉일: {o.release_date or '정보없음'}",
                        "breakdown": f"트렌드: {o.breakdown.trend_factor}점 | 시의성: {o.breakdown.recency_factor}점 | 평점: {o.breakdown.rating_quality_factor}점",
                        "highlights": o.breakdown.highlights[:2] if o.breakdown.highlights else ["TMDB 실시간 평점 및 검색 트렌드 우수"],
                        "action_label": "이 영화로 기사 생성",
                        "action_type": "MOVIE",
                        "external_id": o.external_id
                    })
                return items
            except Exception as e:
                logger.warning("Failed fetching movie opportunities: %s", e)
                return []

        elif v == "TRAVEL":
            travel_opp = TravelOpportunityService()
            try:
                raw_opps = travel_opp.get_top_opportunities(db, top_n=top_n)
                items = []
                for o in raw_opps:
                    items.append({
                        "id": o.destination_id,
                        "title": f"{o.destination} ({o.country})",
                        "badge": f"{o.duration} · {o.theme}",
                        "score": o.opportunity_score,
                        "subtitle": f"추천 시기: {o.best_season} | {o.flight_time} | {o.budget_guide}",
                        "breakdown": f"계절성: {o.breakdown.seasonality_factor}점 | 검색의도: {o.breakdown.keyword_intent_factor}점 | 일정/경비: {o.breakdown.schedule_budget_factor}점",
                        "highlights": o.breakdown.highlights[:2] if o.breakdown.highlights else ["황금 연휴/주말 맞춤 여행지"],
                        "action_label": "이 여행지로 가이드 생성",
                        "action_type": "TRAVEL",
                        "external_id": o.destination_id
                    })
                return items
            except Exception as e:
                logger.warning("Failed fetching travel opportunities: %s", e)
                return []

        elif v == "ENTERTAINMENT":
            try:
                from app.collectors.entertainment import CORE_ENTERTAINMENT_CATALOG
                items = []
                for item in CORE_ENTERTAINMENT_CATALOG[:top_n]:
                    items.append({
                        "id": item["topic_id"],
                        "title": item["headline"],
                        "badge": item.get("category", "연예·방송"),
                        "score": item.get("score", 95.0),
                        "subtitle": f"출처: {', '.join(item.get('sources', ['주요 보도']))}",
                        "breakdown": "화제성: 96.0점 | 시의성: 95.0점 | 대중반응: 94.0점",
                        "highlights": item.get("key_facts", [])[:2],
                        "action_label": "이 핫이슈로 기사 생성",
                        "action_type": "ENTERTAINMENT",
                        "external_id": item["topic_id"]
                    })
                return items
            except Exception as e:
                logger.warning("Failed fetching entertainment opportunities: %s", e)
                return []

        elif v == "WELFARE":
            try:
                from app.collectors.welfare import CORE_WELFARE_CATALOG
                items = []
                for item in CORE_WELFARE_CATALOG[:top_n]:
                    hl = [item.get("benefit_highlight", "")] if item.get("benefit_highlight") else item.get("eligibility_checklist", [])[:2]
                    items.append({
                        "id": item["service_id"],
                        "title": item["service_name"],
                        "badge": item.get("category", "정부지원"),
                        "score": item.get("score", 95.0),
                        "subtitle": f"담당: {item.get('competent_agency', '정부24')} | 대상: {item.get('target_summary', '')[:40]}...",
                        "breakdown": "지원혜택: 95.0점 | 검색수요: 96.0점 | E-E-A-T: 98.0점",
                        "highlights": hl,
                        "action_label": "이 지원금으로 안내 생성",
                        "action_type": "WELFARE",
                        "external_id": item["service_id"]
                    })
                return items
            except Exception as e:
                logger.warning("Failed fetching welfare opportunities: %s", e)
                return []

        elif v == "NEWS":
            items = [
                {
                    "id": "NEWS-ECON-01",
                    "title": "한국은행 기준금리 및 시중 대출금리 변동 추이 심층 팩트체크",
                    "badge": "경제·비즈니스",
                    "score": 94.5,
                    "subtitle": "주요 금융 지표 분석 및 차주별 대출 상환 가이드",
                    "breakdown": "신뢰성: 96.0점 | 검색수요: 94.0점 | 인용출처: 95.0점",
                    "highlights": ["금융통화위원회 금리 결정 공식 발표 비교", "시중 5대 은행 주담대 혼합형 금리 영향 분석"],
                    "action_label": "이 뉴스로 브리핑 생성",
                    "action_type": "NEWS",
                    "external_id": "NEWS-ECON-01"
                },
                {
                    "id": "NEWS-TECH-02",
                    "title": "차세대 온디바이스 AI 탑재 스마트폰 스펙 및 실사용 체감 분석",
                    "badge": "IT·테크",
                    "score": 93.0,
                    "subtitle": "실시간 통번역, AI 사진 편집, 배터리 효율 총정리",
                    "breakdown": "트렌드: 95.0점 | 기술검증: 93.0점 | 구매의도: 92.0점",
                    "highlights": ["전작 대비 NPU 성능 40% 향상 벤치마크", "실사용자 배터리 및 발열 테스트 종합"],
                    "action_label": "이 뉴스로 브리핑 생성",
                    "action_type": "NEWS",
                    "external_id": "NEWS-TECH-02"
                },
                {
                    "id": "NEWS-SOCIETY-03",
                    "title": "2026년 달라지는 노동·고용 제도 및 근로시간 단축 핵심 정리",
                    "badge": "사회·트렌드",
                    "score": 92.5,
                    "subtitle": "육아휴직 급여 인상, 유연근무제 지원금 개편안",
                    "breakdown": "정책시의성: 95.0점 | 실생활체감: 94.0점 | 정확도: 96.0점",
                    "highlights": ["고용노동부 고시 확정안 완벽 해설", "직장인이 놓치기 쉬운 필수 체크리스트"],
                    "action_label": "이 뉴스로 브리핑 생성",
                    "action_type": "NEWS",
                    "external_id": "NEWS-SOCIETY-03"
                }
            ]
            return items

        elif v == "PRODUCT":
            items = [
                {
                    "id": "PROD-TECH-01",
                    "title": "2026 가성비 로봇청소기 3대 모델 실사용 물걸레·흡입력 비교",
                    "badge": "가전·스마트홈",
                    "score": 96.0,
                    "subtitle": "내돈내산 솔직 리뷰 종합 및 흡입력/스테이션 유지비 분석",
                    "breakdown": "구매의도: 97.0점 | 스펙비교: 95.0점 | 상투어구제거: 98.0점",
                    "highlights": ["실제 소음 및 문턱 등반 테스트 결과", "월간 유지비 및 소모품 교체 주기 비교"],
                    "action_label": "이 상품으로 비교글 생성",
                    "action_type": "PRODUCT",
                    "external_id": "PROD-TECH-01"
                },
                {
                    "id": "PROD-LIVING-02",
                    "title": "경추 목베개 & 메모리폼 토퍼 5종 30일 수면 질 개선 스펙 분석",
                    "badge": "리빙·수면",
                    "score": 94.5,
                    "subtitle": "수면 자세별 최적 높이 가이드 및 세탁 관리법",
                    "breakdown": "구매전환: 95.0점 | 실사용데이터: 94.0점 | 체류시간: 96.0점",
                    "highlights": ["옆으로 자는 사람 vs 바로 자는 사람 비교", "라돈 안전성 및 내구성 시험성적서 요약"],
                    "action_label": "이 상품으로 비교글 생성",
                    "action_type": "PRODUCT",
                    "external_id": "PROD-LIVING-02"
                }
            ]
            return items

        return []
