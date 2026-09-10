#!/usr/bin/env python3
"""Run crv on downloaded videos that lack frames.json."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from inventory import load_inventory, rounds_with_source

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VID = os.path.join(ROOT, "raw/youtube/videos")
YT = os.path.join(ROOT, "raw/youtube")


def extract(vid):
    work = os.path.join(YT, f"work_{vid}")
    frames_json = os.path.join(work, "frames.json")
    src = os.path.join(VID, f"{vid}.mp4")
    if os.path.isfile(frames_json):
        print("skip crv", vid)
        return
    if not os.path.isfile(src):
        print("missing video", vid)
        return
    os.makedirs(work, exist_ok=True)
    cmd = [
        "crv",
        "--scene",
        "0.30",
        "--fps-floor",
        "2.0",
        "--max-frames",
        "150",
        "--no-transcribe",
        "--overwrite",
        "-o",
        work,
        src,
    ]
    print("crv", vid)
    subprocess.check_call(cmd)


def main(only=None):
    data = load_inventory()
    for r in rounds_with_source(data):
        if r["source"] != "youtube":
            continue
        if only and r["id"] != only:
            continue
        for vid in r["video_ids"]:
            extract(vid)


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    main(only)
