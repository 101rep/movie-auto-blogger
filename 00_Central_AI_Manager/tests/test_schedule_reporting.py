# -*- coding: utf-8 -*-
"""Unit tests for 7-blog scheduled posts reporting integration."""
import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from monitor.daily_reporter import DailyExecutiveReporter

class TestScheduleReporting(unittest.TestCase):

    def setUp(self):
        self.reporter = DailyExecutiveReporter()

    def test_01_collect_scheduled_posts_structure(self):
        data = self.reporter._collect_scheduled_posts_data()
        self.assertEqual(data["total_target"], 28)
        self.assertEqual(len(data["sites"]), 7)
        
        # Verify site 3 (아이템픽24) is strictly excluded
        site_ids = [s["id"] for s in data["sites"]]
        self.assertNotIn(3, site_ids)
        self.assertEqual(site_ids, [1, 2, 4, 5, 6, 7, 8])

        # Verify each site has exactly 4 slots
        for s in data["sites"]:
            self.assertEqual(len(s["slots"]), 4)
            for slot in s["slots"]:
                self.assertIn("icon", slot)
                self.assertIn("time", slot)
                self.assertIn("status", slot)
                self.assertIn("title", slot)

    def test_02_generate_schedule_report_content(self):
        report = asyncio.run(self.reporter.generate_schedule_report())
        self.assertIn("7대 블로그 일일 4개 예약발행 일정", report)
        self.assertIn("아이템픽24 제외", report)
        self.assertIn("28편", report)
        self.assertIn("트래블픽24", report)
        self.assertIn("트렌드스팟24", report)
        self.assertIn("뉴스픽24", report)

    def test_03_traffic_report_includes_schedule(self):
        # Mock traffic data collection to avoid needing live MySQL connection during unit test
        mock_traffic = {
            "date": "2026년 09월 24일 09:00 KST",
            "total_today_vis": 10,
            "total_today_pv": 25,
            "total_yest_vis": 8,
            "total_yest_pv": 20,
            "total_month_vis": 150,
            "total_month_pv": 320,
            "sites": [
                {"id": 1, "name": "트래블픽24", "url": "travelpick24.com", "today_vis": 2, "today_pv": 5, "yest_vis": 1, "yest_pv": 3, "month_vis": 20, "month_pv": 50},
                {"id": 3, "name": "아이템픽24", "url": "item.travelpick24.com", "today_vis": 1, "today_pv": 2, "yest_vis": 0, "yest_pv": 0, "month_vis": 10, "month_pv": 20}
            ]
        }
        with patch.object(self.reporter, "_collect_traffic_data", return_value=mock_traffic):
            report = asyncio.run(self.reporter.generate_evening_traffic_report("09:00 KST 오전"))
            # 1. Visitor metrics must be present
            self.assertIn("8대 블로그 통합 일일 트래픽 리포트", report)
            self.assertIn("오늘 순방문자", report)
            self.assertIn("10 명", report)
            # 2. Scheduled posts section must be present
            self.assertIn("7대 블로그 일일 4개 예약발행 일정", report)
            self.assertIn("아이템픽24 제외", report)
            self.assertIn("28편", report)
            self.assertIn("트렌드스팟24", report)

    def test_04_intent_router_schedule_command(self):
        from router.intent_router import IntentRouter
        router = IntentRouter()
        with patch.object(self.reporter, "generate_schedule_report", new=AsyncMock(return_value="SCHEDULE_OK")):
            with patch("monitor.daily_reporter.daily_reporter", self.reporter):
                reply, _ = asyncio.run(router.route_and_execute("/schedule", "test_user"))
                self.assertEqual(reply, "SCHEDULE_OK")

if __name__ == "__main__":
    unittest.main()
