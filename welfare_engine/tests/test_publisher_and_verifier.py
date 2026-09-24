"""Tests for WordPress Publisher and Verification Agent."""
import pytest
from unittest.mock import AsyncMock, patch
from welfare_engine.config import BLOG_A
from welfare_engine.database.models import WelfarePublication
from welfare_engine.publisher.wordpress_publisher import WordPressWelfarePublisher
from welfare_engine.agent.verifier import WelfareVerifierAgent
from welfare_engine.reporter.telegram_reporter import WelfareTelegramReporter


def test_01_publisher_auth_header():
    """Verify WordPress publisher builds correct HTTP Basic auth header."""
    publisher = WordPressWelfarePublisher(BLOG_A)
    assert publisher.auth_header.startswith("Basic ")


@pytest.mark.asyncio
async def test_02_verifier_logic_and_alerts():
    """Verify Verifier agent checks real status, URL, and dispatches failure alerts."""
    mock_reporter = AsyncMock(spec=WelfareTelegramReporter)
    mock_reporter.send_verification_failure_alert = AsyncMock(return_value=True)

    verifier = WelfareVerifierAgent(reporter=mock_reporter)

    # 1. Test success verification mock
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={
            "id": 999,
            "status": "future",
            "link": "https://welfare25.travelpick24.com/policy-999/",
            "date": "2026-09-24T14:00:00"
        })
        mock_get.return_value.__aenter__.return_value = mock_resp

        pub = WelfarePublication(
            content_id=1,
            blog_key="BLOG_A",
            site_id=7,
            persona_title="테스트 글",
            wp_post_id=999
        )
        ok = await verifier.verify_and_record(pub, BLOG_A, expected_status="future")
        assert ok is True
        assert pub.verification_status == "VERIFIED"
        assert pub.wp_status == "future"
        assert pub.wp_url == "https://welfare25.travelpick24.com/policy-999/"

    # 2. Test failure verification mock
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 404
        mock_resp.text = AsyncMock(return_value="Not Found")
        mock_get.return_value.__aenter__.return_value = mock_resp

        pub_fail = WelfarePublication(
            content_id=2,
            blog_key="BLOG_A",
            site_id=7,
            persona_title="실패 글",
            wp_post_id=888
        )
        ok = await verifier.verify_and_record(pub_fail, BLOG_A, expected_status="future")
        assert ok is False
        assert pub_fail.verification_status == "FAILED"
        assert "실패" in pub_fail.error_message
        # Verify alert was triggered
        assert mock_reporter.send_verification_failure_alert.called
