"""OCR napass-class restoration frames. Number is a large left token, not a bottom badge."""
import json
import os
import re
import subprocess
import tempfile
from difflib import SequenceMatcher

from PIL import Image, ImageFilter, ImageOps

NUM_RE = re.compile(r"^\s*0*([1-9]\d?)\b")
HEADER_HINTS = ("CBT", "기출", "복원", "202")
SOLUTION_RE = re.compile(r"solut", re.I)


def _tesseract(path, lang="kor+eng", psm=4):
    r = subprocess.run(
        ["tesseract", path, "stdout", "-l", lang, "--psm", str(psm)],
        capture_output=True,
        text=True,
    )
    return r.stdout or ""


def prepare_left_body(im, scale=3):
    w, h = im.size
    box = (int(w * 0.01), int(h * 0.14), int(w * 0.58), int(h * 0.98))
    c = im.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.Resampling.LANCZOS)
    g = ImageOps.grayscale(c)
    g = ImageOps.autocontrast(g)
    g = g.filter(ImageFilter.SHARPEN)
    return g


def parse_num(text, num_range=(1, 60)):
    if not text:
        return None
    t = text.replace("O", "0").replace("o", "0")
    head = t.lstrip()
    if re.match(r"^[1-4①-④][).]", head):
        return None
    if re.search(r"^\s*0*[1-9]\d?\s*\|", t):
        return None
    spaced = re.match(r"^\s*([1-6])\s+([0-9])\b", t)
    if spaced:
        n = int(spaced.group(1) + spaced.group(2))
        lo, hi = num_range
        if lo <= n <= hi:
            return n
    m = NUM_RE.search(t)
    if not m:
        m = re.search(r"(?m)^\s*([1-9]\d?)\s*$", t[:40])
    if not m:
        return None
    rest = t[m.end() : m.end() + 16].lstrip()
    if rest.startswith(")"):
        return None
    n_try = int(m.group(1))
    if rest.startswith(".") and n_try <= 4:
        return None
    n = int(m.group(1))
    lo, hi = num_range
    if lo <= n <= hi:
        return n
    return None





def ocr_frame(path, num_range=(1, 60)):
    im = Image.open(path)
    body = prepare_left_body(im)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp = f.name
        body.save(tmp)
    try:
        text = _tesseract(tmp, "kor+eng", 4)
    finally:
        os.unlink(tmp)
    num = parse_num(text, num_range)
    return {"file": os.path.basename(path), "text": text.strip(), "num": num}


def load_frames_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["frames"] if isinstance(data, dict) else data


def group_frames(ocr_rows, threshold=0.55):
    groups = []
    for row in ocr_rows:
        text = row.get("text") or ""
        placed = False
        for g in groups:
            if SequenceMatcher(None, text[:120], (g["text"] or "")[:120]).ratio() > threshold:
                g["members"].append(row)
                if len(text) > len(g["text"] or ""):
                    g["text"] = text
                if row.get("num") and not g.get("num"):
                    g["num"] = row["num"]
                placed = True
                break
        if not placed:
            groups.append(
                {
                    "text": text,
                    "num": row.get("num"),
                    "file": row["file"],
                    "ts": row.get("ts", 0),
                    "members": [row],
                }
            )
    return groups
