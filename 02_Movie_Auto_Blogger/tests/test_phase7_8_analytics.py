"""Tests for Phase 7 & 8: Search Console, Web Traffic, and Revenue Analytics."""
import pytest
from app.services.analytics_service import (
    AnalyticsHubService,
    BaseRevenueProvider,
    BaseSearchConsoleProvider,
    BaseTrafficAnalyticsProvider,
    ContentPerformanceSummary,
    DefaultRevenueProvider,
    DefaultSearchConsoleProvider,
    DefaultTrafficAnalyticsProvider,
    IntegrationStatus,
    RevenueMetrics,
    SearchMetrics,
    TrafficMetrics,
)


@pytest.mark.asyncio
async def test_search_console_not_configured_by_default():
    """Verify Search Console defaults safely to NOT_CONFIGURED without fake numbers."""
    provider = DefaultSearchConsoleProvider(credentials_available=False)
    metrics = await provider.get_search_metrics("dune-part-two-review")

    assert metrics.status == IntegrationStatus.NOT_CONFIGURED
    assert metrics.impressions == 0
    assert metrics.clicks == 0
    assert "인증 정보가 구성되지 않았습니다" in metrics.message


@pytest.mark.asyncio
async def test_traffic_analytics_not_configured_by_default():
    """Verify Web Traffic defaults safely to NOT_CONFIGURED without fake numbers."""
    provider = DefaultTrafficAnalyticsProvider(credentials_available=False)
    metrics = await provider.get_traffic_metrics("dune-part-two-review")

    assert metrics.status == IntegrationStatus.NOT_CONFIGURED
    assert metrics.page_views == 0
    assert metrics.unique_visitors == 0


@pytest.mark.asyncio
async def test_revenue_not_configured_by_default():
    """Verify AdSense defaults safely to NOT_CONFIGURED without fake numbers."""
    provider = DefaultRevenueProvider(credentials_available=False)
    metrics = await provider.get_revenue_metrics("dune-part-two-review")

    assert metrics.status == IntegrationStatus.NOT_CONFIGURED
    assert metrics.estimated_earnings == 0.0
    assert metrics.page_rpm == 0.0


@pytest.mark.asyncio
async def test_analytics_hub_aggregation():
    """Verify AnalyticsHub aggregates all 3 dimensions into a unified summary."""
    hub = AnalyticsHubService()
    summary: ContentPerformanceSummary = await hub.get_post_performance(
        slug="inception-review",
        post_id=42
    )

    assert summary.post_id == 42
    assert summary.slug == "inception-review"
    assert summary.search.status == IntegrationStatus.NOT_CONFIGURED
    assert summary.traffic.status == IntegrationStatus.NOT_CONFIGURED
    assert summary.revenue.status == IntegrationStatus.NOT_CONFIGURED
    assert summary.has_active_integrations is False


@pytest.mark.asyncio
async def test_connected_provider_mock():
    """Verify that when real/mock providers are connected, real data is accurately processed."""
    class MockSearchProvider(BaseSearchConsoleProvider):
        async def get_search_metrics(self, slug_or_url: str) -> SearchMetrics:
            return SearchMetrics(
                status=IntegrationStatus.CONNECTED,
                impressions=1250,
                clicks=85,
                ctr=6.8,
                average_position=4.2,
                message="데이터 수집 완료"
            )

    class MockRevenueProvider(BaseRevenueProvider):
        async def get_revenue_metrics(self, slug_or_url: str) -> RevenueMetrics:
            return RevenueMetrics(
                status=IntegrationStatus.CONNECTED,
                estimated_earnings=15.40,
                page_rpm=12.32,
                ad_clicks=48,
                ad_ctr=3.84,
                message="애드센스 정산 완료"
            )

    hub = AnalyticsHubService(
        search_provider=MockSearchProvider(),
        revenue_provider=MockRevenueProvider()
    )
    summary = await hub.get_post_performance("hit-movie", post_id=99)

    assert summary.has_active_integrations is True
    assert summary.search.status == IntegrationStatus.CONNECTED
    assert summary.search.impressions == 1250
    assert summary.search.clicks == 85
    assert summary.revenue.status == IntegrationStatus.CONNECTED
    assert summary.revenue.estimated_earnings == 15.40
    assert summary.revenue.page_rpm == 12.32
