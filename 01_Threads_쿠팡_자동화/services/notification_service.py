import requests
from typing import Dict, Any, Optional
from config import settings

class NotificationService:
    """
    Webhook Notification Service (Discord / Slack / Telegram).
    Sends instant alerts upon automated post publishing, review warnings, or daily revenue summaries.
    """
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or getattr(settings, "WEBHOOK_URL", None)

    def send_post_published_alert(self, title: str, post_id: str, preview_url: Optional[str] = None) -> bool:
        content = (
            f"🚀 **[Threads x 쿠팡 자동화] 새 글이 성공적으로 발행되었습니다!**\n"
            f"• **제목**: {title}\n"
            f"• **포스트 ID**: `{post_id}`\n"
            f"• **링크**: {preview_url or 'https://threads.net'}\n"
            f"• **공정위 표기**: 규정 준수 검수 완료 ✅"
        )
        return self._dispatch(content)

    def send_daily_learning_report(self, best_angle: str, total_views: int, total_clicks: int, revenue: int) -> bool:
        content = (
            f"📊 **[일일 자가 학습 루프 정산 리포트]**\n"
            f"• **최고 성과 각도**: `{best_angle}`\n"
            f"• **누적 노출수**: {total_views:,}회\n"
            f"• **총 클릭수**: {total_clicks:,}회\n"
            f"• **추정 누적 수익**: **{revenue:,}원** 💰"
        )
        return self._dispatch(content)

    def _dispatch(self, message: str) -> bool:
        if not self.webhook_url:
            # If webhook URL is not configured, simulate log output
            print(f"[Notification] (Simulated Webhook Alert)\n{message}")
            return True

        try:
            res = requests.post(
                self.webhook_url,
                json={"content": message, "text": message},
                timeout=5
            )
            return res.status_code in [200, 204]
        except Exception as e:
            print(f"[Notification] Failed to dispatch webhook: {e}")
            return False