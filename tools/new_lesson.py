"""Scaffold a new lesson (AGENTS.md §4 step 3).

Usage:  python tools/new_lesson.py <slug> <CP-xx> "<title>" [level] [minutes]

Creates lessons/<slug>/index.html from lessons/_template, a matching notes/<slug>.md
skeleton, and appends an entry to lessons.json (summary left as TODO for you to fill).
Refuses to overwrite anything that already exists.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPE_RE = re.compile(r'<section class="slide" data-type="(\w+)">')


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        raise SystemExit(__doc__)
    slug, code, title = argv[0], argv[1], argv[2]
    level = argv[3] if len(argv) > 3 else "入門"
    minutes = int(argv[4]) if len(argv) > 4 else 10
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        raise SystemExit("slug must be lowercase english with hyphens")
    if not re.fullmatch(r"CP-\d{2}", code):
        raise SystemExit("code must look like CP-04")

    registry = ROOT / "lessons.json"
    items = json.loads(registry.read_text(encoding="utf-8"))
    if any(it["slug"] == slug or it["code"] == code for it in items):
        raise SystemExit("slug or code already in lessons.json")
    out_dir = ROOT / "lessons" / slug
    note = ROOT / "notes" / f"{slug}.md"
    if out_dir.exists() or note.exists():
        raise SystemExit("lesson folder or note already exists")

    tpl = (ROOT / "lessons" / "_template" / "index.html").read_text(encoding="utf-8")
    page = tpl.replace("{{CODE}}", code).replace("{{TITLE}}", title)
    out_dir.mkdir(parents=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8", newline="\n")

    lines = [f"# {code}｜{title}", "", "> 狀態：✏ 草稿（使用者確認後改成 ✅ 定稿）", ""]
    for i, t in enumerate(TYPE_RE.findall(tpl), 1):
        lines += [f"## S{i:02d} {t}｜（標題）", "", "（這一頁的最終文字）", ""]
    lines += ["## 參考", "", "- （課本或文獻；不要編造出處）", ""]
    note.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    items.append({"slug": slug, "code": code, "title": title,
                  "summary": "TODO：一句話說明讀者會帶走什麼", "minutes": minutes, "level": level})
    registry.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"created lessons/{slug}/index.html, notes/{slug}.md, lessons.json entry")
    print("next: write notes first, then the HTML, then run tools/build_index.py and tools/check.py")


if __name__ == "__main__":
    main(sys.argv[1:])
