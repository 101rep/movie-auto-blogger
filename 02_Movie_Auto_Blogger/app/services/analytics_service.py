"""Search Console, Web Analytics, and Revenue Analytics layer with graceful unconfigured states."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger("analytics_service")


class IntegrationStatus(str, Enum):
    """External service integration readiness state."""
    NOT_CONFIGURED = "NOT_CONFIGURED"    # API credentials or integration not set up
    CONNECTED = "CONNECTED"              # Integrated and actively returning real data
    NO_DATA = "NO_DATA"                  # Integrated, but no data available for this query
    ERROR = "ERROR"                      # API error during fetch


class SearchMetrics(BaseModel):
    """Search console query performance metrics."""
    provider_name: str = "GoogleSearchConsole"
    status: IntegrationStatus = IntegrationStatus.NOT_CONFIGURED
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0                     # Click-through rate % (e.g. 3.5%)
    average_position: float = 0.0        # Average rank in SERP (e.g. 8.2)
    top_queries: List[Dict[str, Any]] = Field(default_factory=list)
    message: str = "Search Console 연동이 설정되지 않았습니다 (API 키 미설정)."


class TrafficMetrics(BaseModel):
    """Web traffic and engagement analytics."""
    provider_name: str = "WebAnalytics"
    status: IntegrationStatus = IntegrationStatus.NOT_CONFIGURED
    page_views: int = 0
    unique_visitors: int = 0
    avg_duration_seconds: float = 0.0
    bounce_rate: float = 0.0
    message: str = "웹 로그/GA4 분석 연동이 설정되지 않았습니다."


class RevenueMetrics(BaseModel):
    """Monetization and ad revenue analytics."""
    provider_name: str = "AdSense"
    status: IntegrationStatus = IntegrationStatus.NOT_CONFIGURED
    estimated_earnings: float = 0.0      # Currency amount
    page_rpm: float = 0.0                # Revenue per 1,000 impressions
    ad_clicks: int = 0
    ad_ctr: float = 0.0                  # Ad click-through rate %
    currency: str = "USD"
    message: str = "애드센스/수익 연동이 설정되지 않았습니다 (ADSENSE_CLIENT_ID 미설정)."


class ContentPerformanceSummary(BaseModel):
    """Unified performance dashboard summary for a published article."""
    post_id: Optional[int] = None
    slug: str
    search: SearchMetrics
    traffic: TrafficMetrics
    revenue: RevenueMetrics
    has_active_integrations: bool = False


# Provider Interfaces
class BaseSearchConsoleProvider(ABC):
    @abstractmethod
    async def get_search_metrics(self, slug_or_url: str) -> SearchMetrics:
        pass


class BaseTrafficAnalyticsProvider(ABC):
    @abstractmethod
    async def get_traffic_metrics(self, slug_or_url: str) -> TrafficMetrics:
        pass


class BaseRevenueProvider(ABC):
    @abstractmethod
    async def get_revenue_metrics(self, slug_or_url: str) -> RevenueMetrics:
        pass


# Default Providers (Never fabricate numbers; explicitly report NOT_CONFIGURED)
class DefaultSearchConsoleProvider(BaseSearchConsoleProvider):
    def __init__(self, credentials_available: bool = False):
        self.credentials_available = credentials_available

    async def get_search_metrics(self, slug_or_url: str) -> SearchMetrics:
        if not self.credentials_available:
            return SearchMetrics(
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Google Search Console API 인증 정보가 구성되지 않았습니다."
            )
        return SearchMetrics(
            status=IntegrationStatus.NO_DATA,
            message="Search Console 연결됨: 최근 28일간 집계된 검색 노출 데이터가 없습니다."
        )


class DefaultTrafficAnalyticsProvider(BaseTrafficAnalyticsProvider):
    def __init__(self, credentials_available: bool = False):
        self.credentials_available = credentials_available

    async def get_traffic_metrics(self, slug_or_url: str) -> TrafficMetrics:
        if not self.credentials_available:
            return TrafficMetrics(
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Google Analytics (GA4) 측정 ID가 구성되지 않았습니다."
            )
        return TrafficMetrics(
            status=IntegrationStatus.NO_DATA,
            message="트래픽 통계 연결됨: 아직 방문자 유입이 기록되지 않았습니다."
        )


class DefaultRevenueProvider(BaseRevenueProvider):
    def __init__(self, credentials_available: bool = False):
        self.credentials_available = credentials_available

    async def get_revenue_metrics(self, slug_or_url: str) -> RevenueMetrics:
        if not self.credentials_available:
            return RevenueMetrics(
                status=IntegrationStatus.NOT_CONFIGURED,
                message="Google AdSense 계정이 연동되지 않았습니다."
            )
        return RevenueMetrics(
            status=IntegrationStatus.NO_DATA,
            message="애드센스 연동됨: 집계된 광고 수익이 아직 없습니다."
        )


class AnalyticsHubService:
    """Aggregates multi-source analytics without ever faking unconnected data."""

    def __init__(
        self,
        search_provider: Optional[BaseSearchConsoleProvider] = None,
        traffic_provider: Optional[BaseTrafficAnalyticsProvider] = None,
        revenue_provider: Optional[BaseRevenueProvider] = None
    ):
        self.search_provider = search_provider or DefaultSearchConsoleProvider()
        self.traffic_provider = traffic_provider or DefaultTrafficAnalyticsProvider()
        self.revenue_provider = revenue_provider or DefaultRevenueProvider()

    async def get_post_performance(self, slug: str, post_id: Optional[int] = None) -> ContentPerformanceSummary:
        """Fetch unified search, traffic, and revenue metrics for a post."""
        search = await self.search_provider.get_search_metrics(slug)
        traffic = await self.traffic_provider.get_traffic_metrics(slug)
        revenue = await self.revenue_provider.get_revenue_metrics(slug)

        has_active = any(
            m.status == IntegrationStatus.CONNECTED
            for m in [search, traffic, revenue]
        )

        return ContentPerformanceSummary(
            post_id=post_id,
            slug=slug,
            search=search,
            traffic=traffic,
            revenue=revenue,
            has_active_integrations=has_active
        )
