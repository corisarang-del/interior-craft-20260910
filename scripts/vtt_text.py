"""Flatten rolling YouTube VTT to last-line-only text."""
import re


def vtt_to_text(path):
    lines = []
    seen_tail = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("WEBVTT") or "-->" in line or line.isdigit():
                continue
            line = re.sub(r"<[^>]+>", "", line)
            if line == seen_tail:
                continue
            lines.append(line)
            seen_tail = line
    return "\n".join(lines)
