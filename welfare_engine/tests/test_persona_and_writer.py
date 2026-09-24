"""Tests for Persona Router and 10-Step Content Writer Agent."""
import pytest
from welfare_engine.config import WELFARE_BLOGS, BLOG_A, BLOG_B, BLOG_C
from welfare_engine.database.models import WelfareContent
from welfare_engine.agent.persona_router import WelfarePersonaRouter
from welfare_engine.agent.writer import WelfareWriterAgent


def test_01_persona_router_differentiation():
    """Verify one policy produces differentiated angles for eligible blogs without duplication."""
    router = WelfarePersonaRouter()

    # Policy 1: Youth Monthly Rent (Relevant for Blog A citizen and Blog B youth)
    content1 = WelfareContent(
        id=201,
        title="2026 청년월세 한시 특별지원 (최대 월 20만원 지원)",
        category="청년지원",
        target="무주택 청년 (만 19~34세)",
        amount="월 20만원",
        deadline="2026-12-31",
        url="https://gov.kr/rent-support"
    )
    plans1 = router.route(content1)
    blog_keys = [p.blog_key for p in plans1]
    assert "BLOG_A" in blog_keys
    assert "BLOG_B" in blog_keys
    assert "BLOG_C" not in blog_keys # Not a business policy!

    # Check distinct titles and angles
    plan_a = next(p for p in plans1 if p.blog_key == "BLOG_A")
    plan_b = next(p for p in plans1 if p.blog_key == "BLOG_B")
    assert plan_a.title != plan_b.title
    assert "친절한 복지 상담사" in plan_a.blog_config.persona_name
    assert "젊은 가족을 돕는 정책 전문가" in plan_b.blog_config.persona_name


@pytest.mark.asyncio
async def test_02_writer_10_step_structure_and_anti_cliche():
    """Verify writer fulfills the 10-step structure and avoids AI cliches."""
    writer = WelfareWriterAgent()
    router = WelfarePersonaRouter()

    content = WelfareContent(
        id=202,
        title="2026 부모급여 (0세 월 100만원 지원)",
        source="보건복지부",
        category="육아지원",
        target="만 0~1세 영유아 가정",
        age="만 0~1세",
        amount="월 100만원",
        deadline="상시접수",
        apply_method="정부24 및 주민센터",
        documents="신분증, 통장사본",
        url="https://gov.kr/parent-benefit"
    )

    plans = router.route(content)
    plan_b = next((p for p in plans if p.blog_key == "BLOG_B"), plans[0])

    data = await writer.generate_article_data(content, plan_b)
    # Check required fields
    assert "title" in data
    assert "summary" in data and len(data["summary"]) >= 3
    assert "target_desc" in data
    assert "benefits" in data
    assert "amount_desc" in data
    assert "period_desc" in data
    assert "steps" in data and len(data["steps"]) >= 3
    assert "documents" in data and len(data["documents"]) >= 1
    assert "faqs" in data and len(data["faqs"]) >= 2
    assert "official_url" in data

    # Check HTML rendering
    html = writer.render_html(data, plan_b)
    assert "welfare-post-container" in html
    assert "핵심 요약 3줄 브리핑" in html
    assert "1. 누가 지원받을 수 있나요?" in html
    assert "2. 어떤 혜택과 지원 금액을 받나요?" in html
    assert "3. 신청 기간 및 마감 일정" in html
    assert "4. 어떻게 신청하나요?" in html
    assert "5. 제출해야 할 필수 서류" in html
    assert "6. 자주 묻는 질문 (FAQ)" in html
    assert "공식 접수처 바로가기" in html

    # Anti-cliche check
    cliches = ["~에 대해 알아보겠습니다", "지금부터 살펴보겠습니다", "함께 알아보시죠"]
    for c in cliches:
        assert c not in html, f"Forbidden AI cliché found in HTML: {c}"
