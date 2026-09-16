import json
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
META = ROOT / "metadata"
VAULT = Path("/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사")


class Test2026PredictionNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = json.loads((META / "2026_prediction_cards.json").read_text())

    def test_has_180_cards_and_three_rounds(self):
        self.assertEqual(len(self.cards), 180)
        self.assertEqual({x["round"] for x in self.cards}, {"2026-1회", "2026-2회", "2026-3회"})
        self.assertEqual(len({(x["round"], x["number"]) for x in self.cards}), 180)

    def test_prediction_never_claims_confirmed(self):
        self.assertTrue(all(x["prediction_status"].startswith("예측") for x in self.cards))
        self.assertTrue(all(x.get("candidate_answer") is None or "후보" in x["candidate_answer"] for x in self.cards))

    def test_notes_have_all_question_cards(self):
        for rid in ("2026-1회", "2026-2회", "2026-3회"):
            p = VAULT / "2026-예상복원" / f"{rid}-예상복원.md"
            text = p.read_text()
            nums = {int(x) for x in re.findall(r"^## (\d+)\.", text, re.M)}
            self.assertEqual(nums, set(range(1, 61)))
            self.assertNotIn("정답: 확정", text)

    def test_existing_notes_are_not_replaced_by_prediction_notes(self):
        for rid in ("2026-1회", "2026-2회", "2026-3회"):
            original = VAULT / "기출문제" / f"{rid}.md"
            self.assertTrue(original.exists())
            self.assertNotIn("# 예상복원 카드", original.read_text())


if __name__ == "__main__":
    unittest.main()
