#!/usr/bin/env python3
"""Copy notes/images/metadata/docs/tests/scripts into a session git workspace."""
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEST = "/var/minis/workspace/interior-craft-git"


def main():
    os.makedirs(DEST, exist_ok=True)
    for name in ["docs", "tests", "scripts", "metadata"]:
        src = os.path.join(ROOT, name)
        dst = os.path.join(DEST, name)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    shutil.copy2(os.path.join(ROOT, "README.md"), os.path.join(DEST, "README.md"))
    notes_src = os.path.join(ROOT, "out/notes")
    img_src = os.path.join(ROOT, "out/images")
    notes_dst = os.path.join(DEST, "notes")
    img_dst = os.path.join(DEST, "images")
    os.makedirs(notes_dst, exist_ok=True)
    if os.path.isdir(img_src):
        if os.path.isdir(img_dst):
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
    if os.path.isdir(notes_src):
        for fn in os.listdir(notes_src):
            if not fn.endswith(".md"):
                continue
            text = open(os.path.join(notes_src, fn), encoding="utf-8").read()
            text = re.sub(r"!\[\]\(이미지/([^)]+)\)", r"![](../images/\1)", text)
            open(os.path.join(notes_dst, fn), "w", encoding="utf-8").write(text)
    keep = {".git", "docs", "tests", "scripts", "metadata", "notes", "images", "README.md"}
    print("exported", DEST, "entries", sorted(os.listdir(DEST)))


if __name__ == "__main__":
    main()
