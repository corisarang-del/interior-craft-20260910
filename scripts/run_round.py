#!/usr/bin/env python3
"""Process one youtube round: assume work_<vid>/frames.json already exists."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from answers import extract_answers
from assign_questions import assign_questions, detect_first_starts, mark_duplicate_stems
from fill_gaps import read_left_number
from inventory import NUM_RANGE, digit_keys, load_inventory
from notes import image_md5_duplicates, render_round_note
from ocr_frames import group_frames, load_frames_json, ocr_frame, parse_num
from PIL import Image, ImageFilter
from vtt_text import vtt_to_text

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"


def upscale(src, dest, scale=4):
    im = Image.open(src)
    im = im.resize((im.width * scale, im.height * scale), Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=160, threshold=2))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, quality=90)


def process_video(vid, existing_rows=None):
    work = os.path.join(ROOT, "raw/youtube", f"work_{vid}")
    frames_dir = os.path.join(work, "frames")
    frames_json = os.path.join(work, "frames.json")
    ocr_json = os.path.join(ROOT, "raw/youtube/ocr", f"{vid}.json")
    frames = load_frames_json(frames_json)
    ts_map = {f["file"]: f.get("timestamp_sec", 0) for f in frames}
    os.makedirs(os.path.dirname(ocr_json), exist_ok=True)
    if existing_rows is not None:
        rows = existing_rows
    elif os.path.isfile(ocr_json):
        rows = json.load(open(ocr_json, encoding="utf-8"))
    else:
        rows = []
        for i, f in enumerate(frames, 1):
            row = ocr_frame(os.path.join(frames_dir, f["file"]), NUM_RANGE)
            row["ts"] = ts_map.get(f["file"], 0)
            rows.append(row)
            if i % 25 == 0:
                print(f"  ocr {vid} {i}/{len(frames)}")
        json.dump(rows, open(ocr_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in rows:
        r["num"] = parse_num(r.get("text") or "", NUM_RANGE)
        r.setdefault("ts", ts_map.get(r["file"], 0))
    return rows, frames_dir


def merge_rows(parts):
    offset = 0
    merged = []
    for rows in parts:
        for r in rows:
            x = dict(r)
            x["ts"] = r.get("ts", 0) + offset
            merged.append(x)
        if rows:
            offset = max(x["ts"] for x in merged) + 30
    return merged


def build_questions(rows, frames_dir):
    badges = [(r["ts"], r["num"]) for r in rows if r.get("num")]
    starts = detect_first_starts(badges, NUM_RANGE)
    have = {n for _, n in starts}
    missing = [i for i in range(1, 61) if i not in have]
    for n in missing:
        prevs = [(ts, pn) for ts, pn in starts if pn < n]
        nexts = [(ts, pn) for ts, pn in starts if pn > n]
        lo_ts = max(prevs)[0] if prevs else 0
        hi_ts = min(nexts)[0] if nexts else 10**9
        for r in rows:
            if not (lo_ts < r["ts"] < hi_ts) or r.get("num"):
                continue
            path = os.path.join(frames_dir, r["file"])
            if not os.path.isfile(path):
                continue
            got = read_left_number(path, NUM_RANGE)
            if got == n:
                r["num"] = n
                break
    badges = [(r["ts"], r["num"]) for r in rows if r.get("num")]
    starts = detect_first_starts(badges, NUM_RANGE)
    groups = group_frames(rows)
    for g in groups:
        g["file"] = g["members"][0]["file"]
        g["ts"] = g["members"][0].get("ts", 0)
    q = assign_questions(groups, starts, margin=90)
    return mark_duplicate_stems(q), starts


def write_round(round_id, questions, frames_dirs, answers, source="youtube"):
    keys = digit_keys(questions)
    for i, k in enumerate(keys):
        questions[k]["answer"] = answers[i] if i < len(answers) else None
    out_img = os.path.join(ROOT, "out/images", round_id)
    os.makedirs(out_img, exist_ok=True)
    copied = []
    for k in keys:
        src = None
        for d in frames_dirs:
            p = os.path.join(d, questions[k]["file"])
            if os.path.isfile(p):
                src = p
                break
        dest = os.path.join(out_img, f"q{int(k):02d}.jpg")
        if questions[k].get("image_confirmed") and src:
            upscale(src, dest)
            copied.append(dest)
        questions[k]["file"] = f"q{int(k):02d}.jpg"
    dups = image_md5_duplicates(copied) if copied else {}
    md = render_round_note(round_id, questions, source=source)
    out_note = os.path.join(ROOT, "out/notes", f"{round_id}.md")
    os.makedirs(os.path.dirname(out_note), exist_ok=True)
    open(out_note, "w", encoding="utf-8").write(md)
    vault_img = os.path.join(VAULT, "기출문제", "이미지", round_id)
    vault_note = os.path.join(VAULT, "기출문제", f"{round_id}.md")
    os.makedirs(vault_img, exist_ok=True)
    for p in copied:
        Image.open(p).save(os.path.join(vault_img, os.path.basename(p)), quality=90)
    open(vault_note, "w", encoding="utf-8").write(md)
    print(round_id, "q", len(keys), "img", len(copied), "dups", len(dups), "missing", [i for i in range(1, 61) if str(i) not in questions])
    return len(keys), len(dups)


def main(round_id):
    data = load_inventory()
    rnd = next(r for r in data["rounds"] if r["id"] == round_id)
    if rnd["source"] != "youtube":
        raise SystemExit(f"{round_id} source is {rnd['source']}")
    parts = []
    dirs = []
    vtts = []
    for vid in rnd["video_ids"]:
        rows, frames_dir = process_video(vid)
        parts.append(rows)
        dirs.append(frames_dir)
        vtt = os.path.join(ROOT, "raw/youtube/videos", f"{vid}.ko.vtt")
        if os.path.isfile(vtt):
            vtts.append(vtt)
    rows = merge_rows(parts) if len(parts) > 1 else parts[0]
    q, starts = build_questions(rows, dirs[0] if len(dirs) == 1 else dirs[0])
    answers = []
    for vtt in vtts:
        answers.extend(extract_answers(vtt_to_text(vtt)))
    write_round(round_id, q, dirs, answers)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: run_round.py 2024-1회")
    main(sys.argv[1])
