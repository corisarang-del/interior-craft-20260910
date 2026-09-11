#!/usr/bin/env python3
"""Fill one youtube round. Images untouched. Persist per question. Skip 미확정 overwrite."""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(__file__))
from answers_status import apply_answers_to_note
from collect_round_rows import load_round_rows
from last_frames import last_frames_from_rows
from vision_marks import merge_mark_items

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"
MODEL = "gpt-5.6-luna"


def _prompt():
    return open(os.path.join(ROOT, "scripts/vision_prompt.txt"), encoding="utf-8").read()


def call_vision(image_path, retries=6):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    body = {
        "model": MODEL,
        "max_tokens": 300,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _prompt()},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
    }
    last_err = None
    for attempt in range(retries):
        inp = outp = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
                json.dump(body, tmp, ensure_ascii=False)
                inp = tmp.name
            outp = inp + ".out"
            r = subprocess.run(
                ["minis-model-use", "run", "--model", MODEL, "--input", inp, "--output", outp],
                capture_output=True,
                text=True,
            )
            combined = (r.stdout or "") + (r.stderr or "")
            if r.returncode != 0 or "Rate limited" in combined:
                last_err = combined[-200:]
                time.sleep(15 * (attempt + 1))
                continue
            if not os.path.isfile(outp):
                last_err = "no output"
                time.sleep(8)
                continue
            raw = open(outp, encoding="utf-8").read()
            rec = parse_model_json(raw)
            if rec:
                return rec
            last_err = "bad json"
        except Exception as e:
            last_err = type(e).__name__
            time.sleep(8)
        finally:
            for p in (inp, outp):
                if p and os.path.isfile(p):
                    os.unlink(p)
    return {"answer": None, "status": "미확정", "why": f"vision fail {last_err}"}


def parse_model_json(raw):
    data = json.loads(raw)
    text = None
    if isinstance(data, dict):
        ch = data.get("choices") or []
        if ch:
            msg = ch[0].get("message") or {}
            text = msg.get("content")
        if not text:
            text = data.get("text") or data.get("output_text")
        if isinstance(text, list):
            text = "".join(
                (b.get("text") or "") if isinstance(b, dict) else str(b) for b in text
            )
    if not text:
        text = raw
    s = str(text).strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s.split("\n", 1)[-1]
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end < 0:
        return None
    return json.loads(s[start : end + 1])


def meta_path(round_id):
    return os.path.join(ROOT, "metadata", f"answers_{round_id}.json")


def load_meta(round_id):
    p = meta_path(round_id)
    if os.path.isfile(p):
        return json.load(open(p, encoding="utf-8"))
    return {"round": round_id, "replace_note_image": False, "answers": {}, "raw": []}


def save_meta(round_id, meta):
    json.dump(meta, open(meta_path(round_id), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def apply_note(round_id, updates):
    if not updates:
        return
    for path in (
        os.path.join(VAULT, "기출문제", f"{round_id}.md"),
        os.path.join(ROOT, "out/notes", f"{round_id}.md"),
    ):
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        open(path, "w", encoding="utf-8").write(apply_answers_to_note(text, updates))


def question_windows(rows):
    starts = {}
    for r in rows:
        n = r.get("num")
        if n is None:
            continue
        n = int(n)
        ts = r.get("ts") or 0
        if n not in starts or ts < starts[n]:
            starts[n] = ts
    ordered = sorted(starts)
    windows = {}
    for i, n in enumerate(ordered):
        lo = starts[n]
        hi = starts[ordered[i + 1]] if i + 1 < len(ordered) else 10**9
        if hi - lo > 180:
            hi = lo + 180
        windows[n] = (lo, hi)
    return windows


def fill_round(round_id, only=None, limit=None):
    rows, rnd = load_round_rows(round_id)
    last = last_frames_from_rows(rows, windows=question_windows(rows))
    nums = sorted(last)
    if only:
        nums = [n for n in nums if n in only]
    if limit:
        nums = nums[: int(limit)]
    meta = load_meta(round_id)
    existing = meta.get("answers") or {}
    raw = meta.get("raw") or []
    for n in nums:
        prev = existing.get(str(n))
        if prev and prev.get("status") in ("확정", "추론") and prev.get("answer"):
            print(round_id, n, "skip", prev.get("status"), prev.get("answer"))
            continue
        info = last[n]
        path = info["path"]
        if not path or not os.path.isfile(path):
            rec = {"num": n, "answer": None, "status": "미확정", "why": "no frame"}
        else:
            rec = call_vision(path) or {}
            rec["num"] = n
            rec["frame"] = info.get("file")
            rec["source"] = "image" if rec.get("status") == "확정" else "solve"
        print(round_id, n, rec.get("status"), rec.get("answer"), rec.get("why"))
        merged = merge_mark_items([rec])
        if str(n) in merged and merged[str(n)].get("status") != "미확정":
            existing[str(n)] = merged[str(n)]
            apply_note(round_id, {str(n): merged[str(n)]})
        raw = [x for x in raw if x.get("num") != n]
        raw.append(rec)
        meta["answers"] = existing
        meta["raw"] = raw
        save_meta(round_id, meta)
        time.sleep(1.5)
    return existing


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: fill_round_answers.py 2025-1회 [limit]")
    rid = sys.argv[1]
    limit = sys.argv[2] if len(sys.argv) > 2 else None
    fill_round(rid, limit=limit)


if __name__ == "__main__":
    main()
