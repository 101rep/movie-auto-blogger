"""Content Writer Agent for Welfare Engine V1.0.
Generates structured, SEO-optimized, highly authoritative Korean welfare articles.
Adheres strictly to the 10-step section structure:
1. 제목 생성
2. 요약
3. 대상자 설명
4. 지원 내용
5. 지원 금액
6. 신청 기간
7. 신청 방법
8. 필요 서류
9. FAQ
10. 공식 링크
Equipped with Universal Content Quality Engine:
- Anti-Cliche: Strict elimination of AI generic phrases.
- Persona-first: Tailored to Blog A (Consultant), Blog B (Family/Youth), Blog C (Business).
- Grounding: Accurate official government figures and criteria.
"""
import json
import logging
import re
from typing import Dict, Any, Optional
from google import genai

from welfare_engine.config import settings, WelfareBlogConfig
from welfare_engine.agent.persona_router import PersonaDispatchPlan
from welfare_engine.database.models import WelfareContent

logger = logging.getLogger("welfare_engine.writer")


class WelfareWriterAgent:
    """Writes persona-tailored articles using Gemini 3.6 Flash with deterministic fallback."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.client = None
        if self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(api_key=self.api_key.strip())
            except Exception as e:
                logger.warning(f"Could not initialize genai.Client: {e}")

    def build_prompt(self, content: WelfareContent, plan: PersonaDispatchPlan) -> str:
        """Construct the prompt enforcing the 10-step structure and strict persona tone."""
        blog = plan.blog_config
        return f"""당신은 대한민국 최고 권위의 복지 정책 전문 취재 기자이자 '{blog.persona_name}'입니다.
다음 공식 정부 복지 정책 데이터를 바탕으로, 블로그 [{blog.name}]의 독자({blog.target_audience})를 위한 고품질 기사를 작성하세요.

[블로그 페르소나 및 어조]
- 정체성: {blog.title}
- 페르소나: {blog.persona_name}
- 글쓰기 스타일: {blog.persona_style}
- 대표 문체 예시: {blog.sample_phrases[0]}
- 이번 기획 앵글: {plan.angle}

[정부 공식 정책 원천 데이터]
- 정책명: {content.title}
- 소관 기관: {content.source}
- 지원 대상: {content.target}
- 연령/지역 요건: {content.age} / {content.region}
- 소득 요건: {content.income_condition}
- 지원 금액/혜택: {content.amount}
- 신청 기간: {content.deadline}
- 신청 방법: {content.apply_method}
- 필요 서류: {content.documents}
- 공식 링크: {content.url}

[절대 준수 규칙]
1. 과장 광고, 허위 표현, 불안 조성성 표현을 절대 사용하지 마세요.
2. AI 상투어구 금지: '~에 대해 알아보겠습니다', '지금부터 살펴보겠습니다', '함께 확인해보시죠' 등 진부한 도입부를 일체 쓰지 마세요.
3. 기사 시작은 독자의 실생활 고충을 짚어주는 1인칭 공감 도입부("{plan.lead_intro}")로 자연스럽게 시작하세요.
4. 반드시 아래 10단계 구조를 순서대로 준수하여 본문을 작성하세요:
   (1) 제목 (SEO 키워드 포함, 35자 내외)
   (2) 요약 (바쁜 독자를 위한 3줄 핵심 포인트)
   (3) 대상자 설명 (누가 받을 수 있고 누가 제외되는지 명확한 불릿)
   (4) 지원 내용 (실질적으로 제공되는 서비스 및 혜택)
   (5) 지원 금액 (최대 지원 한도, 지급 주기, 방식)
   (6) 신청 기간 (시작일, 마감일, D-Day 유의사항)
   (7) 신청 방법 (온라인 정부24/복지로 및 오프라인 주민센터 방문 절차)
   (8) 필요 서류 (필수 서류 목록 및 발급 팁)
   (9) FAQ (가장 많이 묻는 실전 질문 3가지와 명쾌한 답변)
   (10) 공식 링크 (공식 신청 홈페이지 안내)

[출력 형식]
반드시 아래 JSON 형식으로만 응답하세요:
{{
  "title": "SEO 최적화 기사 제목",
  "summary": ["핵심 요약 1", "핵심 요약 2", "핵심 요약 3"],
  "target_desc": "지원 자격 상세 설명 (마크다운 불릿 포함)",
  "benefits": "지원 혜택 내용",
  "amount_desc": "지원 금액 및 규모 상세",
  "period_desc": "신청 기간 및 마감 안내",
  "steps": ["1단계: ...", "2단계: ...", "3단계: ..."],
  "documents": ["서류 1", "서류 2", "서류 3"],
  "faqs": [
    {{"question": "Q1 질문", "answer": "A1 답변"}},
    {{"question": "Q2 질문", "answer": "A2 답변"}},
    {{"question": "Q3 질문", "answer": "A3 답변"}}
  ],
  "official_url": "{content.url}",
  "tags": ["키워드1", "키워드2", "키워드3", "키워드4"]
}}
"""

    async def generate_article_data(self, content: WelfareContent, plan: PersonaDispatchPlan) -> Dict[str, Any]:
        """Generate structured article data via Gemini API with deterministic fallback."""
        prompt = self.build_prompt(content, plan)

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                text = response.text.strip()
                # Extract JSON from markdown fences if any
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
                clean_json = json_match.group(1) if json_match else text
                parsed = json.loads(clean_json)
                if parsed.get("title") and parsed.get("summary"):
                    logger.info(f"Gemini generation successful for {plan.blog_key}: '{parsed['title']}'")
                    return parsed
            except Exception as e:
                logger.warning(f"Gemini API generation failed for {plan.blog_key} ({e}). Falling back to deterministic writer.")

        # Deterministic High-Quality Fallback
        return self._generate_fallback(content, plan)

    def _generate_fallback(self, content: WelfareContent, plan: PersonaDispatchPlan) -> Dict[str, Any]:
        """High-fidelity fallback generator ensuring 100% reliable system operation."""
        blog = plan.blog_config
        title = plan.title

        return {
            "title": title,
            "summary": [
                f"{content.title}의 핵심 지원 요건과 수혜 대상을 알기 쉽게 정리했습니다.",
                f"지원 규모는 {content.amount or '정부 기준액'} 수준이며, 신청 절차에 맞춘 사전 서류 준비가 필수적입니다.",
                f"신청 기한은 {content.deadline or '상시접수'}이므로 기한 내 정부 공식 접수처를 확인하시기 바랍니다."
            ],
            "target_desc": f"• 지원 대상: {content.target or '대한민국 해당 요건 충족자'}\n• 연령 기준: {content.age or '해당 정책 연령'}\n• 소득 기준: {content.income_condition or '소득 요건 충족'}",
            "benefits": f"정부에서 공식 지원하는 정책으로, {content.amount or '상세 지원혜택'}에 해당하는 실질적 가계/사업 혜택이 제공됩니다.",
            "amount_desc": content.amount or "정부 정책 기준에 따른 지원금 지급",
            "period_desc": f"{content.deadline or '상시 접수 진행'} (예산 소진 및 조기 마감에 유의하세요)",
            "steps": [
                f"1단계: {content.apply_method or '온라인 신청 사이트(정부24/복지로)'} 접속 및 본인인증",
                "2단계: 자격 요건 자가진단 및 신청서 작성",
                "3단계: 구비 서류 첨부 후 최종 접수 및 심사 결과 확인"
            ],
            "documents": [d.strip() for d in (content.documents or "신분증, 주민등록등본").split(",") if d.strip()],
            "faqs": [
                {"question": "다른 정부 지원금과 중복해서 받을 수 있나요?", "answer": "정책 성격에 따라 중복 수혜가 가능한 항목과 제한되는 항목이 있으므로 주관 부처 안내를 확인해야 합니다."},
                {"question": "소득 인정액 기준은 어떻게 계산하나요?", "answer": f"{content.income_condition or '중위소득 기준'}을 따르며 모의계산기를 통해 사전 확인 가능합니다."},
                {"question": "온라인 신청이 어려운 경우 어디로 가야 하나요?", "answer": "가까운 읍·면·동 행정복지센터(주민센터)에 신분증을 지참하고 방문하시면 직원의 안내를 받아 접수할 수 있습니다."}
            ],
            "official_url": content.url,
            "tags": [content.category or "정부지원금", "복지혜택", blog.name, "신청방법"]
        }

    def render_html(self, article_data: Dict[str, Any], plan: PersonaDispatchPlan) -> str:
        """Render beautiful, semantic, responsive HTML matching the 10-step layout."""
        blog = plan.blog_config
        title = article_data.get("title", "")
        summary_items = "".join(f"<li>{s}</li>" for s in article_data.get("summary", []))
        
        steps_items = "".join(f"<div class='step-item'><span class='step-num'>{i+1}</span><p>{s}</p></div>" 
                              for i, s in enumerate(article_data.get("steps", [])))
        
        docs_items = "".join(f"<li><span class='check-icon'>✓</span> {d}</li>" 
                             for d in article_data.get("documents", []))
        
        faqs_items = "".join(
            f"<details class='faq-item'><summary><strong>Q. {faq['question']}</strong></summary><div class='faq-ans'><p>{faq['answer']}</p></div></details>"
            for faq in article_data.get("faqs", [])
        )

        html = f"""<!-- Welfare Content Engine V1.0 - Persona: {blog.persona_name} -->
<div class="welfare-post-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.8; color: #222; max-width: 780px; margin: 0 auto; word-break: keep-all;">

  <!-- Persona & Category Badge -->
  <div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;">
    <span style="background: #2563eb; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">{blog.persona_name} 브리핑</span>
    <span style="background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">{blog.name} 추천</span>
  </div>

  <!-- Persona Intro -->
  <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 16px 20px; border-radius: 0 8px 8px 0; margin-bottom: 24px;">
    <p style="margin: 0; font-size: 16px; color: #334155; font-weight: 500;">
      {plan.lead_intro}
    </p>
  </div>

  <!-- 1. 핵심 요약 (3줄 요약 박스) -->
  <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 20px 24px; margin-bottom: 32px;">
    <h3 style="margin: 0 0 12px 0; font-size: 18px; color: #1e40af; display: flex; align-items: center; gap: 8px;">
      📌 핵심 요약 3줄 브리핑
    </h3>
    <ul style="margin: 0; padding-left: 20px; color: #1e3a8a; font-size: 15px;">
      {summary_items}
    </ul>
  </div>

  <!-- 2. 지원 대상자 설명 -->
  <h2 style="font-size: 22px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; margin-bottom: 16px;">
    1. 누가 지원받을 수 있나요? (지원 자격)
  </h2>
  <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 20px; margin-bottom: 28px; white-space: pre-line;">
{article_data.get("target_desc", "")}
  </div>

  <!-- 3. 지원 내용 및 지원 금액 -->
  <h2 style="font-size: 22px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; margin-bottom: 16px;">
    2. 어떤 혜택과 지원 금액을 받나요?
  </h2>
  <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 20px 24px; margin-bottom: 28px;">
    <p style="margin: 0 0 10px 0; font-size: 16px; color: #166534; font-weight: 600;">
      💰 지원 규모: {article_data.get("amount_desc", "")}
    </p>
    <p style="margin: 0; font-size: 15px; color: #15803d;">
      {article_data.get("benefits", "")}
    </p>
  </div>

  <!-- 4. 신청 기간 -->
  <h2 style="font-size: 22px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; margin-bottom: 16px;">
    3. 신청 기간 및 마감 일정
  </h2>
  <div style="background: #fff7ed; border-left: 4px solid #ea580c; padding: 14px 18px; margin-bottom: 28px;">
    <p style="margin: 0; font-size: 15px; color: #9a3412; font-weight: 600;">
      ⏰ {article_data.get("period_desc", "")}
    </p>
  </div>

  <!-- 5. 신청 방법 (단계별 프로세스) -->
  <h2 style="font-size: 22px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; margin-bottom: 16px;">
    4. 어떻게 신청하나요? (신청 절차)
  </h2>
  <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 28px;">
    {steps_items}
  </div>

  <!-- 6. 필요 서류 -->
  <h2 style="font-size: 22px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; margin-bottom: 16px;">
    5. 제출해야 할 필수 서류
  </h2>
  <ul style="list-style: none; padding: 0; margin-bottom: 28px; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px;">
    {docs_items}
  </ul>

  <!-- 7. 자주 묻는 질문 (FAQ) -->
  <h2 style="font-size: 22px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; margin-bottom: 16px;">
    6. 자주 묻는 질문 (FAQ)
  </h2>
  <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 36px;">
    {faqs_items}
  </div>

  <!-- 8. 공식 링크 (CTA) -->
  <div style="background: #1e293b; border-radius: 12px; padding: 24px; text-align: center; color: #fff; margin-bottom: 20px;">
    <h3 style="margin: 0 0 10px 0; font-size: 18px; color: #fff;">정부 공식 홈페이지 바로가기</h3>
    <p style="margin: 0 0 18px 0; font-size: 14px; color: #cbd5e1;">자격 요건 조회 및 온라인 신청은 주관 부처 공식 시스템에서 안전하게 진행하세요.</p>
    <a href="{article_data.get('official_url', '#')}" target="_blank" rel="noopener noreferrer" 
       style="display: inline-block; background: #2563eb; color: #fff; font-weight: 700; text-decoration: none; padding: 12px 32px; border-radius: 30px; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
      공식 접수처 바로가기 ➔
    </a>
  </div>

</div>
"""
        return html
