import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

from services.itempick_queue_service import itempick_queue_service
from router.intent_router import IntentRouter
from monitor.daily_reporter import DailyExecutiveReporter, KST, TRAFFIC_REPORT_HOURS


class TestItemPickDedupAndTrafficReports(unittest.TestCase):

    def test_01_normalize_url(self):
        url1 = "https://www.coupang.com/vp/products/12345678?itemId=999&vendorItemId=888&utm_source=affiliate&subid=tg123&trackingCode=abc"
        norm1 = itempick_queue_service.normalize_url(url1)
        self.assertNotIn("utm_source", norm1)
        self.assertNotIn("subid", norm1)
        self.assertNotIn("trackingCode", norm1)
        self.assertIn("itemId=999", norm1)
        self.assertIn("vendorItemId=888", norm1)
        self.assertIn("coupang.com/vp/products/12345678", norm1)

    def test_02_normalize_title_for_cmp(self):
        t1 = "[구매 가이드] 오늘의집 단독 모듈소파 / 레이어 패브릭 소파, 중소기업 제품 대신 골라야 하는 결정적 이유"
        norm1 = itempick_queue_service._normalize_title_for_cmp(t1)
        self.assertNotIn("구매", norm1)
        self.assertNotIn("가이드", norm1)
        self.assertIn("오늘의집", norm1)
        self.assertIn("모듈소파", norm1)
        self.assertIn("레이어", norm1)
        self.assertIn("패브릭", norm1)

    def test_03_check_duplicate_against_existing(self):
        # Existing post 118 on item.travelpick24.com
        is_dup, info = itempick_queue_service.check_duplicate("https://item.travelpick24.com/")
        self.assertTrue(is_dup)
        self.assertIsNotNone(info)
        self.assertEqual(info["match_type"], "URL")
        self.assertIn("동일 제휴 URL", info["reason"])

    def test_04_check_duplicate_title(self):
        # Existing title on item.travelpick24.com
        is_dup, info = itempick_queue_service.check_duplicate("https://new-unique-url-9999.com/prod", "오늘의집 단독 모듈소파")
        self.assertTrue(is_dup)
        self.assertIsNotNone(info)
        self.assertEqual(info["match_type"], "TITLE")
        self.assertIn("동일 상품 제목", info["reason"])

    def test_05_check_unique_url_and_title(self):
        is_dup, info = itempick_queue_service.check_duplicate("https://super-unique-test-url-2026.com/product/abcde", "전혀다른가상의제품999XYZ")
        self.assertFalse(is_dup)
        self.assertIsNone(info)

    def test_06_add_and_publish_now_rejection(self):
        # Passing an existing URL should be rejected immediately
        res = itempick_queue_service.add_and_publish_now("https://item.travelpick24.com/", "test_user")
        self.assertEqual(res.get("status"), "REJECTED_DUPLICATE")
        self.assertIn("existing", res)
        self.assertIn("reason", res)

    def test_07_traffic_report_hours_config(self):
        self.assertEqual(TRAFFIC_REPORT_HOURS, [9, 15, 21])

    def test_08_traffic_report_scheduled_trigger(self):
        reporter = DailyExecutiveReporter()
        bot = AsyncMock()
        target_chat_id = "6290024230"

        # Mock datetime to 09:00 KST
        mock_now = datetime(2026, 9, 24, 9, 0, 0, tzinfo=KST)
        with patch("monitor.daily_reporter.datetime") as mock_dt, \
             patch.object(reporter, "generate_traffic_report", new=AsyncMock(return_value="Traffic Report 09:00")):
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            # First cycle at 09:00 should fire
            fired = asyncio.run(reporter.check_and_send_scheduled(bot, target_chat_id))
            self.assertTrue(fired)
            bot.send_message.assert_called_once()
            self.assertIn("2026-09-24_9", reporter.sent_traffic_keys)

            # Second cycle in the same hour must NOT fire again (deduplication guard)
            bot.send_message.reset_mock()
            fired_again = asyncio.run(reporter.check_and_send_scheduled(bot, target_chat_id))
            self.assertFalse(fired_again)
            bot.send_message.assert_not_called()

        # Mock datetime to 15:00 KST
        mock_now_15 = datetime(2026, 9, 24, 15, 2, 0, tzinfo=KST)
        with patch("monitor.daily_reporter.datetime") as mock_dt, \
             patch.object(reporter, "generate_traffic_report", new=AsyncMock(return_value="Traffic Report 15:00")):
            mock_dt.now.return_value = mock_now_15
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            fired = asyncio.run(reporter.check_and_send_scheduled(bot, target_chat_id))
            self.assertTrue(fired)
            self.assertIn("2026-09-24_15", reporter.sent_traffic_keys)

        # Mock datetime to 21:00 KST
        mock_now_21 = datetime(2026, 9, 24, 21, 1, 0, tzinfo=KST)
        with patch("monitor.daily_reporter.datetime") as mock_dt, \
             patch.object(reporter, "generate_traffic_report", new=AsyncMock(return_value="Traffic Report 21:00")):
            mock_dt.now.return_value = mock_now_21
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            fired = asyncio.run(reporter.check_and_send_scheduled(bot, target_chat_id))
            self.assertTrue(fired)
            self.assertIn("2026-09-24_21", reporter.sent_traffic_keys)

    def test_09_intent_router_duplicate_rejection_message(self):
        router = IntentRouter()
        # Simulate sending a duplicate URL to intent router
        msg, markup = asyncio.run(router.route_and_execute("https://item.travelpick24.com/", "test_user"))
        self.assertIn("아이템픽24 등록 거절 안내", msg)
        self.assertIn("거절 사유", msg)
        self.assertIn("기존 등록 글", msg)
        self.assertIn("기존 글 링크", msg)


if __name__ == "__main__":
    unittest.main()
