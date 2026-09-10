"""TDD: sungandang catalog PDF = book map + new-only full questions."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from pdf_parse import parse_catalog_text  # noqa: E402

SAMPLE = """
  2026년 1월 21일 시행 제1회 실내건축기능사 필기
문항번호
       쪽수       번호               내용
  1     33        29             선의 종류
  2     37        56            장방형 형태
 58                                    열전도율
 59        신규 출제 문제                1소점 투시도(그림)
 60                                  구조체면 표기법

[신규 출제 문제]

58. 열전도율이 큰 것부터 순서로 나열된 것은?
① B－D－A－C
② B－D－C－A
③ D－B－A－C
④ D－B－C－A

59. 건축물을 표현하는 투시도법 중 그림과 같은 투시도법은 어느 것인
가?
① 평행 투시도
② 유각 투시도
③ 경사 투시도
④ 3소점 투시도
\x0c60. 도면에 있어서 구조체면의 표기 방법으로 옳은 것은?
①▼
②▲
"""


class TestCatalog(unittest.TestCase):
    def test_map_has_sixty_or_present_rows(self):
        data = parse_catalog_text(SAMPLE)
        self.assertEqual(data["map"]["1"]["topic"], "선의 종류")
        self.assertEqual(data["map"]["1"]["page"], "33")
        self.assertEqual(data["map"]["1"]["book_num"], "29")
        self.assertTrue(data["map"]["59"]["is_new"])

    def test_new_questions_keep_options(self):
        data = parse_catalog_text(SAMPLE)
        self.assertIn("58", data["new"])
        self.assertIn("60", data["new"])
        self.assertIn("열전도율", data["new"]["58"]["text"])
        self.assertIn("①", data["new"]["58"]["text"])
        self.assertIn("구조체면", data["new"]["60"]["text"])
        self.assertIsNone(data["new"]["58"]["answer"])

    def test_does_not_invent_answers(self):
        data = parse_catalog_text(SAMPLE)
        for q in data["new"].values():
            self.assertIsNone(q["answer"])


if __name__ == "__main__":
    unittest.main()
