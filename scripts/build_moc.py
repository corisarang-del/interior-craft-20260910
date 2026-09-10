#!/usr/bin/env python3
"""Write vault MOC from inventory. Source-none rounds are listed, not linked."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from inventory import load_inventory

VAULT = "/var/minis/mounts/minis1/obsidian-vault/지식/실내건축기능사"
MOC = os.path.join(VAULT, "_moc", "실내건축기능사-MOC.md")


def main():
    data = load_inventory()
    lines = [
        "---",
        "날짜: 2026-09-10",
        "태그: [실내건축기능사, MOC]",
        "분야: 실내건축기능사",
        "zettel_id: 20260910fa440a",
        "---",
        "# 실내건축기능사 필기 기출 지식맵",
        "",
        "## 회차별 기출문제",
        "",
    ]
    for r in data["rounds"]:
        rid = r["id"]
        src = r["source"]
        note = os.path.join(VAULT, "기출문제", f"{rid}.md")
        if src == "none":
            lines.append(f"- {rid} — 공개 복원 소스 없음")
        elif os.path.isfile(note):
            lines.append(f"- [[지식/실내건축기능사/기출문제/{rid}|{rid}]] ({src})")
        else:
            lines.append(f"- {rid} — 소스 있음, 노트 미생성 ({src})")
    lines.extend(
        [
            "",
            "## 핵심요약",
            "",
            "- [[지식/실내건축기능사/기출핵심요약/실내건축기능사|기출핵심요약 100]]",
            "",
            "## 역링크",
            "- [[홈-대시보드]]",
            "",
        ]
    )
    os.makedirs(os.path.dirname(MOC), exist_ok=True)
    open(MOC, "w", encoding="utf-8").write("\n".join(lines))
    print("wrote", MOC)


if __name__ == "__main__":
    main()
