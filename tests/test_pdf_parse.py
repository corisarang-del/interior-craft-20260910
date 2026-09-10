"""TDD: sungandang restoration PDF parsing. New-only PDFs must not invent missing numbers."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from pdf_parse import parse_restored_text  # noqa: E402


SAMPLE = """
1. 다음 중 디자인 원리와 거리가 먼 것은?
① 통일 ② 균형 ③ 리듬 ④ 콘크리트
정답 ④

5. 색의 3속성이 아닌 것은?
① 명도 ② 채도 ③ 색상 ④ 질감
정답: ④
"""


class TestPdfParse(unittest.TestCase):
    def test_extracts_only_present_numbers(self):
        qs = parse_restored_text(SAMPLE)
        self.assertEqual(sorted(qs), ["1", "5"])
        self.assertEqual(qs["1"]["answer"], "④")
        self.assertEqual(qs["5"]["answer"], "④")
        self.assertIn("디자인 원리", qs["1"]["text"])
        self.assertNotIn("2", qs)

    def test_does_not_fill_sixty(self):
        qs = parse_restored_text(SAMPLE)
        self.assertLess(len(qs), 60)

    def test_options_kept(self):
        qs = parse_restored_text(SAMPLE)
        self.assertIn("①", qs["1"]["text"])


if __name__ == "__main__":
    unittest.main()
