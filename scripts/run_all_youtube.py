#!/usr/bin/env python3
"""Extract frames then build notes for every youtube round."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from inventory import load_inventory, rounds_with_source

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main():
    data = load_inventory()
    rounds = [r["id"] for r in rounds_with_source(data) if r["source"] == "youtube"]
    for rid in rounds:
        print("==== extract", rid)
        subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/extract_frames.py"), rid])
        print("==== note", rid)
        subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/run_round.py"), rid])


if __name__ == "__main__":
    main()
