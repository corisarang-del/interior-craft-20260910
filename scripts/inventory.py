"""Inventory contract for interior-architecture craftsman written-exam recovery."""
import json
import os
import re

NUM_RANGE = (1, 60)
ANSWER_CAP = 60
TITLE_RANGE_RE = re.compile(r"\d{1,3}[~-]\d{1,3}")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_INVENTORY = os.path.join(ROOT, "metadata", "inventory.json")


def inventory_path():
    return DEFAULT_INVENTORY


def load_inventory(path=None):
    path = path or inventory_path()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "rounds" not in data or not isinstance(data["rounds"], list):
        raise ValueError("inventory missing rounds")
    return data


def digit_keys(question_map):
    return sorted([k for k in question_map if str(k).isdigit()], key=lambda x: int(x))


def validate_question_map(question_map):
    lo, hi = NUM_RANGE
    for k in digit_keys(question_map):
        n = int(k)
        if n < lo or n > hi:
            raise ValueError(f"question key {k} outside {NUM_RANGE}")
    return True


def validate_answers(answers):
    out = []
    for a in answers[:ANSWER_CAP]:
        if a is None or a == "":
            out.append(None)
        else:
            out.append(a)
    return out


def question_image_md(round_id, num):
    return f"![](이미지/{round_id}/q{int(num):02d}.jpg)"


def rounds_with_source(data):
    return [r for r in data["rounds"] if r.get("source") and r["source"] != "none"]
