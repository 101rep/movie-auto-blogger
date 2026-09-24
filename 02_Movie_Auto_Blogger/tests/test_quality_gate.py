"""Unit tests for the deterministic quality gate service."""
from app.database.models import QualityStatusEnum
from app.services.quality_service import QualityGateService
from tests.test_ai_providers import create_sample_article


def test_quality_gate_clean_pass():
    """Verify standard complete article receives PASS status."""
    article = create_sample_article()
    status, issues = QualityGateService.evaluate(article, expected_movie_title="인사이드 아웃 2")

    assert status == QualityStatusEnum.PASS
    assert len(issues) == 0


def test_quality_gate_placeholder_fails():
    """Verify placeholder text triggers immediate FAIL status."""
    article = create_sample_article()
    article.introduction = "이 영화는 [여기에 소개 내용을 입력하세요] 픽사의 명작입니다."

    status, issues = QualityGateService.evaluate(article, expected_movie_title="인사이드 아웃 2")
    assert status == QualityStatusEnum.FAIL
    assert any("플레이스홀더" in issue for issue in issues)


def test_quality_gate_raw_json_leakage_fails():
    """Verify raw JSON leakage triggers immediate FAIL status."""
    article = create_sample_article()
    article.conclusion = '마무리 결론입니다. ```json\n{"title": "test"}\n```'

    status, issues = QualityGateService.evaluate(article, expected_movie_title="인사이드 아웃 2")
    assert status == QualityStatusEnum.FAIL
    assert any("JSON" in issue for issue in issues)


def test_quality_gate_api_key_leakage_fails():
    """Verify secret token in generated text triggers immediate FAIL status."""
    article = create_sample_article()
    article.conclusion = "마무리 내용입니다. 문의 시 sk-1234567890abcdef1234 키를 사용하지 마세요."

    status, issues = QualityGateService.evaluate(article, expected_movie_title="인사이드 아웃 2")
    assert status == QualityStatusEnum.FAIL
    assert any("API 키" in issue or "민감 문자열" in issue for issue in issues)


def test_quality_gate_minor_issue_enters_review():
    """Verify minor issues (e.g. short excerpt) result in REVIEW status rather than publish."""
    article = create_sample_article()
    article.excerpt = "너무 짧은 요약문입니다."  # < 40 chars

    status, issues = QualityGateService.evaluate(article, expected_movie_title="인사이드 아웃 2")
    assert status == QualityStatusEnum.REVIEW
    assert any("excerpt" in issue for issue in issues)
