"""TDD: answer status 미확정/추론/확정. No invented answers. No subtitle zip."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from answers_status import (  # noqa: E402
    CONFIRMED,
    UNCONFIRMED,
    INFERRED,
    apply_answers_to_note,
    format_answer_line,
    parse_answers_from_note,
    reset_untrusted_answers,
    validate_mark,
)


NOTE = """---
회차: 2025-1회
---
### 1.

![](이미지/2025-1회/q01.jpg)

**정답: ①**

### 2.

![](이미지/2025-1회/q02.jpg)

**정답: 미확정**

### 5.

**정답: ③ (추론)**
"""


class TestFormat(unittest.TestCase):
    def test_unconfirmed(self):
        self.assertEqual(format_answer_line(None, UNCONFIRMED), "**정답: 미확정**")

    def test_confirmed(self):
        self.assertEqual(format_answer_line("③", CONFIRMED), "**정답: ③**")

    def test_inferred(self):
        self.assertEqual(format_answer_line("②", INFERRED), "**정답: ② (추론)**")

    def test_confirmed_requires_choice(self):
        with self.assertRaises(ValueError):
            format_answer_line(None, CONFIRMED)


class TestValidateMark(unittest.TestCase):
    def test_only_circled_1_to_4(self):
        self.assertEqual(validate_mark("③"), "③")
        self.assertEqual(validate_mark("3"), "③")
        self.assertIsNone(validate_mark("5"))
        self.assertIsNone(validate_mark(""))
        self.assertIsNone(validate_mark("미확정"))


class TestParseAndApply(unittest.TestCase):
    def test_parse_status(self):
        parsed = parse_answers_from_note(NOTE)
        self.assertEqual(parsed["1"]["answer"], "①")
        self.assertEqual(parsed["1"]["status"], CONFIRMED)
        self.assertEqual(parsed["2"]["status"], UNCONFIRMED)
        self.assertEqual(parsed["5"]["status"], INFERRED)
        self.assertEqual(parsed["5"]["answer"], "③")

    def test_apply_only_listed_questions(self):
        out = apply_answers_to_note(
            NOTE,
            {"2": {"answer": "④", "status": CONFIRMED, "source": "image"}},
        )
        parsed = parse_answers_from_note(out)
        self.assertEqual(parsed["2"]["answer"], "④")
        self.assertEqual(parsed["2"]["status"], CONFIRMED)
        self.assertEqual(parsed["1"]["answer"], "①")

    def test_reset_untrusted_clears_answers_without_image_source(self):
        out = reset_untrusted_answers(NOTE)
        parsed = parse_answers_from_note(out)
        self.assertEqual(parsed["1"]["status"], UNCONFIRMED)
        self.assertEqual(parsed["2"]["status"], UNCONFIRMED)
        self.assertEqual(parsed["5"]["status"], UNCONFIRMED)

    def test_does_not_invent_missing_numbers(self):
        out = apply_answers_to_note(NOTE, {"99": {"answer": "①", "status": CONFIRMED}})
        self.assertNotIn("### 99.", out)


if __name__ == "__main__":
    unittest.main()
