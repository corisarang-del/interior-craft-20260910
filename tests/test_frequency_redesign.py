import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from frequency import (  # noqa: E402
    cluster_items,
    cluster_score_components,
    rank_clusters,
)
from build_summary import stems_from_round  # noqa: E402


class TestFrequencyRedesign(unittest.TestCase):
    def test_repeated_types_are_ranked_before_singletons(self):
        clusters = [
            {"stem": "최신단독", "members": [{"id": "2025-1회#1", "year": 2025, "round": "2025-1회", "num": 1}]},
            {"stem": "반복유형", "members": [
                {"id": "2018-1회#1", "year": 2018, "round": "2018-1회", "num": 1},
                {"id": "2020-1회#1", "year": 2020, "round": "2020-1회", "num": 1},
            ]},
        ]
        ranked = rank_clusters(clusters)
        self.assertEqual(ranked[0]["category"], "반복 출제 핵심 유형")
        self.assertEqual(ranked[1]["category"], "단독 출제 참고")

    def test_frequency_and_latest_scores_are_separate(self):
        c = {"members": [
            {"year": 2018, "round": "2018-1회", "num": 1},
            {"year": 2024, "round": "2024-1회", "num": 1},
        ]}
        score = cluster_score_components(c)
        self.assertEqual(score["frequency_score"], 8)
        self.assertEqual(score["latest_score"], 1)
        self.assertEqual(score["latest_years"], [2024])
        self.assertNotIn("weighted_score", score)

    def test_tie_break_is_stable_and_independent_of_input_order(self):
        a = {"stem": "A", "members": [{"id": "2024-1회#2", "year": 2024, "round": "2024-1회", "num": 2}]}
        b = {"stem": "B", "members": [{"id": "2024-1회#1", "year": 2024, "round": "2024-1회", "num": 1}]}
        self.assertEqual([x["stable_key"] for x in rank_clusters([a, b])], ["2024-1회#01", "2024-1회#02"])
        self.assertEqual([x["stable_key"] for x in rank_clusters([b, a])], ["2024-1회#01", "2024-1회#02"])

    def test_latest_score_is_only_a_secondary_sort_key(self):
        old = {"stem": "old", "members": [{"id": "2017-1회#1", "year": 2017, "round": "2017-1회", "num": 1}]}
        new = {"stem": "new", "members": [{"id": "2025-1회#1", "year": 2025, "round": "2025-1회", "num": 1}]}
        ranked = rank_clusters([old, new])
        self.assertEqual([x["category"] for x in ranked], ["단독 출제 참고", "단독 출제 참고"])
        self.assertEqual([x["stable_key"] for x in ranked], ["2017-1회#01", "2025-1회#01"])
        self.assertEqual([x["latest_score"] for x in ranked], [0, 1])
        self.assertEqual([x["frequency_score"] for x in ranked], [4, 4])

    def test_latest_year_does_not_change_frequency_rank(self):
        old = {"stem": "old", "members": [{"id": "2017-1회#1", "year": 2017, "round": "2017-1회", "num": 1}]}
        new = {"stem": "new", "members": [{"id": "2025-1회#1", "year": 2025, "round": "2025-1회", "num": 1}]}
        ranked = rank_clusters([new, old])
        self.assertEqual([x["stable_key"] for x in ranked], ["2017-1회#01", "2025-1회#01"])

    def test_2026_sungandang_is_excluded_from_frequency_input(self):
        self.assertEqual(stems_from_round({"source": "sungandang_pdf", "year": 2026, "id": "2026-1회"}), [])


if __name__ == "__main__":
    unittest.main()
