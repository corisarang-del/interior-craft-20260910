import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from build_summary import review_topic_key, review_number_match, format_frequency_line


class TestSummaryReview(unittest.TestCase):
    def test_unrelated_topics_do_not_share_review_key(self):
        self.assertNotEqual(review_topic_key("암순응에 따른 시각 적응 현상"), review_topic_key("목재의 응력과 강도 변화"))
        self.assertNotEqual(review_topic_key("아일랜드 전시"), review_topic_key("VMD의 목적과 거리가 먼 항목"))

    def test_same_topic_wording_can_share_key(self):
        self.assertEqual(review_topic_key("석재의 강도와 내화성"), review_topic_key("석재의 내화성 비교"))
        self.assertEqual(review_topic_key("강구조 기둥의 좌굴 현상"), review_topic_key("강구조 기둥의 좌굴 발생 원리"))

    def test_mismatched_display_number_is_not_linkable(self):
        members = [{"round": "2024-1회", "num": 26}, {"round": "2024-1회", "num": 23}]
        review = {
            "2024-1회#26": {"displayed_number": 27},
            "2024-1회#23": {"displayed_number": 23},
        }
        self.assertEqual(review_number_match(members, review), {("2024-1회", "23")})

    def test_frequency_line_exposes_score_and_repeat_count(self):
        self.assertEqual(
            format_frequency_line({"score": 18.0, "members": [{"year": 2018}, {"year": 2021}, {"year": 2024}]}),
            "> **출제빈도**: 3회 / 3개년 / 점수 18",
        )


if __name__ == "__main__":
    unittest.main()
