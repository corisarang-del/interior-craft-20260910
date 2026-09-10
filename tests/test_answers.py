"""TDD: conservative subtitle answer extraction."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from answers import ANSWER_CAP, extract_answers, normalize_choice  # noqa: E402


class TestNormalize(unittest.TestCase):
    def test_circled_and_digit(self):
        self.assertEqual(normalize_choice("3"), "③")
        self.assertEqual(normalize_choice("③"), "③")
        self.assertEqual(normalize_choice("4"), "④")


class TestExtract(unittest.TestCase):
    def test_clear_pattern_only(self):
        text = "정답은 2번이 됩니다. 다음 문제."
        self.assertEqual(extract_answers(text), ["②"])

    def test_ignores_bare_nbeoni(self):
        text = "1번이 틀리고 2번이 애매하고 3번이 비슷합니다."
        self.assertEqual(extract_answers(text), [])

    def test_neighbor_dedup_within_20_chars(self):
        text = "답이 1번 정답은 1번이 됩니다"
        self.assertEqual(extract_answers(text), ["①"])

    def test_cap_60(self):
        parts = [f"정답은 {i % 4 + 1}번이 됩니다." for i in range(80)]
        self.assertEqual(len(extract_answers(" ".join(parts))), ANSWER_CAP)


if __name__ == "__main__":
    unittest.main()
