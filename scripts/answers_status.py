"""Answer status: 미확정 / 추론 / 확정. Never invent. Never zip subtitles."""
import re

from answers import normalize_choice

UNCONFIRMED = "미확정"
INFERRED = "추론"
CONFIRMED = "확정"

ANSWER_LINE_RE = re.compile(
    r"^\*\*정답:\s*(미확정|([①②③④])(?:\s*\(추론\))?)\*\*[ \t]*$",
    re.M,
)
Q_HEADER_RE = re.compile(r"^###\s+(\d+)\.\s*$", re.M)


def validate_mark(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if s in ("", "미확정", "없음"):
        return None
    return normalize_choice(s) if normalize_choice(s) in ("①", "②", "③", "④") else None


def format_answer_line(answer, status):
    if status == UNCONFIRMED or not answer:
        if status == CONFIRMED:
            raise ValueError("confirmed answer requires a choice")
        return "**정답: 미확정**"
    mark = validate_mark(answer)
    if not mark:
        raise ValueError("invalid choice")
    if status == INFERRED:
        return f"**정답: {mark} (추론)**"
    if status == CONFIRMED:
        return f"**정답: {mark}**"
    return "**정답: 미확정**"


def parse_answers_from_note(text):
    parts = Q_HEADER_RE.split(text)
    out = {}
    # split: preamble, num, body, num, body...
    i = 1
    while i + 1 < len(parts):
        num = parts[i]
        body = parts[i + 1]
        m = ANSWER_LINE_RE.search(body)
        if not m:
            i += 2
            continue
        raw = m.group(1)
        if raw == "미확정":
            out[num] = {"answer": None, "status": UNCONFIRMED}
        elif m.group(0).find("(추론)") >= 0:
            out[num] = {"answer": m.group(2), "status": INFERRED}
        else:
            out[num] = {"answer": m.group(2), "status": CONFIRMED}
        i += 2
    return out


def apply_answers_to_note(text, updates):
    parts = Q_HEADER_RE.split(text)
    out = [parts[0]]
    i = 1
    while i + 1 < len(parts):
        num = parts[i]
        body = parts[i + 1]
        upd = updates.get(str(num))
        if upd is None and str(num).isdigit():
            upd = updates.get(int(num))
        if upd:
            mark = validate_mark(upd.get("answer"))
            status = upd.get("status") or UNCONFIRMED
            if not mark:
                status = UNCONFIRMED
            line = format_answer_line(mark, status)
            if ANSWER_LINE_RE.search(body):
                body = ANSWER_LINE_RE.sub(line, body, count=1)
            else:
                body = body.rstrip() + "\n\n" + line + "\n"
        out.append(f"### {num}.\n")
        if body.startswith("\n"):
            out.append(body)
        else:
            out.append("\n" + body)
        i += 2
    return "".join(out)


def reset_untrusted_answers(text):
    def repl(_m):
        return "**정답: 미확정**"

    return ANSWER_LINE_RE.sub(repl, text)
