#!/usr/bin/env python3
"""Load OCR rows for a youtube round and attach frames_dir/vid."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from inventory import load_inventory
from ocr_frames import parse_num
from last_frames import last_frames_from_rows

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_round_rows(round_id):
    data = load_inventory()
    rnd = next(r for r in data["rounds"] if r["id"] == round_id)
    if rnd["source"] != "youtube":
        return [], rnd
    parts = []
    offset = 0
    for vid in rnd["video_ids"]:
        ocr = os.path.join(ROOT, "raw/youtube/ocr", f"{vid}.json")
        frames_dir = os.path.join(ROOT, "raw/youtube", f"work_{vid}", "frames")
        if not os.path.isfile(ocr):
            continue
        rows = json.load(open(ocr, encoding="utf-8"))
        chunk = []
        for r in rows:
            x = dict(r)
            x["num"] = parse_num(x.get("text") or "")
            x["ts"] = (x.get("ts") or 0) + offset
            x["vid"] = vid
            x["frames_dir"] = frames_dir
            x["src_file"] = x.get("file")
            chunk.append(x)
        if chunk:
            offset = max(c["ts"] for c in chunk) + 30
        parts.extend(chunk)
    return parts, rnd


def main(round_id):
    rows, rnd = load_round_rows(round_id)
    last = last_frames_from_rows(rows)
    print(round_id, "rows", len(rows), "qs", len(last), "missing", [i for i in range(1, 61) if i not in last])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: collect_round_rows.py 2025-1회")
    main(sys.argv[1])
