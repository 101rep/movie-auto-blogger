import unittest
import random
from app.modules.travel.title_generator import TitleGenerator

class TestTitleGenerator(unittest.TestCase):
    def setUp(self):
        random.seed(0)
        class MockItem:
            def __init__(self, dest="제주도", dur="2박 3일"):
                self.destination = dest
                self.duration = dur
        self.item = MockItem()

    def test_generate_ctr_title_length(self):
        title = TitleGenerator.generate_ctr_title(self.item)
        self.assertTrue(len(title) <= TitleGenerator.MAX_LENGTH)

    def test_destination_in_title(self):
        title = TitleGenerator.generate_ctr_title(self.item)
        self.assertIn("제주도", title)

    def test_duration_in_title(self):
        title = TitleGenerator.generate_ctr_title(self.item)
        self.assertIn("2박 3일", title)

    def test_returns_string(self):
        title = TitleGenerator.generate_ctr_title(self.item)
        self.assertIsInstance(title, str)

    def test_bracket_format(self):
        title = TitleGenerator.generate_ctr_title(self.item)
        self.assertIn("[", title)
        self.assertIn("]", title)

    def test_osaka_strips_english(self):
        class OsakaItem:
            destination = "오사카 (Osaka)"
            duration = "3박 4일"
        title = TitleGenerator.generate_ctr_title(OsakaItem())
        self.assertIn("오사카", title)
        self.assertNotIn("(Osaka)", title)

    def test_fukuoka_strips_english(self):
        class FukuokaItem:
            destination = "후쿠오카 (Fukuoka)"
            duration = "2박 3일"
        title = TitleGenerator.generate_ctr_title(FukuokaItem())
        self.assertIn("후쿠오카", title)
        self.assertNotIn("(Fukuoka)", title)

    def test_unknown_city_fallback(self):
        class UnknownItem:
            destination = "하노이 (Hanoi)"
            duration = "3박 4일"
        title = TitleGenerator.generate_ctr_title(UnknownItem())
        self.assertIn("하노이", title)
        self.assertTrue(len(title) <= TitleGenerator.MAX_LENGTH)

    def test_multiple_generations_are_varied(self):
        random.seed(None)
        titles = set()
        for _ in range(20):
            titles.add(TitleGenerator.generate_ctr_title(self.item))
        self.assertGreaterEqual(len(titles), 3)

if __name__ == "__main__":
    unittest.main()

