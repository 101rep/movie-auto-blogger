from typing import Dict, Any
from integrations.interfaces import AnalyticsProvider

class MockAnalyticsProvider(AnalyticsProvider):
    def get_metrics(self, content_id: str) -> Dict[str, Any]:
        return {
            'content_id': content_id,
            'views': 4520,
            'likes': 184,
            'replies': 37,
            'shares': 19,
            'clicks': 142,
            'estimated_conversion': 8
        }
