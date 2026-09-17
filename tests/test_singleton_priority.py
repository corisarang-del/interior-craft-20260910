import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from frequency import annotate_singletons, extract_concept_key, rank_singletons


class TestSingletonPriority(unittest.TestCase):
    def test_specific_concept_keys_are_not_broad_subjects(self):
        self.assertEqual(extract_concept_key("조도", "조도의 정의"), "조도")
        self.assertEqual(extract_concept_key("스티프너", "웨브 국부좌굴 방지"), "철골·접합")
        self.assertEqual(extract_concept_key("", "실내디자인 일반 설명"), "기타")

    def test_question_text_uses_concrete_topic(self):
        self.assertEqual(extract_concept_key("", "탄소량에 따른 강의 특성에 관한 설명"), "강재·열처리")
        self.assertEqual(extract_concept_key("", "부엌의 기능적인 수납을 위해 기본적으로 네 가지 원칙"), "수납")
        self.assertEqual(extract_concept_key("", "함수율에 따른 목재의 강도 설명"), "목재·강도")
        self.assertEqual(extract_concept_key("", "휘도의 단위로 사용되는 것은"), "휘도")
        self.assertEqual(extract_concept_key("", "콘크리트의 일반적인 성질에 관한 설명"), "기타")

    def test_generic_words_do_not_match_every_question(self):
        self.assertEqual(extract_concept_key("", "실내디자인 일반 설명"), "기타")
        self.assertEqual(extract_concept_key("", "철근 기둥의 구조 설명"), "건축구조·철근")

    def test_related_count_is_unique_question_count(self):
        clusters = [{"members": [{"id": "2025-1회#1", "round": "2025-1회", "num": 1, "year": 2025}], "stem": "조도"}]
        items = [
            {"id": "2018-1회#1", "round": "2018-1회", "num": 1, "year": 2018, "stem": "조도의 정의"},
            {"id": "2021-1회#1", "round": "2021-1회", "num": 1, "year": 2021, "stem": "조도 단위"},
            {"id": "2021-1회#2", "round": "2021-1회", "num": 2, "year": 2021, "stem": "휘도의 단위"},
        ]
        out = annotate_singletons(clusters, items, {"2025-1회#1": {"topic": "조도"}})[0]
        self.assertEqual(out["concept_key"], "조도")
        self.assertEqual(out["related_count"], 2)
        self.assertEqual(out["related_years"], [2018, 2021])

    def test_unknown_concept_does_not_inherit_all_other_questions(self):
        clusters = [{"members": [{"id": "2025-1회#1", "round": "2025-1회", "num": 1, "year": 2025}], "stem": "알 수 없는 세부 용어"}]
        items = [{"id": "2018-1회#1", "round": "2018-1회", "num": 1, "year": 2018, "stem": "전혀 다른 구조 설명"}]
        out = annotate_singletons(clusters, items, {})[0]
        self.assertEqual(out["concept_key"], "기타")
        self.assertEqual(out["related_count"], 0)
        self.assertEqual(out["related_years"], [])

    def test_priority_order_uses_score_before_id(self):
        low = {"stable_key": "2017-1회#01", "related_years": [], "related_count": 0, "core": 1, "numeric": 0, "utility": 0}
        high = {"stable_key": "2025-1회#01", "related_years": [2018, 2021], "related_count": 2, "core": 5, "numeric": 2, "utility": 2}
        ranked = rank_singletons([low, high])
        self.assertEqual(ranked[0]["stable_key"], "2025-1회#01")


if __name__ == "__main__":
    unittest.main()
