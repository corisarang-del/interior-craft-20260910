"""TDD: obsidian note rendering."""
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from notes import image_md5_duplicates, render_round_note  # noqa: E402


class TestRender(unittest.TestCase):
    def test_relative_image_and_unconfirmed_answer(self):
        q = {
            "1": {"file": "q01.jpg", "image_confirmed": True, "answer": "③"},
            "2": {"file": "q02.jpg", "image_confirmed": False, "answer": None},
        }
        md = render_round_note("2025-1회", q, source="youtube")
        self.assertIn("![](이미지/2025-1회/q01.jpg)", md)
        self.assertNotIn("![[", md)
        self.assertIn("**정답: ③**", md)
        self.assertIn("**정답: 미확정**", md)
        self.assertNotIn("OCR", md)

    def test_skips_missing_source_round(self):
        md = render_round_note("2025-2회", {}, source="none")
        self.assertIsNone(md)


class TestMd5(unittest.TestCase):
    def test_detects_duplicate_files(self):
        with tempfile.TemporaryDirectory() as d:
            a = os.path.join(d, "q01.jpg")
            b = os.path.join(d, "q02.jpg")
            c = os.path.join(d, "q03.jpg")
            with open(a, "wb") as f:
                f.write(b"same")
            with open(b, "wb") as f:
                f.write(b"same")
            with open(c, "wb") as f:
                f.write(b"other")
            dups = image_md5_duplicates([a, b, c])
            self.assertEqual(len(dups), 1)
            self.assertEqual(len(next(iter(dups.values()))), 2)


if __name__ == "__main__":
    unittest.main()
