import os
import sys
import unittest
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from build_summary import (
    format_frequency_line,
    reorder_singleton_section,
    review_number_match,
    review_topic_key,
    write_singleton_priority_metadata,
)
from frequency import singleton_score_components


class TestSummaryReview(unittest.TestCase):
    def test_unrelated_topics_do_not_share_review_key(self):
        self.assertNotEqual(review_topic_key("암순응에 따른 시각 적응 현상"), review_topic_key("목재의 응력과 강도 변화"))
        self.assertNotEqual(review_topic_key("아일랜드 전시"), review_topic_key("VMD의 목적과 거리가 먼 항목"))

    def test_same_topic_wording_can_share_key(self):
        self.assertEqual(review_topic_key("석재의 강도와 내화성"), review_topic_key("석재의 내화성 비교"))
        self.assertEqual(review_topic_key("강구조 기둥의 좌굴 현상"), review_topic_key("강구조 기둥의 좌굴 발생 원리"))

    def test_mismatched_display_number_is_not_linkable(self):
        members = [{"round": "2024-1회", "num": 26}, {"round": "2024-1회", "num": 23}]
        review = {"2024-1회#26": {"displayed_number": 27}, "2024-1회#23": {"displayed_number": 23}}
        self.assertEqual(review_number_match(members, review), {("2024-1회", "23")})

    def test_singleton_score_fields_are_separate(self):
        score = singleton_score_components({"related_years": [2018, 2021], "related_count": 3, "core": 5, "numeric": 2, "utility": 2})
        self.assertEqual(score["related_year_count"], 2)
        self.assertEqual(score["singleton_score"], 23)

    def test_singleton_reorder_keeps_baseline_candidates(self):
        repeated = {"category": "반복 출제 핵심 유형", "members": [{"round": "2018-1회", "num": 1}], "frequency_score": 8, "latest_score": 0}
        single_a = {"category": "단독 출제 참고", "stable_key": "2025-1회#01", "members": [{"round": "2025-1회", "num": 1}], "related_years": [2024], "related_count": 1, "core": 5, "numeric": 2, "utility": 2}
        single_b = {"category": "단독 출제 참고", "stable_key": "2017-1회#01", "members": [{"round": "2017-1회", "num": 1}], "related_years": [], "related_count": 0, "core": 1, "numeric": 0, "utility": 0}
        out = reorder_singleton_section([single_a, repeated, single_b], ["2025-1회#1", "2017-1회#1"])
        self.assertEqual(out[0], repeated)
        self.assertEqual([x["stable_key"] for x in out[1:]], ["2025-1회#01", "2017-1회#01"])

    def test_priority_metadata_has_one_row_per_singleton(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            rows = write_singleton_priority_metadata([
                {"category": "반복 출제 핵심 유형", "members": [{"round": "2018-1회", "num": 1}]},
                {"category": "단독 출제 참고", "members": [{"round": "2017-1회", "num": 2}], "concept_key": "치수기입", "singleton_score": 8},
            ], output_path=str(Path(td) / "singleton_priority.json"))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["id"], "2017-1회#2")
            self.assertEqual(rows[0]["rank"], 1)

    def test_frequency_line_exposes_score_and_repeat_count(self):
        self.assertEqual(
            format_frequency_line({"score": 18.0, "frequency_score": 8, "latest_score": 1, "category": "반복 출제 핵심 유형", "members": [{"year": 2018}, {"year": 2021}, {"year": 2024}]}),
            "> **출제빈도**: 반복 출제 핵심 유형 / 3회 / 3개년 / 빈도점수 8 / 최신점수 1",
        )


if __name__ == "__main__":
    unittest.main()
