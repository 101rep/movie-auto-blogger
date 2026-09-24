"""Tests for 1080x1080 Government Card News Image Generator."""
from PIL import Image
from welfare_engine.config import BLOG_A, BLOG_B, BLOG_C
from welfare_engine.database.models import WelfareContent
from welfare_engine.agent.image_generator import WelfareCardNewsGenerator


def test_01_card_news_dimensions_and_generation():
    """Verify generated thumbnail is exactly 1080x1080 with valid PNG encoding."""
    generator = WelfareCardNewsGenerator()
    content = WelfareContent(
        id=301,
        title="2026 청년도약계좌 5,000만원 목돈 형성 지원",
        category="청년지원",
        target="만 19~34세 일하는 청년",
        age="만 19~34세",
        amount="5년 만기 시 최대 5,000만원",
        deadline="매월 초 접수"
    )

    img_path = generator.generate_card_news(content, BLOG_B)
    assert img_path.exists()

    with Image.open(img_path) as im:
        assert im.size == (1080, 1080)
        assert im.format == "PNG"
