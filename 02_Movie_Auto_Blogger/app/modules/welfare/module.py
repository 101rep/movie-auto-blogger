"""Welfare Content Module implementing BaseContentModule for Korean Government Support & Benefits."""
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.ai.router import AIProviderRouter
from app.ai.schemas import FAQItem, WelfareArticleOutput
from app.collectors.welfare import WelfareCollector, WelfareCandidateItem
from app.core.base_module import BaseContentModule, CandidateItem
from app.core.prompts.manager import PromptTemplateManager
from app.core.verticals import VerticalType, VerticalStatus
from app.utils.logging import get_logger

logger = get_logger("welfare_module")


class WelfareModule(BaseContentModule):
    """Production Content Module for Korean Welfare & Government Subsidies."""

    def __init__(self, collector: Optional[WelfareCollector] = None):
        self.collector = collector or WelfareCollector()
        self.ai_router = AIProviderRouter()

    @property
    def vertical(self) -> VerticalType:
        return VerticalType.WELFARE

    @property
    def status(self) -> VerticalStatus:
        return VerticalStatus.PRODUCTION

    async def health_check(self) -> Dict[str, Any]:
        """Verify welfare data collector and AI provider connectivity."""
        collector_health = await self.collector.health_check()
        return {
            "success": collector_health.get("success", True),
            "collector": collector_health,
            "message": "대한민국 복지 & 지원금 모듈 정상 가동 중"
        }

    async def collect_candidates(self, db: Session, limit: int = 10, site_id: Optional[int] = None) -> List[CandidateItem]:
        """Discover, score, and normalize welfare policy candidates from Gov24 & data.go.kr."""
        logger.info("WelfareModule: Collecting welfare candidates (site_id=%s, limit=%d)...", str(site_id), limit)
        if site_id:
            welfare_items = await self.collector.discover_policies_for_site(site_id=site_id, limit=limit)
        else:
            welfare_items = await self.collector.discover_latest_policies(limit=limit)
        items: List[CandidateItem] = []

        for w in welfare_items:
            items.append(
                CandidateItem(
                    external_id=w.service_id,
                    vertical=VerticalType.WELFARE,
                    title=w.service_name,
                    original_title=w.category,
                    summary=w.benefit_summary,
                    source_attribution=w.source_attribution,
                    source_url=w.apply_url,
                    score=w.score,
                    score_breakdown={
                        "category_demand": 90.0,
                        "benefit_scale": w.score
                    },
                    raw_data=w.model_dump()
                )
            )

        return items

    async def enrich_item(self, db: Session, external_id: str) -> Dict[str, Any]:
        """Retrieve full details, checklist, and guidelines for a welfare program."""
        item = await self.collector.get_program_by_id(external_id)
        if not item:
            # Fallback lookup in popular programs
            popular = await self.collector.get_popular_programs(limit=10)
            for p in popular:
                if p.service_id == external_id:
                    item = p
                    break

        if not item:
            # Construct minimal item if dynamic
            item = WelfareCandidateItem(
                service_id=external_id,
                service_name=f"정부 지원 정책 ({external_id})",
                target_summary="관련 요건 충족 국민",
                benefit_summary="정부 지원금 및 바우처 혜택",
                benefit_highlight="정부 공식 지원 혜택",
                eligibility_checklist=["주민등록상 대한민국 거주자", "소득 및 재산 기준 부합자"],
                application_steps=["1단계: 공고 확인", "2단계: 온라인 서류 접수", "3단계: 심사 및 지급"],
                required_documents=["신분증", "주민등록등본", "소득증빙서류"]
            )

        from app.services.image_provider import image_provider
        img_url = await image_provider.get_welfare_image(item.service_name, item.category)

        return {"welfare_item": item, "image_url": img_url}

    async def generate_content(self, db: Session, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-E-E-A-T welfare guide article using AI router with failover."""
        welfare_item: WelfareCandidateItem = enriched_data["welfare_item"]
        data_dict = welfare_item.model_dump()

        prompt = PromptTemplateManager.build_user_prompt(VerticalType.WELFARE, data_dict)
        system_prompt = PromptTemplateManager.get_system_prompt(VerticalType.WELFARE)

        logger.info("WelfareModule: Generating article for '%s'...", welfare_item.service_name)
        # Attempt generation via AI provider
        gen_result = await self.ai_router.generate_article(
            movie_data={
                "title": welfare_item.service_name,
                "overview": f"{welfare_item.target_summary}\n{welfare_item.benefit_summary}",
                "genres": [welfare_item.category],
                "vote_average": 9.5,
                "popularity": welfare_item.score,
                "custom_prompt": prompt,
                "custom_system_prompt": system_prompt,
                "schema": WelfareArticleOutput,
            }
        )

        # Build structured WelfareArticleOutput
        welfare_article = None
        if gen_result.success and gen_result.article:
            raw_art = gen_result.article
            if isinstance(raw_art, WelfareArticleOutput):
                welfare_article = raw_art
                if not welfare_article.official_apply_url or not welfare_article.official_apply_url.startswith("http"):
                    welfare_article.official_apply_url = welfare_item.apply_url
                if not welfare_article.inquiry_contact:
                    welfare_article.inquiry_contact = welfare_item.inquiry_contact
                if not welfare_article.benefit_highlight:
                    welfare_article.benefit_highlight = welfare_item.benefit_highlight
                if not welfare_article.slug_hint:
                    welfare_article.slug_hint = f"welfare-{welfare_item.service_id.lower()}"
            else:
                welfare_article = WelfareArticleOutput(
                    title=f"{welfare_item.service_name} 자격조건 및 신청방법 총정리 ({welfare_item.benefit_highlight})",
                    slug_hint=f"welfare-{welfare_item.service_id.lower()}",
                    excerpt=f"{welfare_item.service_name}의 지원 대상, 혜택 금액, 신청 기간 및 구비 서류를 한눈에 알기 쉽게 정리해 드립니다.",
                    introduction=raw_art.introduction if hasattr(raw_art, 'introduction') else f"{welfare_item.service_name}은 대한민국 국민들의 생활 안정과 복지 증진을 위해 마련된 핵심 정책입니다.",
                    target_summary=welfare_item.target_summary,
                    eligibility_checklist=welfare_item.eligibility_checklist or [
                        "주민등록 기준 대한민국 거주 국민",
                        "해당 연령 및 소득 기준 부합자"
                    ],
                    benefit_details=welfare_item.benefit_summary,
                benefit_highlight=welfare_item.benefit_highlight,
                application_period=welfare_item.application_period,
                application_steps=welfare_item.application_steps or [
                    "1단계: 온라인(복지로/정부24) 또는 관할 기관 방문",
                    "2단계: 신청서 작성 및 필수 증빙 서류 제출",
                    "3단계: 자격 심사 후 선정 결과 통보 및 지원 혜택 수령"
                ],
                required_documents=welfare_item.required_documents or ["신분증", "주민등록등본", "소득증빙자료"],
                official_apply_url=welfare_item.apply_url,
                inquiry_contact=welfare_item.inquiry_contact,
                caution_notes=welfare_item.caution_notes or ["중복 수혜 제한 규정을 사전 확인하십시오."],
                faq=[
                    FAQItem(
                        question=f"{welfare_item.service_name}은 누구나 신청할 수 있나요?",
                        answer=f"기본적으로 {welfare_item.target_summary} 조건을 충족해야 신청이 가능합니다."
                    ),
                    FAQItem(
                        question="신청 시 준비해야 할 서류는 무엇인가요?",
                        answer=f"주요 필수 서류는 {', '.join(welfare_item.required_documents[:3])} 등입니다."
                    )
                ],
                conclusion=f"정부 지원금과 복지 혜택은 직접 신청하지 않으면 받을 수 없는 경우가 많습니다. 본인이 지원 대상인지 꼼꼼히 확인하시고 꼭 신청하시기 바랍니다.",
                seo_title=f"{welfare_item.service_name} 자격조건 및 신청방법 총정리",
                meta_description=f"{welfare_item.service_name} 지원 대상, 지원 혜택 금액, 신청 방법 및 필요 서류 완벽 가이드.",
                tags=[welfare_item.service_name, "정부지원금", "복지혜택", welfare_item.category, "복지로"]
            )
        else:
            # Fallback deterministic high-quality welfare article
            welfare_article = WelfareArticleOutput(
                title=f"{welfare_item.service_name} 지원 대상 및 신청 방법 완벽 가이드",
                slug_hint=f"welfare-{welfare_item.service_id.lower()}",
                excerpt=f"{welfare_item.service_name} 핵심 자격 요건과 지원 금액, 놓치지 말고 신청하세요.",
                introduction=f"정부에서 지원하는 {welfare_item.service_name}은 대상자에게 실질적인 도움을 제공하는 대표적인 복지 정책입니다. 본 가이드에서는 지원 자격부터 신청 절차까지 명쾌하게 정리합니다.",
                target_summary=welfare_item.target_summary,
                eligibility_checklist=welfare_item.eligibility_checklist,
                benefit_details=welfare_item.benefit_summary,
                benefit_highlight=welfare_item.benefit_highlight,
                application_period=welfare_item.application_period,
                application_steps=welfare_item.application_steps,
                required_documents=welfare_item.required_documents,
                official_apply_url=welfare_item.apply_url,
                inquiry_contact=welfare_item.inquiry_contact,
                caution_notes=welfare_item.caution_notes,
                faq=[
                    FAQItem(
                        question=f"{welfare_item.service_name} 지원 자격은 어떻게 되나요?",
                        answer=f"{welfare_item.target_summary} 조건에 부합하는 국민이면 신청 가능합니다."
                    ),
                    FAQItem(
                        question="어디서 신청할 수 있나요?",
                        answer=f"{welfare_item.apply_url} 또는 관할 지자체 주민센터에서 접수할 수 있습니다."
                    )
                ],
                conclusion=f"지원 혜택을 놓치지 않도록 신청 기한 내에 온라인 접수를 완료하시길 권장합니다.",
                seo_title=f"{welfare_item.service_name} 자격조건 및 신청방법",
                meta_description=f"{welfare_item.service_name} 지원 내용, 자격 요건, 신청 기간 상세 정리.",
                tags=[welfare_item.service_name, "정부지원금", "복지혜택", "신청가이드"]
            )

        return {
            "welfare_article": welfare_article,
            "welfare_item": welfare_item,
            "image_url": enriched_data.get("image_url"),
            "status": "SUCCESS"
        }

    def render_html(self, content_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Render high-conversion, responsive HTML welfare guide with E-E-A-T styling & Schema.org."""
        article: WelfareArticleOutput = content_data.get("welfare_article")
        item: Optional[WelfareCandidateItem] = content_data.get("welfare_item")
        image_url = content_data.get("image_url")

        if not article:
            return "<div class='welfare-container'><p>복지 정보 원고가 준비되지 않았습니다.</p></div>"

        # 1. Checklist HTML
        checklist_html = "".join(
            f"<li style='margin-bottom:8px; display:flex; align-items:flex-start; gap:8px;'>"
            f"<span style='color:#10b981; font-weight:bold;'>&#10004;</span> <span>{item}</span></li>"
            for item in article.eligibility_checklist
        )

        # 2. Steps HTML
        steps_html = "".join(
            f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:10px;'>"
            f"<span style='background:#3b82f6; color:#ffffff; font-size:12px; font-weight:bold; padding:3px 8px; border-radius:4px; margin-right:8px;'>STEP {idx+1}</span>"
            f"<strong style='color:#1e293b;'>{step}</strong></div>"
            for idx, step in enumerate(article.application_steps)
        )

        # 3. Required Documents HTML
        docs_html = "".join(
            f"<li style='margin-bottom:6px;'>&#128196; {doc}</li>"
            for doc in article.required_documents
        )

        # 4. Caution Notes HTML
        cautions_html = "".join(
            f"<li style='margin-bottom:6px; color:#b91c1c;'>&#9888; {note}</li>"
            for note in article.caution_notes
        )

        # 5. FAQ HTML & Schema
        faq_items_html = ""
        faq_schema_items = []
        for faq in article.faq:
            faq_items_html += f"""
            <details style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; margin-bottom:10px;">
              <summary style="font-weight:600; color:#0f172a; cursor:pointer;">Q. {faq.question}</summary>
              <div style="margin-top:10px; color:#475569; line-height:1.6;">A. {faq.answer}</div>
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

        # 6. JSON-LD Schema
        schema_data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "GovernmentService",
                    "name": article.title,
                    "serviceType": article.tags[0] if article.tags else "정부 복지 지원",
                    "provider": {
                        "@type": "GovernmentOrganization",
                        "name": getattr(item, "competent_agency", "대한민국 정부")
                    },
                    "description": article.excerpt
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_schema_items
                }
            ]
        }
        schema_json = json.dumps(schema_data, ensure_ascii=False)

        legal_basis = getattr(item, "legal_basis", None)
        legal_badge_html = f'<span style="background:#f1f5f9; color:#475569; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px; border:1px solid #cbd5e1;">⚖️ 법령: {legal_basis.split("||")[0]}</span>' if legal_basis else ""

        stats_box_html = ""
        stats_content = getattr(item, "stats_fact_box", None)
        if stats_content:
            stats_box_html = f"""
  <!-- 보건복지부 및 공공데이터포털 공식 통계 팩트 박스 (E-E-A-T 사실 접지) -->
  <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #16a34a; border-radius:10px; padding:18px; margin-bottom:28px;">
    <h3 style="margin:0 0 8px 0; font-size:16px; color:#15803d; display:flex; align-items:center; gap:8px;">
      <span>🏛️</span> 보건복지부 & 대한민국 공공데이터포털 정책·통계 브리핑
    </h3>
    <div style="font-size:14px; color:#166534; line-height:1.7; white-space:pre-line;">{stats_content}</div>
    <div style="font-size:12px; color:#65a30d; margin-top:8px; text-align:right;">
      * 출처: 공공데이터포털(data.go.kr) & {getattr(item, 'competent_agency', '보건복지부')} 공식 통계 지표
    </div>
  </div>
"""

        # 7. Complete Clean Magazine Layout
        html = f"""
<meta name="google" content="notranslate">
<!-- Welfare Article Container -->
<div class="welfare-article-wrap notranslate" translate="no" lang="ko" style="max-width:820px; margin:0 auto; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height:1.75; color:#1e293b;">
  
  <!-- Header Badges -->
  <div style="display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap;">
    <span class="notranslate" translate="no" style="background:#1e293b; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">✍️ 발행: 복지픽 (정책 브리핑)</span>
    <span style="background:#2563eb; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">대한민국 정부 복지</span>
    <span style="background:#ecfdf5; color:#059669; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px; border:1px solid #a7f3d0;">2026 최신 개정판</span>
    <span style="background:#fef3c7; color:#d97706; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">신청 접수 중</span>
    {legal_badge_html}
  </div>

  <!-- Welfare Editorial Visual Photo Card -->
  {"<div style='margin: 16px 0 24px 0; text-align: center; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 18px rgba(0,0,0,0.06);'><img src='" + image_url + "' alt='" + article.title + " 정책 가이드' style='width: 100%; max-height: 380px; object-fit: cover; border-radius: 12px;' /><div style='padding: 8px 12px; font-size: 13px; color: #64748b; background: #f8fafc; text-align: right;'>🏛️ 복지픽24 맞춤 정책 가이드센터</div></div>" if image_url else ""}

  <!-- Key Highlight Callout Box -->
  <div style="background:linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%); border:2px solid #3b82f6; border-radius:12px; padding:20px; margin-bottom:24px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
    <h3 style="margin:0 0 10px 0; color:#1e3a8a; font-size:18px; display:flex; align-items:center; gap:8px;">
      <span>&#128176;</span> 핵심 혜택 한눈에 보기
    </h3>
    <p style="margin:0 0 8px 0; font-size:17px; font-weight:700; color:#047857;">{article.benefit_highlight}</p>
    <p style="margin:0; font-size:14px; color:#475569;">신청 기간: <strong>{article.application_period}</strong> | 문의처: <strong>{article.inquiry_contact or '129'}</strong></p>
  </div>

  <!-- Introduction -->
  <div style="font-size:16px; margin-bottom:24px; color:#334155;">
    <p>{article.introduction}</p>
  </div>

  <!-- Section 1: Target & Eligibility Checklist -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #2563eb; padding-left:12px; margin-bottom:14px;">
      1. 누가 지원받을 수 있나요? (지원 자격)
    </h2>
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:18px; margin-bottom:14px;">
      <p style="margin:0 0 12px 0; color:#1e293b; font-weight:600;">{article.target_summary}</p>
      <ul style="margin:0; padding-left:0; list-style:none;">
        {checklist_html}
      </ul>
    </div>
  </div>

  {stats_box_html}

  <!-- Section 2: Benefit Details -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #059669; padding-left:12px; margin-bottom:14px;">
      2. 어떤 혜택을 얼마나 받나요? (지원 내용)
    </h2>
    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; margin-bottom:14px;">
      <p style="margin:0; font-size:16px; color:#334155; line-height:1.7;">{article.benefit_details}</p>
    </div>
  </div>

  <!-- Section 3: How to Apply (Step by Step) -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #3b82f6; padding-left:12px; margin-bottom:14px;">
      3. 어떻게 신청하나요? (단계별 신청 절차)
    </h2>
    <div>
      {steps_html}
    </div>
  </div>

  <!-- Section 4: Required Documents & Caution -->
  <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-bottom:28px;">
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
      <h3 style="margin:0 0 10px 0; font-size:16px; color:#0f172a;">&#128203; 필수 구비 서류</h3>
      <ul style="margin:0; padding-left:20px; color:#475569; font-size:14px;">
        {docs_html}
      </ul>
    </div>
    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:16px;">
      <h3 style="margin:0 0 10px 0; font-size:16px; color:#991b1b;">&#9888; 신청 시 주의사항</h3>
      <ul style="margin:0; padding-left:20px; color:#7f1d1d; font-size:14px;">
        {cautions_html}
      </ul>
    </div>
  </div>

  <!-- CTA Action Button -->
  <div style="text-align:center; margin:32px 0;">
    <a href="{article.official_apply_url}" target="_blank" rel="noopener noreferrer" 
       style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; font-size:16px; font-weight:700; padding:14px 32px; border-radius:8px; box-shadow:0 4px 6px -1px rgba(37,99,235,0.3); transition:background 0.2s;">
      &#127760; {article.title.split()[0]} 공식 신청 홈페이지 바로가기 &rarr;
    </a>
    <p style="font-size:13px; color:#64748b; margin-top:8px;">* 정부 및 관할 공공기관 공식 접수 웹사이트로 안전하게 연결됩니다.</p>
  </div>

  <!-- Section 5: FAQ Accordion -->
  <div style="margin-bottom:28px;">
    <h2 style="font-size:20px; font-weight:700; color:#0f172a; border-left:4px solid #6366f1; padding-left:12px; margin-bottom:14px;">
      자주 묻는 질문 (FAQ)
    </h2>
    {faq_items_html}
  </div>

  <!-- Conclusion -->
  <div style="background:#f8fafc; border-top:2px solid #e2e8f0; padding:18px; border-radius:8px; font-size:15px; color:#475569;">
    <p style="margin:0;"><strong>에디터 안내:</strong> {article.conclusion}</p>
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
        from app.services.title_hook_service import title_hook_service
        art = gen_result.get("welfare_article")
        w_item = enriched_data.get("welfare_item")
        is_roadmap = getattr(w_item, "is_roadmap", False) if w_item else False
        raw_title = art.title if art else candidate.title
        title = title_hook_service.generate_hooked_title(raw_title, is_multiyear_policy=is_roadmap)
        excerpt = art.excerpt if art else (candidate.summary or candidate.title)
        seo_title = title
        meta_description = excerpt
        tags = art.tags if (art and art.tags) else ["복지", "정부지원금", "정책"]
        article_json_str = art.model_dump_json() if (art and hasattr(art, "model_dump_json")) else "{}"
        featured_image_url = enriched_data.get("image_url") or gen_result.get("image_url")

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
        known_programs = [
            "청년도약계좌", "청년월세", "국민취업지원제도", "K-패스", "기후동행카드",
            "국민연금", "기초연금", "부모급여", "아동수당", "소상공인", "새출발기금",
            "전기요금 특별지원", "에너지바우처", "디딤돌대출", "버팀목전세대출",
            "신생아 특례대출", "희망리턴패키지", "내일채움공제", "알뜰교통카드"
        ]
        return [prog for prog in known_programs if prog in text]

