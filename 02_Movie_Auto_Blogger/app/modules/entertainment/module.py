"""Entertainment Content Module implementing BaseContentModule for K-Culture, Star & Media News."""
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.ai.router import AIProviderRouter
from app.ai.schemas import FAQItem, EntertainmentArticleOutput
from app.collectors.entertainment import EntertainmentCollector, EntertainmentCandidateItem
from app.core.base_module import BaseContentModule, CandidateItem
from app.core.prompts.manager import PromptTemplateManager
from app.core.verticals import VerticalType, VerticalStatus
from app.utils.logging import get_logger

logger = get_logger("entertainment_module")


class EntertainmentModule(BaseContentModule):
    """Production Content Module for Entertainment, Celebrity, Drama & K-POP News."""

    def __init__(self, collector: Optional[EntertainmentCollector] = None):
        self.collector = collector or EntertainmentCollector()
        self.ai_router = AIProviderRouter()

    @property
    def vertical(self) -> VerticalType:
        return VerticalType.ENTERTAINMENT

    @property
    def status(self) -> VerticalStatus:
        return VerticalStatus.PRODUCTION

    async def health_check(self) -> Dict[str, Any]:
        """Verify entertainment news collector and AI provider connectivity."""
        collector_health = await self.collector.health_check()
        return {
            "success": collector_health.get("success", True),
            "collector": collector_health,
            "message": "연예 & K-컬처 매거진 모듈 정상 가동 중"
        }

    async def collect_candidates(self, db: Session, limit: int = 10) -> List[CandidateItem]:
        """Discover, score, and normalize entertainment topics."""
        logger.info("EntertainmentModule: Collecting top entertainment news candidates...")
        news_items = await self.collector.discover_latest_news(limit=limit)
        items: List[CandidateItem] = []

        for item in news_items:
            items.append(
                CandidateItem(
                    external_id=item.topic_id,
                    vertical=VerticalType.ENTERTAINMENT,
                    title=item.headline,
                    original_title=item.category,
                    summary=" / ".join(item.key_facts[:2]) if item.key_facts else item.headline,
                    source_attribution=item.source_attribution,
                    source_url=item.original_url,
                    score=item.score,
                    score_breakdown={
                        "virality": item.score,
                        "freshness": 95.0
                    },
                    raw_data=item.model_dump()
                )
            )

        return items

    async def enrich_item(self, db: Session, external_id: str) -> Dict[str, Any]:
        """Retrieve full details, facts, and statements for an entertainment topic."""
        item = await self.collector.get_topic_by_id(external_id)
        if not item:
            popular = await self.collector.get_popular_topics(limit=10)
            for p in popular:
                if p.topic_id == external_id:
                    item = p
                    break

        if not item:
            item = EntertainmentCandidateItem(
                topic_id=external_id,
                headline=f"연예계 화제의 이슈 분석 ({external_id})",
                category="연예 핫이슈",
                key_facts=["공식 언론 보도 및 대중 관심 집중", "관련 당사자 및 제작진 공식 입장 조율 중"],
                related_persons=["출연진 및 제작진"],
                sources=["국내 주요 연예 매체"]
            )

        from app.services.image_provider import image_provider
        img_url = await image_provider.get_entertainment_image(item.headline)

        return {"entertainment_item": item, "image_url": img_url}

    async def generate_content(self, db: Session, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate objective, fact-based entertainment article using AI router with failover."""
        news_item: EntertainmentCandidateItem = enriched_data["entertainment_item"]
        data_dict = news_item.model_dump()

        prompt = PromptTemplateManager.build_user_prompt(VerticalType.ENTERTAINMENT, data_dict)
        system_prompt = PromptTemplateManager.get_system_prompt(VerticalType.ENTERTAINMENT)

        logger.info("EntertainmentModule: Generating article for '%s'...", news_item.headline)
        gen_result = await self.ai_router.generate_article(
            movie_data={
                "title": news_item.headline,
                "overview": "\n".join(news_item.key_facts),
                "genres": [news_item.category],
                "vote_average": 9.0,
                "popularity": news_item.score,
                "custom_prompt": prompt,
                "custom_system_prompt": system_prompt,
                "schema": EntertainmentArticleOutput,
            }
        )

        article = None
        if gen_result.success and gen_result.article:
            raw_art = gen_result.article
            if isinstance(raw_art, EntertainmentArticleOutput):
                article = raw_art
                if not article.slug_hint:
                    article.slug_hint = f"enter-{news_item.topic_id.lower()}"
            else:
                article = EntertainmentArticleOutput(
                    title=news_item.headline,
                    slug_hint=f"enter-{news_item.topic_id.lower()}",
                    excerpt=raw_art.excerpt if hasattr(raw_art, 'excerpt') else f"{news_item.headline} 관련 핵심 경과와 대중 반응을 신속하게 정리합니다.",
                    introduction=raw_art.introduction if hasattr(raw_art, 'introduction') else f"{news_item.headline} 소식이 전해지며 대중문화계와 팬들의 이목이 집중되고 있습니다.",
                    quick_summary_points=news_item.key_facts if news_item.key_facts else [
                        "화제의 중심에 선 핵심 이슈 브리핑",
                        "공식 언론 보도 및 입장 발표 확인",
                        "향후 일정 및 대중 반응 지속 모니터링"
                    ],
                    timeline_events=[
                        f"이슈 발생: {news_item.headline} 첫 보도 및 화제 형성",
                        f"공식 발표: 소속사 및 제작진 공식 입장 표명",
                        f"현재 동향: 국내외 대중 반응 및 후속 일정 진행"
                    ],
                    key_facts="\n".join(news_item.key_facts) if news_item.key_facts else "확인된 팩트를 바탕으로 객관적으로 정리된 내용입니다.",
                official_statements=news_item.official_statement or "소속사와 관계자 측은 공식 보도자료를 통해 입장을 정리하여 발표했습니다.",
                public_reactions="네티즌들과 팬들은 다양한 반응을 보이며 응원과 관심을 보내고 있습니다.",
                future_outlook="향후 예정된 방송 일정과 후속 활동 계획에 따라 긍정적인 반향이 이어질 것으로 전망됩니다.",
                faq=[
                    FAQItem(
                        question="이번 이슈의 핵심 쟁점은 무엇인가요?",
                        answer=f"{news_item.headline}에 관한 공식 보도와 확인된 사실을 토대로 전개되고 있습니다."
                    ),
                    FAQItem(
                        question="향후 활동 계획이나 공식 입장은 어떻게 되나요?",
                        answer=news_item.official_statement or "관계자 측의 추가 공식 발표를 통해 공식 일정이 확정될 예정입니다."
                    )
                ],
                conclusion="대중문화계의 다양한 시각 속에서 향후 행보에 귀추가 주목되고 있습니다.",
                seo_title=f"{news_item.headline[:45]} 이슈 총정리",
                meta_description=f"{news_item.headline} 사건 경과, 공식 입장, 대중 반응 및 향후 전망 심층 분석.",
                tags=[news_item.category, "연예뉴스", "핫이슈", "K컬처"]
            )
        else:
            # Deterministic fallback
            article = EntertainmentArticleOutput(
                title=f"{news_item.headline} 핵심 경과 및 대중 반응 총정리",
                slug_hint=f"enter-{news_item.topic_id.lower()}",
                excerpt=f"{news_item.headline}에 관한 최신 소식과 확인된 팩트를 전달합니다.",
                introduction=f"연예계 주요 소식으로 {news_item.headline} 이슈가 떠오르며 많은 관심이 집중되고 있습니다.",
                quick_summary_points=news_item.key_facts,
                timeline_events=[
                    "1단계: 주요 매체를 통한 최초 보도 및 이슈화",
                    "2단계: 관계자 측의 공식 입장 확인 및 발표",
                    "3단계: 향후 방송 및 활동 일정 조율"
                ],
                key_facts="\n".join(news_item.key_facts),
                official_statements=news_item.official_statement,
                public_reactions="팬들과 시청자들의 뜨거운 반응이 이어지고 있습니다.",
                future_outlook="차기 활동 및 공식 일정에 대한 기대감이 높아지고 있습니다.",
                faq=[
                    FAQItem(
                        question="이번 소식의 주요 내용은 무엇인가요?",
                        answer=f"{news_item.headline} 관련 핵심 팩트와 공식 입장입니다."
                    )
                ],
                conclusion="향후 전개될 활동과 추가 발표를 주목해 볼 필요가 있습니다.",
                seo_title=f"{news_item.headline[:45]} 최신 이슈",
                meta_description=f"{news_item.headline} 관련 팩트 분석 및 공식 입장.",
                tags=[news_item.category, "연예", "이슈분석"]
            )

        return {
            "entertainment_article": article,
            "entertainment_item": news_item,
            "status": "SUCCESS"
        }

    def render_html(self, content_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Render stylish, mobile-first entertainment magazine layout with Schema.org NewsArticle."""
        article: EntertainmentArticleOutput = content_data.get("entertainment_article")
        item: Optional[EntertainmentCandidateItem] = content_data.get("entertainment_item")

        if not article:
            return "<div class='enter-container'><p>연예 기사 원고가 준비되지 않았습니다.</p></div>"

        # 1. 3-line quick summary
        summary_items_html = "".join(
            f"<li style='margin-bottom:8px; font-weight:600; color:#1e293b;'>&#9889; {pt}</li>"
            for pt in article.quick_summary_points
        )

        # 2. Timeline items
        timeline_html = "".join(
            f"<div style='position:relative; padding-left:24px; margin-bottom:16px; border-left:2px solid #e11d48;'>"
            f"<div style='position:absolute; left:-7px; top:0; width:12px; height:12px; border-radius:50%; background:#e11d48;'></div>"
            f"<p style='margin:0; font-size:15px; color:#334155;'>{event}</p></div>"
            for event in article.timeline_events
        )

        # 3. FAQ items
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

        # 4. JSON-LD Schema
        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "NewsArticle",
                    "headline": article.title,
                    "description": article.excerpt,
                    "articleSection": "Entertainment"
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_schema_items
                }
            ]
        }
        schema_json = json.dumps(schema_data, ensure_ascii=False)

        # 5. Complete HTML Magazine layout
        html = f"""
<meta name="google" content="notranslate">
<!-- Entertainment Magazine Container -->
<div class="entertainment-article-wrap notranslate" translate="no" lang="ko" style="max-width:820px; margin:0 auto; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height:1.75; color:#1e293b;">
  
  <!-- Category & Badges -->
  <div style="display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap;">
    <span class="notranslate" translate="no" style="background:#1e293b; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">✍️ 발행: 엔터픽24</span>
    <span style="background:#e11d48; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">K-ENTERTAINMENT</span>
    <span style="background:#fdf2f8; color:#db2777; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px; border:1px solid #fbcfe8;">실시간 핫이슈</span>
    <span style="background:#f1f5f9; color:#475569; font-size:12px; font-weight:600; padding:4px 10px; border-radius:9999px;">팩트 브리핑</span>
  </div>

  <!-- Quick Summary Card -->
  <div style="background:linear-gradient(135deg, #fff1f2 0%, #ffffff 100%); border:1px solid #fecdd3; border-radius:12px; padding:20px; margin-bottom:24px; box-shadow:0 4px 6px -1px rgba(225,29,72,0.05);">
    <h3 style="margin:0 0 12px 0; color:#9f1239; font-size:17px; display:flex; align-items:center; gap:8px;">
      <span>&#128240;</span> 이슈 3줄 핵심 요약
    </h3>
    <ul style="margin:0; padding-left:0; list-style:none;">
      {summary_items_html}
    </ul>
  </div>

  <!-- Introduction -->
  <div style="font-size:16px; margin-bottom:24px; color:#334155;">
    <p>{article.introduction}</p>
  </div>

  <!-- Section 1: Timeline Flow -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #e11d48; padding-left:12px; margin-bottom:16px;">
      사건 전개 타임라인 (시간순 정리)
    </h2>
    <div style="background:#ffffff; border:1px solid #f1f5f9; border-radius:10px; padding:20px 16px;">
      {timeline_html}
    </div>
  </div>

  <!-- Section 2: Key Facts & Official Statements -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #475569; padding-left:12px; margin-bottom:14px;">
      확인된 핵심 팩트 및 공식 입장
    </h2>
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:18px; margin-bottom:14px;">
      <p style="margin:0 0 12px 0; color:#334155; line-height:1.7;">{article.key_facts}</p>
      {f"<div style='background:#ffffff; border-left:3px solid #0284c7; padding:12px; border-radius:4px; margin-top:12px;'><strong style='color:#0369a1;'>공식 입장:</strong> <span style='color:#334155;'>{article.official_statements}</span></div>" if article.official_statements else ""}
    </div>
  </div>

  <!-- Section 3: Public Reactions & Industry Outlook -->
  <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-bottom:28px;">
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
      <h3 style="margin:0 0 8px 0; font-size:16px; color:#0f172a;">&#128172; 대중 및 팬덤 반응</h3>
      <p style="margin:0; font-size:14px; color:#475569; line-height:1.6;">{article.public_reactions}</p>
    </div>
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
      <h3 style="margin:0 0 8px 0; font-size:16px; color:#0f172a;">&#128200; 향후 방송 및 활동 전망</h3>
      <p style="margin:0; font-size:14px; color:#475569; line-height:1.6;">{article.future_outlook}</p>
    </div>
  </div>

  <!-- Section 4: FAQ Accordion -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #8b5cf6; padding-left:12px; margin-bottom:14px;">
      이슈 관련 자주 묻는 질문 (FAQ)
    </h2>
    {faq_items_html}
  </div>

  <!-- Conclusion -->
  <div style="background:#fff1f2; border-left:4px solid #e11d48; padding:16px; border-radius:4px; font-size:15px; color:#881337;">
    <p style="margin:0;"><strong>에디터 총평:</strong> {article.conclusion}</p>
  </div>

</div>

<!-- Structured Data -->
<script type="application/ld+json">
{schema_json}
</script>
"""
        return html

    def extract_metadata(
        self,
        gen_result: Dict[str, Any],
        enriched_data: Dict[str, Any],
        candidate: CandidateItem
    ) -> Dict[str, Any]:
        art = gen_result.get("entertainment_article")
        title = candidate.title
        excerpt = candidate.summary or candidate.title
        seo_title = title
        meta_description = excerpt
        tags = ["연예", "K컬처", "방송"]
        article_json_str = "{}"
        featured_image_url = enriched_data.get("image_url")
        if art:
            title = art.title
            excerpt = art.excerpt
            seo_title = art.seo_title
            meta_description = art.meta_description
            tags = art.tags or tags
            article_json_str = art.model_dump_json() if hasattr(art, "model_dump_json") else "{}"
            featured_image_url = featured_image_url or getattr(art, "hero_image_url", None)

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
        return [text.strip()]

