"""Travel Content Module implementing BaseContentModule for Domestic & Global Travel Guides."""
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.ai.router import AIProviderRouter
from app.ai.schemas import FAQItem, TravelSpotItem, TravelItineraryDay, TravelArticleOutput
from app.collectors.travel import TravelCollector, TravelCandidateItem
from app.core.base_module import BaseContentModule, CandidateItem
from app.config import get_settings

from app.core.prompts.manager import PromptTemplateManager
from app.core.verticals import VerticalType, VerticalStatus
from app.services.stock_image_service import StockImageService
from app.services.youtube_service import YouTubeService, YouTubeVideoInfo
from app.utils.logging import get_logger

logger = get_logger("travel_module")


class TravelModule(BaseContentModule):
    """Production Content Module for Travel Guides, Itineraries & Destination Info."""

    def __init__(
        self,
        collector: Optional[TravelCollector] = None,
        image_service: Optional[StockImageService] = None,
        youtube_service: Optional[YouTubeService] = None
    ):
        self.collector = collector or TravelCollector()
        self.ai_router = AIProviderRouter()
        self.image_service = image_service or StockImageService()
        self.youtube_service = youtube_service or YouTubeService()
        # Load title generator for CTR‑optimized titles
        from .title_generator import TitleGenerator  # local import to avoid circular deps
        self.title_generator = TitleGenerator

    @property
    def vertical(self) -> VerticalType:
        return VerticalType.TRAVEL

    @property
    def status(self) -> VerticalStatus:
        return VerticalStatus.PRODUCTION

    async def health_check(self) -> Dict[str, Any]:
        """Verify travel collector and AI provider connectivity."""
        collector_health = await self.collector.health_check()
        return {
            "success": collector_health.get("success", True),
            "collector": collector_health,
            "message": "여행 & 명소 가이드 모듈 정상 가동 중"
        }

    async def collect_candidates(self, db: Session, limit: int = 1500) -> List[CandidateItem]:
        """Discover, score, and normalize travel destinations."""
        logger.info("TravelModule: Collecting top travel destinations...")
        destinations = await self.collector.discover_popular_destinations(limit=limit)
        items: List[CandidateItem] = []

        for item in destinations:
            items.append(
                CandidateItem(
                    external_id=item.destination_id,
                    vertical=VerticalType.TRAVEL,
                    title=self.title_generator.generate_ctr_title(item),
                    original_title=f"{item.destination} ({item.country})",
                    summary=" / ".join(item.highlights[:2]) if item.highlights else item.theme,
                    source_attribution=item.source_attribution,
                    source_url=item.original_url,
                    score=item.score,
                    score_breakdown={
                        "popularity": item.score,
                        "practicality": 95.0
                    },
                    raw_data=item.model_dump()
                )
            )

        return items

    async def enrich_item(self, db: Session, external_id: str) -> Dict[str, Any]:
        """Retrieve full details, itinerary candidates, and travel tips for a destination."""
        item = await self.collector.get_destination_by_id(external_id)
        if not item:
            popular = await self.collector.discover_popular_destinations(limit=10)
            for p in popular:
                if p.destination_id == external_id:
                    item = p
                    break

        if not item:
            item = TravelCandidateItem(
                destination_id=external_id,
                destination="인기 여행지",
                country="해외/국내",
                region="",
                duration="3박 4일",
                theme="핵심 명소 & 미식 힐링 투어",
                highlights=["주요 랜드마크 방문 및 인생샷 명소", "현지 로컬 맛집 투어"],
                spots=["도심 중심가", "대표 전망대", "전통 시장"],
                budget_guide="1인 기준 실속 예산",
                transport_pass="현지 대중교통 1일 패스"
            )

        return {"travel_item": item}

    @staticmethod
    def _get_all_used_travel_image_urls(db: Session) -> List[str]:
        """Collect all image URLs already used across existing travel posts in DB."""
        from app.database.models import Post
        import re
        import json
        used_urls: List[str] = []
        try:
            posts = db.query(Post).filter(Post.vertical == "TRAVEL").all()
            for p in posts:
                if p.rendered_content:
                    found = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', p.rendered_content)
                    used_urls.extend(found)
                if p.article_json:
                    try:
                        data = json.loads(p.article_json)
                        if data.get("hero_image_url"):
                            used_urls.append(data["hero_image_url"])
                        for sp in data.get("must_visit_spots", []):
                            if sp.get("image_url"):
                                used_urls.append(sp["image_url"])
                    except Exception:
                        pass
        except Exception as e:
            logger.warning("Failed to collect historical travel image URLs: %s", e)
        return list(set(used_urls))

    async def generate_content(self, db: Session, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive travel guide with failover and zero cross-post image duplication."""
        import random
        item: TravelCandidateItem = enriched_data["travel_item"]
        data_dict = item.model_dump()

        prompt = PromptTemplateManager.build_user_prompt(VerticalType.TRAVEL, data_dict)
        system_prompt = PromptTemplateManager.get_system_prompt(VerticalType.TRAVEL)

        logger.info("TravelModule: Generating guide for '%s'...", item.destination)
        gen_result = await self.ai_router.generate_article(
            movie_data={
                "title": f"{item.destination} {item.duration} 완벽 여행 코스",
                "overview": "\n".join(item.highlights),
                "genres": ["여행", "가이드", item.country],
                "vote_average": 9.2,
                "popularity": item.score,
                "custom_prompt": prompt,
                "custom_system_prompt": system_prompt,
                "schema": TravelArticleOutput,
            }
        )

        article = None
        # 1. Fetch Hero Cover Image with Global DB Deduplication
        # Collect ALL historical travel image URLs from DB so we NEVER reuse existing photos!
        used_image_urls: List[str] = self._get_all_used_travel_image_urls(db)
        logger.info("TravelModule: Loaded %d historical travel image URLs from DB for deduplication.", len(used_image_urls))

        clean_dest = item.destination.split('(')[-1].replace(')', '').strip() if '(' in item.destination else item.destination
        cover_modifiers = [
            "travel landmark scenery",
            "city skyline architecture",
            "popular tourism destination",
            "downtown street scenic view",
            "urban travel perspective"
        ]
        dest_query = f"{clean_dest} {random.choice(cover_modifiers)}"
        
        pref_page = random.randint(1, 3)
        hero_img = await self.image_service.search_image(
            dest_query,
            exclude_urls=used_image_urls,
            prefer_page=pref_page,
            preferred_source="Pixabay"
        )
        hero_url = hero_img.url if hero_img else None
        if hero_url:
            used_image_urls.append(hero_url)

        # 2. Fetch Spot Images with Zero Duplication Guarantee (Alternating Pexels & Pixabay)
        spot_items: List[TravelSpotItem] = []
        spot_queries = getattr(item, 'spot_image_queries', {}) or {}

        for idx, s_name in enumerate(item.spots[:4]):
            specific_q = spot_queries.get(s_name) or f"{s_name} {clean_dest}"
            spot_pref_page = random.randint(1, 3)
            pref_source = "Pexels" if idx % 2 == 0 else "Pixabay"
            s_img = await self.image_service.search_image(
                specific_q,
                exclude_urls=used_image_urls,
                prefer_page=spot_pref_page,
                preferred_source=pref_source
            )
            
            spot_img_url = None
            spot_caption = None
            if s_img and s_img.url and s_img.url not in used_image_urls:
                spot_img_url = s_img.url
                spot_caption = f"{s_name} 현장 풍경 (출처: {s_img.source})"
                used_image_urls.append(spot_img_url)
            else:
                logger.info("TravelModule: No distinct unique image found for spot '%s', omitting spot image.", s_name)

            spot_items.append(
                TravelSpotItem(
                    name=s_name,
                    category="필수 명소",
                    description=f"{item.destination}을 대표하는 핵심 랜드마크로 방문객들의 만족도가 매우 높습니다.",
                    tip="오전 이른 시간에 방문하면 비교적 한산하게 사진을 남길 수 있습니다.",
                    image_url=spot_img_url,
                    image_caption=spot_caption
                )
            )

        # 3. Discover high-retention YouTube Travel Video
        travel_video: Optional[YouTubeVideoInfo] = None
        try:
            travel_video = await self.youtube_service.search_travel_video(item.destination, item.country)
        except Exception as e:
            logger.warning("TravelModule: Failed to fetch YouTube travel video: %s", e)

        if gen_result.success and gen_result.article:
            raw_art = gen_result.article
            if isinstance(raw_art, TravelArticleOutput):
                article = raw_art
                article.hero_image_url = hero_url
                if not article.must_visit_spots or len(article.must_visit_spots) == 0:
                    article.must_visit_spots = spot_items
                if not article.slug_hint:
                    article.slug_hint = f"travel-{item.destination_id.lower()}"
            else:
                article = TravelArticleOutput(
                    title=self.title_generator.generate_ctr_title(item),
                    slug_hint=f"travel-{item.destination_id.lower()}",
                    excerpt=raw_art.excerpt if hasattr(raw_art, 'excerpt') else f"{item.destination} {item.duration} 추천 일정, 경비, 필수 명소 및 교통패스 총정리 가이드입니다.",
                    hero_image_url=hero_url,
                    introduction=raw_art.introduction if hasattr(raw_art, 'introduction') else f"{item.destination}은 매력적인 문화와 맛있는 음식, 아름다운 풍경이 공존하는 최고의 여행지입니다.",
                destination_overview=f"{item.destination}({item.country})는 비행/이동 시간 {item.flight_time} 수준으로, 최적의 방문 시기는 {item.best_season}입니다.",
                weather_and_clothing=f"{item.destination}의 기후 특성을 고려해 {item.best_season} 방문 시에는 가벼운 외투와 편안한 운동화 착용을 추천합니다.",
                exchange_and_budget=f"{item.budget_guide} 수준으로, 현지 결제는 트래블 카드와 일부 현금 병행을 권장합니다.",
                itinerary_days=[
                    TravelItineraryDay(
                        day=1,
                        theme="도착 및 주요 도심 랜드마크 적응",
                        schedule=["공항 도착 후 숙소 체크인", f"{item.spots[0] if item.spots else '중심 광장'} 둘러보기", "로컬 대표 맛집 저녁 식사 및 야경 감상"],
                        tip="공항에서 시내 진입 시 공항철도나 사전 예약 리무진을 이용하면 편리합니다."
                    ),
                    TravelItineraryDay(
                        day=2,
                        theme="핵심 명소 투어 및 문화 탐방",
                        schedule=[f"{item.spots[1] if len(item.spots) > 1 else '명소'} 관람", "현지 카페 투어", f"{item.spots[2] if len(item.spots) > 2 else '전망대'} 일몰 감상"],
                        tip="오후 일몰 시간대 전망대는 사전 온라인 예약을 추천합니다."
                    ),
                    TravelItineraryDay(
                        day=3,
                        theme="근교 투어 또는 쇼핑 & 미식 마무리",
                        schedule=["전통 시장 또는 대형 쇼핑몰 방문", "기념품 및 특산품 쇼핑", "출국 준비 또는 귀가"],
                        tip="시내 텍스리펀(Tax Refund) 매장을 확인하여 환급 혜택을 챙기세요."
                    )
                ],
                must_visit_spots=spot_items,
                transport_tips=f"현지 대중교통 이용 시 {item.transport_pass}를 이용하면 요금을 대폭 절약할 수 있습니다.",
                travel_tips=[
                    "여권 유효기간은 출발일 기준 최소 6개월 이상 남아있어야 합니다.",
                    "해외 결제 수수료가 없는 트래블로그/트래블월렛 카드를 준비하세요.",
                    "구글 지도(Google Maps) 오프라인 지도를 사전 다운로드하면 편리합니다.",
                    "비상 상황을 대비해 여행자 보험 가입은 필수입니다."
                ],
                faq=[
                    FAQItem(
                        question=f"{item.destination} 여행 시 환전은 얼마나 해가야 하나요?",
                        answer="대부분의 가맹점에서 카드 결제가 가능하므로, 1일 3~5만 원 상당의 비상 현금과 수수료 우대 트래블 카드를 함께 챙기시면 충분합니다."
                    ),
                    FAQItem(
                        question="대중교통 패스는 필수인가요?",
                        answer=f"하루 3회 이상 대중교통을 탈 계획이라면 {item.transport_pass} 구매가 훨씬 경제적입니다."
                    )
                ],
                conclusion=f"알찬 계획과 여유로운 마음으로 {item.destination}에서 잊지 못할 추억을 만들어보세요!",
                seo_title=f"{item.destination} 여행 코스 경비 총정리",
                meta_description=f"{item.destination} {item.duration} 추천 코스, 1인 예상 경비, 필수 명소 및 교통 꿀팁 완벽 가이드.",
                tags=[item.destination.split()[0], item.country, "해외여행" if item.country != "대한민국" else "국내여행", "여행코스", "여행경비"]
            )
        else:
            # Deterministic fallback
            article = TravelArticleOutput(
                title=f"{item.destination} {item.duration} 추천 여행 코스 & 경비 가이드",
                slug_hint=f"travel-{item.destination_id.lower()}",
                excerpt=f"{item.destination} 여행을 준비하는 분들을 위한 {item.duration} 필수 코스와 경비 가이드입니다.",
                hero_image_url=hero_url,
                introduction=f"{item.destination}은 다채로운 매력과 볼거리로 매년 수많은 여행객이 찾는 인기 명소입니다.",
                destination_overview=f"비행시간 {item.flight_time}, 여행하기 좋은 최적의 시기는 {item.best_season}입니다.",
                weather_and_clothing=f"{item.best_season}에는 활동하기 쾌적하며, 편안한 운동화와 가벼운 겉옷을 준비하는 것이 좋습니다.",
                exchange_and_budget=f"{item.budget_guide} 수준으로 합리적인 여행 계획을 세울 수 있습니다.",
                itinerary_days=[
                    TravelItineraryDay(
                        day=1,
                        theme="도착 및 주요 도심 투어",
                        schedule=["호텔 체크인", f"{item.spots[0] if item.spots else '중심가'} 탐방", "로컬 디너"],
                        tip="시내 교통패스를 공항에서 미리 수령하세요."
                    ),
                    TravelItineraryDay(
                        day=2,
                        theme="핵심 명소 & 랜드마크",
                        schedule=[f"{item.spots[1] if len(item.spots) > 1 else '명소'} 관람", "감성 카페 투어", "야경 투어"],
                        tip="입장권은 사전 모바일 바우처로 준비하세요."
                    ),
                    TravelItineraryDay(
                        day=3,
                        theme="쇼핑 및 마무리",
                        schedule=["기념품 쇼핑", "마지막 로컬 맛집 탐방", "공항/역 이동"],
                        tip="수하물 무게를 미리 체크해 두세요."
                    )
                ],
                must_visit_spots=spot_items,
                transport_tips=f"현지 이동 시에는 {item.transport_pass}를 활용하는 것이 편리합니다.",
                travel_tips=[
                    "여권 만료일 확인 및 모바일 탑승권 준비",
                    "해외 데이터 eSim 또는 포켓 와이파이 신청",
                    "여행자 보험 가입으로 안심 여행"
                ],
                faq=[
                    FAQItem(
                        question="자유여행 난이도는 어떤가요?",
                        answer="대중교통 시스템과 한글/영문 안내가 잘 되어 있어 초보자도 쉽게 자유여행이 가능합니다."
                    )
                ],
                conclusion=f"지금 바로 {item.destination} 여행 계획을 세워보세요!",
                seo_title=f"{item.destination} {item.duration} 여행 코스",
                meta_description=f"{item.destination} 일정 및 경비 총정리.",
                tags=[item.destination.split()[0], item.country, "여행가이드"]
            )

        return {
            "travel_article": article,
            "travel_item": item,
            "travel_video": travel_video,
            "status": "SUCCESS"
        }

    def render_html(self, content_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Render modern, mobile-first travel guide layout with Schema.org TouristDestination and FAQPage."""
        article: TravelArticleOutput = content_data.get("travel_article")
        item: Optional[TravelCandidateItem] = content_data.get("travel_item")

        internal_links = content_data.get("internal_links") or (metadata.get("internal_links") if metadata else None) or []
        internal_links_html = ""
        if internal_links:
            links_li = "".join(
                f"<li style='margin-bottom:8px;'><a href='{l.get('url')}' style='color:#2563eb; text-decoration:underline; font-weight:600;'>{l.get('title')}</a></li>"
                for l in internal_links
            )
            internal_links_html = f"""
            <section style='margin:28px 0; padding:20px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px;'>
              <h4 style='font-size:16px; font-weight:700; color:#0f172a; margin:0 0 12px 0;'>&#128204; 함께 읽으면 좋은 블로그 추천 여행기</h4>
              <ul style='margin:0; padding-left:20px; line-height:1.7;'>
                {links_li}
              </ul>
            </section>
            """

        # 1. Day-by-Day Itinerary HTML
        itinerary_html = ""
        for day in article.itinerary_days:
            schedules_li = "".join(f"<li style='margin-bottom:6px;'>{s}</li>" for s in day.schedule)
            tip_box = f"<div style='margin-top:10px; padding:10px 14px; background:#eff6ff; border-radius:6px; font-size:13px; color:#1e40af;'><strong>Tip:</strong> {day.tip}</div>" if day.tip else ""
            itinerary_html += f"""
            <div style='background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px 20px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
              <div style='display:flex; align-items:center; margin-bottom:12px;'>
                <span style='background:#2563eb; color:#ffffff; font-size:13px; font-weight:700; padding:4px 10px; border-radius:20px; margin-right:10px;'>Day {day.day}</span>
                <h4 style='margin:0; font-size:16px; font-weight:700; color:#0f172a;'>{day.theme}</h4>
              </div>
              <ul style='margin:0; padding-left:20px; color:#334155; line-height:1.7;'>
                {schedules_li}
              </ul>
              {tip_box}
            </div>
            """

        # 2. Must-Visit Spots HTML
        spots_html = ""
        for spot in article.must_visit_spots:
            tip_html = f"<div style='font-size:13px; color:#059669; margin-top:6px;'>&#128073; <strong>방문 팁:</strong> {spot.tip}</div>" if spot.tip else ""
            img_html = ""
            if spot.image_url:
                img_html = f"""
                <div style='margin-bottom:12px; border-radius:8px; overflow:hidden;'>
                  <img src='{spot.image_url}' alt='{spot.name}' style='width:100%; height:auto; max-height:380px; object-fit:cover; display:block; border-radius:8px;' loading='lazy'>
                  <div style='font-size:12px; color:#64748b; margin-top:4px; text-align:right;'>{spot.image_caption or ''}</div>
                </div>
                """
            spots_html += f"""
            <div style='background:#f8fafc; border-left:4px solid #3b82f6; border-radius:4px; padding:16px 20px; margin-bottom:18px;'>
              <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                <h5 style='margin:0; font-size:17px; font-weight:700; color:#0f172a;'>{spot.name}</h5>
                <span style='font-size:12px; color:#64748b; background:#e2e8f0; padding:2px 8px; border-radius:12px;'>{spot.category}</span>
              </div>
              {img_html}
              <p style='margin:0; color:#475569; font-size:14px; line-height:1.7;'>{spot.description}</p>
              {tip_html}
            </div>
            """

        # 3. Practical Tips List
        tips_li = "".join(f"<li style='margin-bottom:8px; color:#334155;'>&#9989; {t}</li>" for t in article.travel_tips)

        # 4. FAQ Accordion & Schema
        faq_items_html = ""
        faq_schema_items = []
        for faq in article.faq:
            faq_items_html += f"""
            <details style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; margin-bottom:10px;'>
              <summary style='font-weight:600; color:#0f172a; cursor:pointer;'>Q. {faq.question}</summary>
              <div style='margin-top:10px; color:#475569; line-height:1.6;'>A. {faq.answer}</div>
            </details>
            """
            faq_schema_items.append({
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.answer
                }
            })

        # 5. Affiliate CTA Banner (Hotels & Activities)
        dest_name = item.destination.split()[0] if item else "여행지"
        affiliate_cta_html = f"""
        <div style='background:linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border:1px solid #bfdbfe; border-radius:12px; padding:20px; margin:24px 0; text-align:center;'>
          <h4 style='margin:0 0 8px 0; font-size:18px; color:#1e3a8a; font-weight:700;'>&#127976; {dest_name} 최저가 숙소 & 액티비티 특가</h4>
          <p style='margin:0 0 16px 0; font-size:14px; color:#3b82f6;'>인기 호텔과 필수 입장권·교통패스를 실시간 특가로 미리 예약해 보세요.</p>
          <div style='display:flex; justify-content:center; gap:12px; flex-wrap:wrap;'>
            <a href='https://www.agoda.com' target='_blank' rel='nofollow noopener' style='display:inline-block; background:#2563eb; color:#ffffff; font-weight:600; padding:10px 20px; border-radius:8px; text-decoration:none; font-size:14px;'>아고다 호텔 최저가 조회</a>
            <a href='https://www.klook.com' target='_blank' rel='nofollow noopener' style='display:inline-block; background:#059669; color:#ffffff; font-weight:600; padding:10px 20px; border-radius:8px; text-decoration:none; font-size:14px;'>클룩 투어·패스 예약</a>
          </div>
        </div>
        """

        # 6. YouTube 4K Travel Highlight Video Embed
        travel_video: Optional[YouTubeVideoInfo] = content_data.get("travel_video")
        video_html = ""
        if travel_video and travel_video.embed_url:
            view_cnt_str = f"조회수 {travel_video.view_count:,}회" if travel_video.view_count else "인기 추천 영상"
            video_html = f"""
            <section style='margin:28px 0; background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
              <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;'>
                <h4 style='margin:0; font-size:17px; font-weight:700; color:#0f172a;'>&#127916; 영상으로 미리 보는 {item.destination if item else '여행지'} 핵심 가이드</h4>
                <span style='font-size:12px; font-weight:700; color:#dc2626; background:#fee2e2; padding:3px 10px; border-radius:20px;'>&#9654; 유튜브 공식 추천 ({view_cnt_str})</span>
              </div>
              <div style='position:relative; padding-bottom:56.25%; height:0; overflow:hidden; border-radius:10px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);'>
                <iframe src='{travel_video.embed_url}' title='{travel_video.title}' style='position:absolute; top:0; left:0; width:100%; height:100%; border:0;' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' allowfullscreen loading='lazy'></iframe>
              </div>
              <div style='font-size:12px; color:#64748b; margin-top:8px; text-align:right;'>출처: 유튜브 채널 {travel_video.channel_name or 'YouTube Creator'} &middot; {travel_video.title}</div>
            </section>
            """

        # 7. JSON-LD Schema
        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "TouristDestination",
                    "name": item.destination if item else article.title,
                    "description": article.excerpt
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_schema_items
                }
            ]
        }
        schema_json = json.dumps(schema_data, ensure_ascii=False)

        # Full HTML Body
        html = f"""
        <meta name="google" content="notranslate">
        <div class="travel-guide-article notranslate" translate="no" lang="ko" style="max-width:800px; margin:0 auto; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height:1.7; color:#1e293b;">
          
          <!-- Schema.org JSON-LD -->
          <script type="application/ld+json">
          {schema_json}
          </script>

          <!-- Hero Overview Card (Light Magazine Aesthetic matching Elegant Travel theme) -->
          <div style="background:linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border:1px solid #dbeafe; border-radius:14px; padding:24px; margin-bottom:28px; box-shadow:0 2px 4px rgba(0,0,0,0.04);">
            <div style="display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;">
              <span class="notranslate" translate="no" style="background:#1e293b; color:#ffffff; font-size:12px; font-weight:700; padding:4px 12px; border-radius:20px;">✍️ 발행: 트래블픽24</span>
              <span style="background:#2563eb; color:#ffffff; font-size:12px; font-weight:700; padding:4px 12px; border-radius:20px;">
                &#9992; {item.country if item else '여행'} &middot; {item.duration if item else '가이드'}
              </span>
            </div>
            <div class="travel-hero-title" style="font-size:24px; font-weight:800; margin:0 0 12px 0; color:#0f172a; line-height:1.35;">{article.title}</div>
            <p style="font-size:15px; color:#475569; margin:0 0 16px 0; line-height:1.6;">{article.excerpt}</p>
            {f'<div style="border-radius:10px; overflow:hidden; margin-top:14px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.08);"><img src="{article.hero_image_url}" alt="{article.title}" style="width:100%; height:auto; max-height:420px; object-fit:cover; display:block; border-radius:10px;" loading="eager"></div>' if article.hero_image_url else ''}
          </div>

          <!-- Section 1: Introduction -->
          <h2 style="font-size:20px; font-weight:700; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:32px 0 16px 0; color:#0f172a;">
            &#128506; 여행지 한눈에 보기 & 매력 포인트
          </h2>
          <p style="font-size:15px; color:#334155; line-height:1.8;">{article.introduction}</p>
          <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px 18px; margin:16px 0; font-size:14px; color:#475569;">
            <strong>기본 정보:</strong> {article.destination_overview}
          </div>

          <!-- Section 2: Weather, Budget & Transport -->
          <h2 style="font-size:20px; font-weight:700; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:32px 0 16px 0; color:#0f172a;">
            &#128181; 날씨, 환율 및 1인 예상 경비
          </h2>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-bottom:20px;">
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
              <div style="font-weight:700; color:#2563eb; margin-bottom:6px;">&#9728; 날씨 & 옷차림</div>
              <p style="margin:0; font-size:14px; color:#475569; line-height:1.6;">{article.weather_and_clothing}</p>
            </div>
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
              <div style="font-weight:700; color:#059669; margin-bottom:6px;">&#128181; 예상 경비 & 결제</div>
              <p style="margin:0; font-size:14px; color:#475569; line-height:1.6;">{article.exchange_and_budget}</p>
            </div>
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
              <div style="font-weight:700; color:#d97706; margin-bottom:6px;">&#128652; 대중교통 & 패스</div>
              <p style="margin:0; font-size:14px; color:#475569; line-height:1.6;">{article.transport_tips}</p>
            </div>
          </div>

          <!-- Section 3: Recommended Itinerary -->
          <h2 style="font-size:20px; font-weight:700; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:32px 0 16px 0; color:#0f172a;">
            &#128197; 추천 맞춤형 여행 일정 코스
          </h2>
          {itinerary_html}

          <!-- YouTube Travel Video Highlight -->
          {video_html}

          <!-- Affiliate CTA Banner -->
          {affiliate_cta_html}

          <!-- Section 4: Must-Visit Spots -->
          <h2 style="font-size:20px; font-weight:700; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:32px 0 16px 0; color:#0f172a;">
            &#127963; 반드시 가봐야 할 핵심 명소 BEST
          </h2>
          {spots_html}

          <!-- Section 5: Travel Tips -->
          <h2 style="font-size:20px; font-weight:700; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:32px 0 16px 0; color:#0f172a;">
            &#128161; 놓치면 안 되는 현지 여행 꿀팁
          </h2>
          <ul style="list-style:none; padding:0; margin:0 0 20px 0;">
            {tips_li}
          </ul>

          <!-- Section 6: FAQ -->
          <h2 style="font-size:20px; font-weight:700; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:32px 0 16px 0; color:#0f172a;">
            &#10067; 자주 묻는 질문 (FAQ)
          </h2>
          {faq_items_html}

          <!-- Section 7: Internal Links -->
          {internal_links_html}

          <!-- Section 8: Conclusion -->
          <div style="background:#f1f5f9; border-radius:10px; padding:20px; margin-top:28px;">
            <h4 style="margin:0 0 8px 0; font-size:16px; font-weight:700; color:#0f172a;">&#9997; 에디터 여행 총평</h4>
            <p style="margin:0; font-size:14px; color:#475569; line-height:1.7;">{article.conclusion}</p>
          </div>

        </div>
        """
        return html

    def extract_metadata(
        self,
        gen_result: Dict[str, Any],
        enriched_data: Dict[str, Any],
        candidate: CandidateItem
    ) -> Dict[str, Any]:
        art = gen_result.get("travel_article")
        title = candidate.title
        excerpt = candidate.summary or candidate.title
        seo_title = title
        meta_description = excerpt
        tags = ["여행", "여행가이드", "여행코스"]
        article_json_str = "{}"
        featured_image_url = None
        if art:
            title = art.title
            excerpt = art.excerpt
            seo_title = art.seo_title
            meta_description = art.meta_description
            tags = art.tags or tags
            article_json_str = art.model_dump_json() if hasattr(art, "model_dump_json") else "{}"
            featured_image_url = getattr(art, "hero_image_url", None)

        return {
            "title": title,
            "excerpt": excerpt,
            "seo_title": seo_title,
            "meta_description": meta_description,
            "tags": tags,
            "featured_image_url": featured_image_url,
            "article_json_str": article_json_str
        }

    def get_core_entities(self, text: str) -> List[str]:
        known_destinations = [
            "오사카", "도쿄", "후쿠오카", "교토", "삿포로", "오키나와", "나고야",
            "다낭", "방콕", "나트랑", "푸꾸옥", "싱가포르", "타이베이", "가오슝",
            "홍콩", "마카오", "발리", "세부", "보라카이", "괌", "사이판", "하와이",
            "제주도", "부산", "강릉", "속초", "여수", "경주", "전주", "통영", "포항"
        ]
        return [dest for dest in known_destinations if dest in text]

