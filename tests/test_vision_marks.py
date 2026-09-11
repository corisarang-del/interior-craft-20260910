"""TDD: merge vision mark JSON into answer updates."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from vision_marks import merge_mark_items  # noqa: E402


class TestMerge(unittest.TestCase):
    def test_confirmed_and_inferred(self):
        items = [
            {"num": 1, "answer": "④", "status": "확정", "why": "check"},
            {"num": 2, "answer": "①", "status": "추론", "why": "solve"},
            {"num": 3, "answer": None, "status": "미확정", "why": "unread"},
            {"num": 4, "answer": "5", "status": "확정", "why": "bad"},
        ]
        out = merge_mark_items(items)
        self.assertEqual(out["1"]["status"], "확정")
        self.assertEqual(out["1"]["answer"], "④")
        self.assertEqual(out["2"]["status"], "추론")
        self.assertEqual(out["3"]["status"], "미확정")
        self.assertNotIn("4", out)

    def test_rejects_multi_status_confirmed(self):
        items = [{"num": 1, "answer": "①②", "status": "확정"}]
        out = merge_mark_items(items)
        self.assertNotIn("1", out)


if __name__ == "__main__":
    unittest.main()
