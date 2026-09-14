import os
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from make_summary_images import output_names, enhance_image


class TestSummaryImages(unittest.TestCase):
    def test_output_names_are_stable(self):
        self.assertEqual(
            output_names("2024-3회", 34),
            ("2024-3회-q34-problem.jpg", "2024-3회-q34-full.jpg"),
        )

    def test_enhanced_outputs_are_larger_and_readable(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.jpg"
            Image.new("RGB", (640, 360), "white").save(src)
            problem = Path(td) / "problem.jpg"
            full = Path(td) / "full.jpg"
            enhance_image(src, problem, full)
            self.assertGreater(Image.open(problem).width, 500)
            self.assertGreater(Image.open(full).width, 900)
            self.assertEqual(Image.open(problem).format, "JPEG")
            self.assertEqual(Image.open(full).format, "JPEG")


if __name__ == "__main__":
    unittest.main()
