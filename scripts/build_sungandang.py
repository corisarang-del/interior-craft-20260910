#!/usr/bin/env python3
"""Turn sungandang catalog PDFs into vault notes. No invented answers."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from notes import render_round_note
from pdf_parse import parse_catalog_text

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"
PDF_DIR = os.path.join(ROOT, "raw/sungandang")

ROUNDS = {
    "2026-1회": "2026-1회.pdf",
    "2026-2회": "2026-2회.pdf",
    "2026-3회": "2026-3회.pdf",
}


def pdf_text(path):
    r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True)
    r.check_returncode()
    return r.stdout or ""


def catalog_to_questions(data):
    qs = {}
    mapping = data["map"]
    new = data["new"]
    for k, row in mapping.items():
        if k in new:
            q = dict(new[k])
            q["kind"] = "new"
            q["topic"] = row.get("topic")
            q["answer"] = None
            qs[k] = q
        else:
            qs[k] = {
                "kind": "book_map",
                "topic": row.get("topic"),
                "page": row.get("page"),
                "book_num": row.get("book_num"),
                "answer": None,
                "image_confirmed": False,
                "file": None,
            }
    return qs


def main():
    for rid, fn in ROUNDS.items():
        path = os.path.join(PDF_DIR, fn)
        if not os.path.isfile(path):
            print("missing", path)
            continue
        data = parse_catalog_text(pdf_text(path))
        qs = catalog_to_questions(data)
        md = render_round_note(rid, qs, source="sungandang_pdf")
        out = os.path.join(ROOT, "out/notes", f"{rid}.md")
        vault = os.path.join(VAULT, "기출문제", f"{rid}.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        os.makedirs(os.path.dirname(vault), exist_ok=True)
        open(out, "w", encoding="utf-8").write(md)
        open(vault, "w", encoding="utf-8").write(md)
        print(rid, "map", len(data["map"]), "new", sorted(data["new"]), "note_q", len(qs))


if __name__ == "__main__":
    main()
