import os
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from make_question_images import enhance_question_image


class TestQuestionImages(unittest.TestCase):
    def test_upscales_and_sharpens_full_frame(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "q01.jpg"
            dst = Path(td) / "out.jpg"
            Image.new("RGB", (640, 360), "white").save(src)
            enhance_question_image(src, dst, scale=1.5)
            with Image.open(dst) as im:
                self.assertEqual(im.size, (960, 540))
                self.assertEqual(im.format, "JPEG")


if __name__ == "__main__":
    unittest.main()
