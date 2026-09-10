"""TDD: frequency summary top-100 with latest-year weight."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from frequency import cluster_items, importance, normalize_stem, top_n  # noqa: E402


class TestNormalize(unittest.TestCase):
    def test_strips_non_korean_digits(self):
        self.assertEqual(normalize_stem("디자인 요소? ①"), "디자인요소")


class TestScore(unittest.TestCase):
    def test_latest_restore_year_weighted(self):
        old = importance(years=[2017], count=1, keywords=0, latest=False)
        new = importance(years=[2025], count=1, keywords=0, latest=True)
        self.assertGreater(new, old)
        self.assertEqual(old, 3 + 1)
        self.assertEqual(new, (3 + 1) * 1.5)


class TestCluster(unittest.TestCase):
    def test_similar_stems_merge(self):
        items = [
            {"id": "a", "stem": "실내디자인일반요소", "year": 2017},
            {"id": "b", "stem": "실내디자인일반요소문제", "year": 2025},
            {"id": "c", "stem": "철근콘크리트슬래브", "year": 2018},
        ]
        clusters = cluster_items(items, threshold=0.6)
        self.assertEqual(len(clusters), 2)


class TestTopN(unittest.TestCase):
    def test_cap_100(self):
        items = [
            {"id": str(i), "stem": chr(0xAC00 + i * 17), "year": 2017}
            for i in range(120)
        ]
        ranked = top_n(items, limit=100)
        self.assertEqual(len(ranked), 100)


if __name__ == "__main__":
    unittest.main()
