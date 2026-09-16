import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from build_2026_predictions import clean_clue, topic_tokens, infer_question_form


class Test2026Predictions(unittest.TestCase):
    def test_clean_clue_removes_book_location(self):
        text = "- 디자인의 원리(황금비례) (교재 47쪽, 115번)"
        self.assertEqual(clean_clue(text), "디자인의 원리 황금비례")

    def test_topic_tokens_keep_meaningful_words(self):
        tokens = topic_tokens("실내 기본 요소(천장)")
        self.assertIn("천장", tokens)
        self.assertIn("실내", tokens)

    def test_question_form_for_topic(self):
        form = infer_question_form("강화유리")
        self.assertIn("특성", form)


if __name__ == "__main__":
    unittest.main()
