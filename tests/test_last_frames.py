"""TDD: last frame per question is the mark still."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from last_frames import last_frames_from_rows  # noqa: E402


class TestLastFrames(unittest.TestCase):
    def test_picks_latest_ts_per_num(self):
        rows = [
            {"num": 1, "ts": 10, "file": "a.jpg", "vid": "v1", "frames_dir": "/f1"},
            {"num": 1, "ts": 20, "file": "b.jpg", "vid": "v1", "frames_dir": "/f1"},
            {"num": 2, "ts": 30, "file": "c.jpg", "vid": "v1", "frames_dir": "/f1"},
        ]
        last = last_frames_from_rows(rows)
        self.assertEqual(last[1]["file"], "b.jpg")
        self.assertEqual(last[2]["file"], "c.jpg")
        self.assertEqual(last[1]["path"], "/f1/b.jpg")

    def test_skips_null_num(self):
        rows = [{"num": None, "ts": 1, "file": "x.jpg", "frames_dir": "/f"}]
        self.assertEqual(last_frames_from_rows(rows), {})

    def test_window_ignores_later_false_num(self):
        rows = [
            {"num": 1, "ts": 10, "file": "a.jpg", "frames_dir": "/f"},
            {"num": 1, "ts": 20, "file": "b.jpg", "frames_dir": "/f"},
            {"num": 1, "ts": 700, "file": "wrong.jpg", "frames_dir": "/f"},
            {"num": 2, "ts": 80, "file": "c.jpg", "frames_dir": "/f"},
        ]
        last = last_frames_from_rows(rows, windows={1: (10, 80), 2: (80, 200)})
        self.assertEqual(last[1]["file"], "b.jpg")


if __name__ == "__main__":
    unittest.main()
