#!/usr/bin/env python3
"""Fill answers for every youtube round. Images untouched."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from collect_round_rows import load_round_rows
from fill_round_answers import fill_round
from inventory import load_inventory, rounds_with_source


def main():
    only = sys.argv[1:]
    data = load_inventory()
    rounds = [r["id"] for r in rounds_with_source(data) if r["source"] == "youtube"]
    if only:
        rounds = [r for r in rounds if r in only]
    for rid in rounds:
        print("====", rid)
        fill_round(rid)


if __name__ == "__main__":
    main()
