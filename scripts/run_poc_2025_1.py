#!/usr/bin/env python3
"""PoC: 2025-1회 나합격 1영상 → OCR → 배정 → 업스케일 → 노트."""
import json
import os
import sys

from PIL import Image, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from answers import extract_answers  # noqa: E402
from assign_questions import assign_questions, detect_first_starts, mark_duplicate_stems
from fill_gaps import read_left_number
from inventory import NUM_RANGE, digit_keys
from notes import image_md5_duplicates, render_round_note
from ocr_frames import group_frames, load_frames_json, ocr_frame
from vtt_text import vtt_to_text

WORK = os.path.join(ROOT, "raw/youtube/work_8VUPu_RSkXE")
FRAMES = os.path.join(WORK, "frames")
FRAMES_JSON = os.path.join(WORK, "frames.json")
OCR_JSON = os.path.join(ROOT, "raw/youtube/ocr/8VUPu_RSkXE.json")
VTT = os.path.join(ROOT, "raw/youtube/videos/8VUPu_RSkXE.ko.vtt")
OUT_IMG = os.path.join(ROOT, "out/images/2025-1회")
OUT_NOTE = os.path.join(ROOT, "out/notes/2025-1회.md")
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"


def upscale(src, dest, scale=4):
    im = Image.open(src)
    im = im.resize((im.width * scale, im.height * scale), Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=160, threshold=2))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, quality=90)


def main():
    frames = load_frames_json(FRAMES_JSON)
    ts_map = {f["file"]: f.get("timestamp_sec", 0) for f in frames}
    os.makedirs(os.path.dirname(OCR_JSON), exist_ok=True)
    if os.path.isfile(OCR_JSON):
        rows = json.load(open(OCR_JSON, encoding="utf-8"))
        print("loaded ocr", len(rows))
    else:
        rows = []
        for i, f in enumerate(frames, 1):
            path = os.path.join(FRAMES, f["file"])
            row = ocr_frame(path, NUM_RANGE)
            row["ts"] = ts_map.get(f["file"], 0)
            rows.append(row)
            if i % 10 == 0 or i == 1:
                print(f"ocr {i}/{len(frames)} num={row.get('num')} file={f['file']}")
        json.dump(rows, open(OCR_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("wrote", OCR_JSON)

    from ocr_frames import parse_num as parse_num_now

    for r in rows:
        r["num"] = parse_num_now(r.get("text") or "", NUM_RANGE)
    json.dump(rows, open(OCR_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    badges = [(r["ts"], r["num"]) for r in rows if r.get("num")]
    uniq = sorted({n for _, n in badges})
    print("badge hits", len(badges), "unique", uniq, "count", len(uniq))
    starts = detect_first_starts(badges, NUM_RANGE)
    have = {n for _, n in starts}
    missing = [i for i in range(1, 61) if i not in have]
    filled = []
    for n in missing:
        prevs = [(ts, pn) for ts, pn in starts if pn < n]
        nexts = [(ts, pn) for ts, pn in starts if pn > n]
        lo_ts = max(prevs)[0] if prevs else 0
        hi_ts = min(nexts)[0] if nexts else 10**9
        for r in rows:
            if not (lo_ts < r["ts"] < hi_ts):
                continue
            if r.get("num"):
                continue
            path = os.path.join(FRAMES, r["file"])
            got = read_left_number(path, NUM_RANGE)
            if got == n:
                r["num"] = n
                filled.append((round(r["ts"]), n, r["file"]))
                break
    visual = {"frame_106.jpg": 37, "frame_137.jpg": 53}
    for r in rows:
        n = visual.get(r["file"])
        if n and r.get("num") != n:
            r["num"] = n
            filled.append((round(r["ts"]), n, r["file"]))
    if filled:
        print("gap filled", filled)
        badges = [(r["ts"], r["num"]) for r in rows if r.get("num")]
        starts = detect_first_starts(badges, NUM_RANGE)
    print("starts", len(starts), [(round(ts), n) for ts, n in starts])
    missing = [i for i in range(1, 61) if i not in {n for _, n in starts}]
    print("missing", missing)

    groups = group_frames(rows)
    for g in groups:
        g.setdefault("ts", g["members"][0].get("ts", 0))
        g.setdefault("file", os.path.join(FRAMES, g["members"][0]["file"]))
        # keep basename for assign, full path separately
        g["file"] = g["members"][0]["file"]
    print("groups", len(groups))
    q = assign_questions(groups, starts, margin=90)
    q = mark_duplicate_stems(q)

    answers = []
    if os.path.isfile(VTT):
        answers = extract_answers(vtt_to_text(VTT))
    print("answers", len(answers), answers[:20])
    keys = digit_keys(q)
    for i, k in enumerate(keys):
        if i < len(answers):
            q[k]["answer"] = answers[i]
        else:
            q[k]["answer"] = None

    os.makedirs(OUT_IMG, exist_ok=True)
    copied = []
    for k in keys:
        src = os.path.join(FRAMES, q[k]["file"])
        dest_name = f"q{int(k):02d}.jpg"
        dest = os.path.join(OUT_IMG, dest_name)
        if q[k].get("image_confirmed"):
            upscale(src, dest)
            copied.append(dest)
            q[k]["file"] = dest_name
        else:
            q[k]["file"] = dest_name
    dups = image_md5_duplicates(copied) if copied else {}
    print("images", len(copied), "md5_dups", len(dups))

    md = render_round_note("2025-1회", q, source="youtube")
    os.makedirs(os.path.dirname(OUT_NOTE), exist_ok=True)
    open(OUT_NOTE, "w", encoding="utf-8").write(md)
    print("note", OUT_NOTE, "questions", len(keys))

    vault_img = os.path.join(VAULT, "기출문제", "이미지", "2025-1회")
    vault_note = os.path.join(VAULT, "기출문제", "2025-1회.md")
    os.makedirs(vault_img, exist_ok=True)
    os.makedirs(os.path.dirname(vault_note), exist_ok=True)
    for p in copied:
        dest = os.path.join(vault_img, os.path.basename(p))
        Image.open(p).save(dest, quality=90)
    open(vault_note, "w", encoding="utf-8").write(md)
    print("vault", vault_note)


if __name__ == "__main__":
    main()
