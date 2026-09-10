"""TDD: left-number parse for napass restoration slides."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from ocr_frames import parse_num  # noqa: E402


class TestParseNum(unittest.TestCase):
    def test_leading_two_digit(self):
        self.assertEqual(parse_num("05\n주택계획에 관한"), 5)
        self.assertEqual(parse_num("24 건축물의 투시도법"), 24)
        self.assertEqual(parse_num("01 천창 채광"), 1)

    def test_rejects_out_of_range(self):
        self.assertIsNone(parse_num("83 과대번호"))
        self.assertIsNone(parse_num("00"))

    def test_leading_number_with_solution_is_question(self):
        self.assertEqual(parse_num("04 Soluti 점토제품"), 4)
        self.assertEqual(parse_num("21 [Solution 음의 세기"), 21)
        self.assertEqual(parse_num("60 [Soluton 물체에 외력"), 60)
        self.assertEqual(parse_num("1 7 Soluti 연립주택"), 17)
        self.assertEqual(parse_num("3 3 Solutic 기초형식"), 33)
        self.assertEqual(parse_num("3 9 Solution 일반적으로 목재"), 39)
        self.assertEqual(parse_num("45 .5014400 블라인드"), 45)

    def test_rejects_solution_panel_and_option_marker(self):
        self.assertIsNone(parse_num("42 | Solutic 위치에 관한"))
        self.assertIsNone(parse_num("1) 천장이 높은 방"))
        self.assertIsNone(parse_num("1) 천장이"))

    def test_empty(self):
        self.assertIsNone(parse_num(""))
        self.assertIsNone(parse_num(None))


if __name__ == "__main__":
    unittest.main()
