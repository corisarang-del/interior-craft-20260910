"""Merge vision/solve mark items into answer updates. Invalid marks dropped."""
from answers_status import CONFIRMED, INFERRED, UNCONFIRMED, validate_mark


def merge_mark_items(items):
    out = {}
    for it in items or []:
        try:
            num = int(it.get("num"))
        except (TypeError, ValueError):
            continue
        status = it.get("status") or UNCONFIRMED
        mark = validate_mark(it.get("answer"))
        if status == CONFIRMED:
            if not mark:
                continue
            out[str(num)] = {
                "answer": mark,
                "status": CONFIRMED,
                "source": it.get("source") or "image",
                "why": it.get("why"),
                "frame": it.get("frame"),
            }
        elif status == INFERRED:
            if not mark:
                continue
            out[str(num)] = {
                "answer": mark,
                "status": INFERRED,
                "source": it.get("source") or "solve",
                "why": it.get("why"),
                "frame": it.get("frame"),
            }
        else:
            out[str(num)] = {
                "answer": None,
                "status": UNCONFIRMED,
                "source": None,
                "why": it.get("why"),
                "frame": it.get("frame"),
            }
    return out
