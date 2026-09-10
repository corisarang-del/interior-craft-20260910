"""TDD: question assignment for 1-60 craftsman exams."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from assign_questions import (  # noqa: E402
    assign_questions,
    detect_first_starts,
    detect_starts,
    mark_duplicate_stems,
)


class TestDetectStarts(unittest.TestCase):
    def test_filters_out_of_range_badges(self):
        badges = [(10, 83), (20, 1), (40, 2), (90, 85)]
        starts = detect_starts(badges, num_range=(1, 60))
        self.assertEqual([n for _, n in starts], [1, 2])

    def test_monotonic_forward(self):
        badges = [(5, 3), (10, 1), (20, 2), (30, 2), (40, 4)]
        starts = detect_starts(badges, num_range=(1, 60))
        self.assertEqual([n for _, n in starts], [1, 2, 4])

    def test_reverse_path_when_requested(self):
        badges = [(10, 3), (20, 2), (40, 1)]
        starts = detect_starts(badges, num_range=(1, 60), reverse=True)
        self.assertEqual([n for _, n in starts], [3, 2, 1])

    def test_first_starts_drops_far_outlier(self):
        badges = [(10, 1), (20, 2), (30, 3), (40, 4), (800, 23), (50, 5)]
        starts = detect_first_starts(badges)
        self.assertEqual([n for _, n in starts], [1, 2, 3, 4, 5])

    def test_keeps_swapped_neighbor_inside_window(self):
        badges = [
            (10, 1), (20, 2), (30, 4), (35, 3), (50, 5),
        ]
        starts = detect_starts(badges, num_range=(1, 60))
        self.assertEqual(sorted(n for _, n in starts), [1, 2, 3, 4, 5])
        late = [(10, 1), (20, 2), (30, 4), (500, 3), (50, 5)]
        starts2 = detect_starts(late, num_range=(1, 60))
        self.assertNotIn(3, [n for _, n in starts2])


class TestAssign(unittest.TestCase):
    def test_prefers_direct_badge_frame(self):
        groups = [
            {"ts": 12, "text": "디자인 요소", "file": "a.jpg"},
            {"ts": 50, "text": "다른 문제", "file": "b.jpg"},
        ]
        starts = [(10, 1), (45, 2)]
        q = assign_questions(groups, starts, margin=90)
        self.assertEqual(q["1"]["file"], "a.jpg")
        self.assertEqual(q["2"]["file"], "b.jpg")
        self.assertTrue(q["1"]["image_confirmed"])

    def test_keys_are_actual_numbers(self):
        groups = [{"ts": 5, "text": "x", "file": "q.jpg"}]
        starts = [(5, 12)]
        q = assign_questions(groups, starts, margin=90)
        self.assertIn("12", q)
        self.assertNotIn("1", q)


class TestDuplicateStems(unittest.TestCase):
    def test_same_stem_only_first_confirmed(self):
        q = {
            "1": {"text": "같은지문", "file": "a.jpg", "image_confirmed": True, "ts": 1},
            "2": {"text": "같은지문", "file": "a.jpg", "image_confirmed": True, "ts": 2},
        }
        out = mark_duplicate_stems(q)
        self.assertTrue(out["1"]["image_confirmed"])
        self.assertFalse(out["2"]["image_confirmed"])


if __name__ == "__main__":
    unittest.main()
