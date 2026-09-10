#!/usr/bin/env python3
"""Download youtube videos+subs listed in inventory."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from inventory import load_inventory, rounds_with_source

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "raw/youtube/videos")


def main(only=None):
    os.makedirs(OUT, exist_ok=True)
    data = load_inventory()
    ids = []
    for r in rounds_with_source(data):
        if r["source"] != "youtube":
            continue
        if only and r["id"] != only:
            continue
        ids.extend(r["video_ids"])
    for vid in ids:
        dest = os.path.join(OUT, f"{vid}.mp4")
        if os.path.isfile(dest) and os.path.getsize(dest) > 10000:
            print("skip", vid)
            continue
        url = f"https://www.youtube.com/watch?v={vid}"
        cmd = [
            "yt-dlp",
            "--impersonate",
            "chrome",
            "--extractor-args",
            "youtube:player_client=android",
            "-f",
            "18/b[height<=360]/b",
            "--merge-output-format",
            "mp4",
            "--write-auto-subs",
            "--sub-langs",
            "ko",
            "--sub-format",
            "vtt",
            "-o",
            os.path.join(OUT, f"{vid}.%(ext)s"),
            url,
        ]
        print("dl", vid)
        subprocess.check_call(cmd)


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    main(only)
