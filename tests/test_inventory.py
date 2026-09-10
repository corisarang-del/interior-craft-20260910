"""TDD: inventory keys, 1-60 numbering, markdown image paths, no invented answers."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from inventory import (  # noqa: E402
    ANSWER_CAP,
    NUM_RANGE,
    TITLE_RANGE_RE,
    digit_keys,
    inventory_path,
    load_inventory,
    question_image_md,
    rounds_with_source,
    validate_answers,
    validate_question_map,
)

INVENTORY = os.path.join(ROOT, "metadata", "inventory.json")


class TestNumbering(unittest.TestCase):
    def test_num_range_is_1_to_60(self):
        self.assertEqual(NUM_RANGE, (1, 60))

    def test_answer_cap_is_60(self):
        self.assertEqual(ANSWER_CAP, 60)

    def test_digit_keys_sorted_numeric_not_q_get_1_loop(self):
        q = {"10": {}, "2": {}, "1": {}, "60": {}, "note": {}}
        self.assertEqual(digit_keys(q), ["1", "2", "10", "60"])

    def test_title_range_regex_keeps_three_digit_end(self):
        m = TITLE_RANGE_RE.search("81~100")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(0), "81~100")
        m2 = TITLE_RANGE_RE.search("1-60")
        self.assertIsNotNone(m2)
        self.assertEqual(m2.group(0), "1-60")
        self.assertNotEqual(TITLE_RANGE_RE.search("81~100").group(0), "81-10")


class TestQuestionMap(unittest.TestCase):
    def test_rejects_key_outside_range(self):
        with self.assertRaises(ValueError):
            validate_question_map({"61": {"ts": 1}})

    def test_accepts_1_and_60(self):
        validate_question_map({"1": {"ts": 0}, "60": {"ts": 1}})

    def test_answers_cap(self):
        answers = list(range(1, 80))
        self.assertEqual(len(validate_answers(answers)), 60)

    def test_blank_answer_stays_unconfirmed(self):
        self.assertEqual(validate_answers([None, "", "③"]), [None, None, "③"])


class TestImageMarkdown(unittest.TestCase):
    def test_relative_markdown_not_wiki(self):
        md = question_image_md("2025-1회", 1)
        self.assertEqual(md, "![](이미지/2025-1회/q01.jpg)")
        self.assertNotIn("![[", md)


class TestInventoryFile(unittest.TestCase):
    def test_inventory_exists_and_loads(self):
        self.assertTrue(os.path.isfile(INVENTORY))
        data = load_inventory(inventory_path())
        self.assertGreaterEqual(len(data["rounds"]), 15)

    def test_youtube_rounds_have_video_ids(self):
        data = load_inventory(inventory_path())
        yt = [r for r in data["rounds"] if r["source"] == "youtube"]
        self.assertTrue(yt)
        for r in yt:
            self.assertTrue(r["video_ids"], r["id"])
            self.assertTrue(1 <= r["expected_n"] <= 60)

    def test_sungandang_three_pdfs(self):
        data = load_inventory(inventory_path())
        pdfs = [r for r in data["rounds"] if r["source"] == "sungandang_pdf"]
        self.assertEqual([r["id"] for r in pdfs], ["2026-1회", "2026-2회", "2026-3회"])
        for r in pdfs:
            self.assertTrue(r["pdf_url"])
            self.assertEqual(r["restore_scope"], "new_only")

    def test_source_none_not_generated(self):
        data = load_inventory(inventory_path())
        none = [r for r in data["rounds"] if r["source"] == "none"]
        for r in none:
            self.assertEqual(r["video_ids"], [])
            self.assertIsNone(r["pdf_url"])
        ids = {r["id"] for r in rounds_with_source(data)}
        self.assertNotIn("2025-2회", ids)
        self.assertIn("2025-1회", ids)
        self.assertIn("2026-1회", ids)


class TestNoInventedAnswers(unittest.TestCase):
    def test_unconfirmed_marker(self):
        self.assertEqual(validate_answers([None])[0], None)


if __name__ == "__main__":
    unittest.main()
