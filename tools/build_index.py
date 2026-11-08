"""Rebuild the lesson list on the home page from lessons.json (AGENTS.md §8).

Usage:  python tools/build_index.py
Only the block between <!-- LESSONS:START --> and <!-- LESSONS:END --> in index.html is rewritten.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def card(it: dict) -> str:
    e = html.escape
    return (
        '    <li class="lesson-item">\n'
        f'      <a href="lessons/{e(it["slug"])}/">\n'
        f'        <span class="code">{e(it["code"])}</span>\n'
        f'        <span><h2>{e(it["title"])}</h2><p>{e(it["summary"])}</p></span>\n'
        f'        <span class="meta">{e(it["level"])} · {int(it["minutes"])} 分鐘</span>\n'
        "      </a>\n"
        "    </li>\n"
    )


def main() -> None:
    items = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    block = "<!-- LESSONS:START -->\n" + "".join(card(it) for it in items) + "    <!-- LESSONS:END -->"
    new, n = re.subn(r"<!-- LESSONS:START -->.*?<!-- LESSONS:END -->", lambda _m: block, text, flags=re.S)
    if n != 1:
        raise SystemExit("index.html must contain exactly one LESSONS:START/END block")
    path.write_text(new, encoding="utf-8", newline="\n")
    print(f"index.html: {len(items)} lesson card(s)")


if __name__ == "__main__":
    main()
