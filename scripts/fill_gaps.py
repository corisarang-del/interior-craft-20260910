"""Re-OCR number ROI for frames that sit in missing-number time gaps."""
import os
import re
import subprocess
import tempfile

from PIL import Image, ImageEnhance, ImageOps


def _ocr_digits(im):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
        im.save(path)
    try:
        r = subprocess.run(
            [
                "tesseract",
                path,
                "stdout",
                "-l",
                "eng",
                "--psm",
                "8",
                "-c",
                "tessedit_char_whitelist=0123456789",
            ],
            capture_output=True,
            text=True,
        )
        raw = re.sub(r"\D", "", r.stdout or "")
        return int(raw) if raw.isdigit() else None
    finally:
        os.unlink(path)


def read_left_number(path, num_range=(1, 60)):
    im = Image.open(path)
    w, h = im.size
    box = (int(w * 0.008), int(h * 0.13), int(w * 0.11), int(h * 0.31))
    c = im.crop(box)
    c = c.resize((400, 300), Image.Resampling.LANCZOS)
    g = ImageOps.grayscale(c)
    g = ImageOps.autocontrast(g)
    g = ImageEnhance.Contrast(g).enhance(2.5)
    n = _ocr_digits(g)
    if n is None:
        return None
    lo, hi = num_range
    if lo <= n <= hi:
        return n
    return None
