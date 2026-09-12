import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from build_summary import format_member_answers, format_member_links


class TestSummaryAnswers(unittest.TestCase):
    def test_formats_answer_and_inferred_status(self):
        members = [
            {"round": "2018-1회", "num": 50},
            {"round": "2024-1회", "num": 51},
        ]
        index = {
            ("2018-1회", "50"): {"answer": "③", "status": "확정"},
            ("2024-1회", "51"): {"answer": "④", "status": "추론"},
        }
        line = format_member_answers(members, index)
        self.assertEqual(
            line,
            "> **정답**: 2018-1회 50번 ③; 2024-1회 51번 ④ (추론)",
        )

    def test_links_are_scoped_to_interior_craft_vault(self):
        members = [{"round": "2018-1회", "num": 50}]
        links = format_member_links(members, {("2018-1회", "50")})
        self.assertEqual(
            links,
            ["[[지식/실내건축기능사/기출문제/2018-1회#50|2018-1회 50번]]"],
        )

    def test_keeps_unconfirmed_explicit(self):
        members = [{"round": "2026-1회", "num": 1}]
        index = {
            ("2026-1회", "1"): {"answer": None, "status": "미확정"},
        }
        self.assertEqual(
            format_member_answers(members, index),
            "> **정답**: 2026-1회 1번 미확정",
        )


if __name__ == "__main__":
    unittest.main()
