from config import settings
from integrations.interfaces import ProductProvider, AIProvider, ThreadsProvider, AnalyticsProvider
from integrations.providers.mock_product_provider import MockProductProvider
from integrations.providers.mock_ai_provider import MockAIProvider
from integrations.providers.real_ai_provider import RealAIProvider
from integrations.providers.mock_threads_provider import MockThreadsProvider
from integrations.providers.mock_analytics_provider import MockAnalyticsProvider

def get_product_provider() -> ProductProvider:
    if getattr(settings, "COUPANG_ACCESS_KEY", None) and getattr(settings, "COUPANG_SECRET_KEY", None):
        from integrations.coupang_api import CoupangPartnersAPI
        return CoupangPartnersAPI()
    return MockProductProvider()

def get_ai_provider() -> AIProvider:
    if settings.AI_PROVIDER in ["gemini", "openai"] and settings.AI_API_KEY:
        return RealAIProvider()
    return MockAIProvider()

def get_threads_provider() -> ThreadsProvider:
    if getattr(settings, "THREADS_ACCESS_TOKEN", None):
        from integrations.threads_api import ThreadsOfficialAPI
        return ThreadsOfficialAPI()
    return MockThreadsProvider()

def get_analytics_provider() -> AnalyticsProvider:
    if getattr(settings, "THREADS_ACCESS_TOKEN", None):
        from integrations.threads_api import ThreadsOfficialAPI
        return ThreadsOfficialAPI()
    return MockAnalyticsProvider()