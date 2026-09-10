#!/usr/bin/env python3
"""Apply image-confirmed answers to a round note. Optional frame swap for marked stills."""
import json
import os
import sys

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from answers_status import apply_answers_to_note

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"


def upscale(src, dest, scale=4):
    im = Image.open(src)
    im = im.resize((im.width * scale, im.height * scale), Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=160, threshold=2))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, quality=90)


def main(json_path):
    data = json.load(open(json_path, encoding="utf-8"))
    rid = data["round"]
    vid = data.get("video_id")
    frames_dir = os.path.join(ROOT, "raw/youtube", f"work_{vid}", "frames") if vid else None
    note_paths = [
        os.path.join(VAULT, "기출문제", f"{rid}.md"),
        os.path.join(ROOT, "out/notes", f"{rid}.md"),
    ]
    updates = {}
    for num, row in data["answers"].items():
        updates[str(num)] = {
            "answer": row.get("answer"),
            "status": row.get("status") or "미확정",
            "source": row.get("source"),
        }
        frame = row.get("frame")
        if frames_dir and frame and row.get("status") == "확정":
            src = os.path.join(frames_dir, frame)
            if os.path.isfile(src):
                dest_name = f"q{int(num):02d}.jpg"
                upscale(src, os.path.join(ROOT, "out/images", rid, dest_name))
                vault_img = os.path.join(VAULT, "기출문제", "이미지", rid, dest_name)
                os.makedirs(os.path.dirname(vault_img), exist_ok=True)
                Image.open(os.path.join(ROOT, "out/images", rid, dest_name)).save(vault_img, quality=90)
                print("image", dest_name, "<-", frame)
    for path in note_paths:
        if not os.path.isfile(path):
            print("missing note", path)
            continue
        text = open(path, encoding="utf-8").read()
        out = apply_answers_to_note(text, updates)
        open(path, "w", encoding="utf-8").write(out)
        print("updated", path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: apply_image_answers.py metadata/poc_....json")
    main(sys.argv[1])
