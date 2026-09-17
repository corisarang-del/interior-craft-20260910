import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from frequency import (  # noqa: E402
    annotate_singletons,
    cluster_items,
    cluster_score_components,
    extract_concept_key,
    rank_clusters,
    rank_singletons,
    singleton_score_components,
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

    def test_singleton_score_rewards_related_concepts_and_core_topics(self):
        basic = {"topic": "조도", "related_years": [2018, 2021], "related_count": 3, "core": 5, "numeric": 1, "utility": 2}
        obscure = {"topic": "장식 세부용어", "related_years": [], "related_count": 0, "core": 1, "numeric": 0, "utility": 0}
        self.assertGreater(singleton_score_components(basic)["singleton_score"], singleton_score_components(obscure)["singleton_score"])

    def test_singleton_ranking_is_not_by_stable_id_first(self):
        old = {"stem": "A", "members": [{"id": "2017-1회#1", "year": 2017, "round": "2017-1회", "num": 1}], "related_years": [2018, 2021], "related_count": 3, "core": 5, "numeric": 1, "utility": 2}
        new = {"stem": "B", "members": [{"id": "2025-1회#1", "year": 2025, "round": "2025-1회", "num": 1}], "related_years": [], "related_count": 0, "core": 1, "numeric": 0, "utility": 0}
        ranked = rank_clusters([new, old])
        self.assertEqual(ranked[0]["stable_key"], "2017-1회#01")

    def test_singleton_concept_key_groups_related_terms(self):
        self.assertEqual(extract_concept_key("조도", "조도의 단위와 정의"), "조도")
        self.assertEqual(extract_concept_key("고력볼트 접합", "철골구조의 볼트 접합"), "철골·접합")

    def test_annotate_singletons_counts_related_concept_occurrences(self):
        clusters = [{"stem": "조도", "members": [{"id": "2025-1회#1", "round": "2025-1회", "num": 1, "year": 2025}]}]
        all_items = [
            {"id": "2018-1회#2", "round": "2018-1회", "num": 2, "year": 2018, "stem": "조도의 정의"},
            {"id": "2021-1회#2", "round": "2021-1회", "num": 2, "year": 2021, "stem": "조도 단위"},
        ]
        out = annotate_singletons(clusters, all_items, {"2025-1회#1": {"topic": "조도"}})
        self.assertEqual(out[0]["related_years"], [2018, 2021])
        self.assertEqual(out[0]["related_count"], 2)
        self.assertGreater(out[0]["singleton_score"], 0)

    def test_2026_sungandang_is_excluded_from_frequency_input(self):
        self.assertEqual(stems_from_round({"source": "sungandang_pdf", "year": 2026, "id": "2026-1회"}), [])


if __name__ == "__main__":
    unittest.main()
