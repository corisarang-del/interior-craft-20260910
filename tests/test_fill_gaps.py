"""TDD: left-number ROI reader on a real 16-frame if present."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from fill_gaps import read_left_number  # noqa: E402

FRAME = os.path.join(ROOT, "raw/youtube/work_8VUPu_RSkXE/frames/frame_055.jpg")


class TestFillGaps(unittest.TestCase):
    @unittest.skipUnless(os.path.isfile(FRAME), "poc frames missing")
    def test_frame_055_is_16(self):
        self.assertEqual(read_left_number(FRAME), 16)


if __name__ == "__main__":
    unittest.main()
