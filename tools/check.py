"""Acceptance checks for 因果口袋講義 (AGENTS.md §9).

Usage:  python tools/check.py
Exit code 0 and "ALL CHECKS PASSED" when every rule holds; otherwise lists each problem.
Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"cover", "concept", "figure", "cards", "formula", "lab", "quiz", "summary"}
LEVELS = {"入門", "進階", "實務"}
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CODE_RE = re.compile(r"^CP-\d{2}$")
NOTE_HEAD_RE = re.compile(r"^## S(\d{2}) (\w+)｜(.+)$", re.M)
HEX_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")
TEMPLATE_TEXT = ("頁面標題", "用一個問題開場", "問題文字", "第一句。", "每張卡不超過 50 字")
NOTE_PLACEHOLDERS = ("（這一頁的最終文字）", "（標題）")
ALLOWED_EXTERNAL = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")

problems: list[str] = []


def bad(where: str, msg: str) -> None:
    problems.append(f"[{where}] {msg}")


class Lesson(HTMLParser):
    """Collects the facts check.py needs from one lesson page."""

    def __init__(self) -> None:
        super().__init__()
        self.body: dict[str, str] = {}
        self.slides: list[dict] = []  # {type, quiz:int, plain:int, formula:int, takeaways:int}
        self.quizzes: list[dict] = []  # {answer, opts:[(opt, has_why)]}
        self.resources: list[tuple[str, str]] = []  # (tag, url)
        self.styles: list[str] = []
        self._in_takeaways = 0
        self._depth_takeaways = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if "style" in a:
            self.styles.append(a["style"] or "")
        for k in ("fill", "stroke", "color"):
            if k in a:
                self.styles.append(a[k] or "")
        if tag == "body":
            self.body = a
        if tag == "section" and "slide" in cls:
            self.slides.append({"type": a.get("data-type"), "cls": cls, "quiz": 0,
                                "plain": 0, "formula": 0, "takeaways": 0})
        cur = self.slides[-1] if self.slides else None
        if cur is not None:
            if "quiz" in cls:
                cur["quiz"] += 1
                self.quizzes.append({"answer": a.get("data-answer"), "opts": []})
            if "plain" in cls:
                cur["plain"] += 1
            if "formula" in cls:
                cur["formula"] += 1
            if tag == "ol" and "takeaways" in cls:
                self._in_takeaways = 1
            elif tag == "li" and self._in_takeaways:
                cur["takeaways"] += 1
        if tag == "button" and "data-opt" in a and self.quizzes:
            self.quizzes[-1]["opts"].append((a["data-opt"], bool((a.get("data-why") or "").strip())))
        if tag == "script" and a.get("src"):
            self.resources.append(("script", a["src"]))
        if tag == "link" and a.get("href"):
            self.resources.append(("link", a["href"]))
        if tag in ("img", "image", "source") and (a.get("src") or a.get("href")):
            self.resources.append((tag, a.get("src") or a.get("href")))

    def handle_endtag(self, tag):
        if tag == "ol":
            self._in_takeaways = 0


def check_registry() -> list[dict]:
    path = ROOT / "lessons.json"
    try:
        items = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        bad("lessons.json", f"cannot parse: {e}")
        return []
    seen_slug, seen_code = set(), set()
    for i, it in enumerate(items):
        w = f"lessons.json#{i}"
        for k in ("slug", "code", "title", "summary", "minutes", "level"):
            if k not in it or it[k] in ("", None):
                bad(w, f"missing field '{k}'")
        slug, code = it.get("slug", ""), it.get("code", "")
        if not SLUG_RE.match(slug):
            bad(w, f"slug '{slug}' must be lowercase-english-with-hyphens")
        if not CODE_RE.match(code):
            bad(w, f"code '{code}' must look like CP-01")
        if slug in seen_slug:
            bad(w, f"duplicate slug '{slug}'")
        if code in seen_code:
            bad(w, f"duplicate code '{code}'")
        seen_slug.add(slug)
        seen_code.add(code)
        if it.get("level") not in LEVELS:
            bad(w, f"level must be one of {sorted(LEVELS)}")
        if len(it.get("summary", "")) > 40:
            bad(w, f"summary is {len(it['summary'])} chars (max 40)")
    on_disk = {p.name for p in (ROOT / "lessons").iterdir() if p.is_dir() and p.name != "_template"}
    for extra in sorted(on_disk - seen_slug):
        bad("lessons/", f"folder '{extra}' is not registered in lessons.json")
    return items


def check_lesson(it: dict) -> None:
    slug = it["slug"]
    w = f"lessons/{slug}"
    html_path = ROOT / "lessons" / slug / "index.html"
    note_path = ROOT / "notes" / f"{slug}.md"
    if not html_path.exists():
        bad(w, "index.html missing")
        return
    if not note_path.exists():
        bad(w, f"notes/{slug}.md missing (content first, AGENTS.md §4)")
    text = html_path.read_text(encoding="utf-8")
    if "{{" in text:
        bad(w, "template placeholder '{{...}}' left in page")
    for ph in TEMPLATE_TEXT:
        if ph in text:
            bad(w, f"template text '{ph}' left in page; replace it with the real content")
    if "TODO" in it.get("summary", ""):
        bad("lessons.json", f"summary of '{slug}' is still TODO")
    p = Lesson()
    p.feed(text)

    if p.body.get("data-code") != it["code"]:
        bad(w, f"<body data-code> is '{p.body.get('data-code')}', lessons.json says '{it['code']}'")
    if p.body.get("data-title") != it["title"]:
        bad(w, "<body data-title> differs from lessons.json title")

    n = len(p.slides)
    if not 6 <= n <= 12:
        bad(w, f"{n} slides (must be 6–12)")
    types = [s["type"] for s in p.slides]
    for i, s in enumerate(p.slides, 1):
        if s["type"] not in TYPES:
            bad(w, f"slide {i}: data-type '{s['type']}' not in {sorted(TYPES)}")
        clash = TYPES.intersection(s["cls"]) - {"slide"}
        if clash:
            bad(w, f"slide {i}: page type written as class {sorted(clash)}; use data-type")
        if s["type"] == "formula" and s["formula"] and s["plain"] < s["formula"]:
            bad(w, f"slide {i}: every .formula needs a .plain translation")
        if s["type"] == "quiz" and s["quiz"] == 0:
            bad(w, f"slide {i}: quiz page without a .quiz widget")
    if types and types[0] != "cover":
        bad(w, "first slide must be data-type=cover")
    if types and types[-1] != "summary":
        bad(w, "last slide must be data-type=summary")
    if "quiz" not in types:
        bad(w, "needs at least one quiz slide")
    for i, s in enumerate(p.slides, 1):
        if s["type"] == "summary" and s["takeaways"] != 3:
            bad(w, f"slide {i}: summary has {s['takeaways']} takeaways (must be exactly 3)")

    for qi, q in enumerate(p.quizzes, 1):
        opts = [o for o, _ in q["opts"]]
        if q["answer"] not in opts:
            bad(w, f"quiz {qi}: data-answer '{q['answer']}' is not one of the options {opts}")
        if not all(has for _, has in q["opts"]):
            bad(w, f"quiz {qi}: every option needs a data-why explanation")
        if len(opts) < 2:
            bad(w, f"quiz {qi}: needs at least 2 options")

    for tag, url in p.resources:
        if url.startswith(("http://", "https://", "//")):
            if not url.startswith(ALLOWED_EXTERNAL):
                bad(w, f"external {tag} '{url}' not allowed (Google Fonts only)")
            continue
        target = (html_path.parent / url.split("#")[0].split("?")[0]).resolve()
        if not target.exists():
            bad(w, f"{tag} '{url}' points to a missing file")
    needed = {("link", "../../shared/style.css"), ("script", "../../shared/deck.js")}
    for tag, url in needed - set(p.resources):
        bad(w, f"must include <{tag}> {url}")
    for s in p.styles:
        if HEX_RE.search(s):
            bad(w, f"hard-coded colour '{HEX_RE.search(s).group()}'; use CSS variables / svg classes")
    if re.search(r"<style[\s>]", text) and HEX_RE.search("".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S))):
        bad(w, "hard-coded colour inside <style> — use CSS variables")

    if note_path.exists():
        note_text = note_path.read_text(encoding="utf-8")
        if any(ph in note_text for ph in NOTE_PLACEHOLDERS):
            bad(f"notes/{slug}.md", "still has placeholder text; write the notes first (AGENTS.md section 4)")
        heads = NOTE_HEAD_RE.findall(note_text)
        nums = [int(h[0]) for h in heads]
        if nums != list(range(1, len(nums) + 1)):
            bad(f"notes/{slug}.md", f"headings must be S01, S02, … in order (found {nums})")
        note_types = [h[1] for h in heads]
        if note_types != types:
            bad(f"notes/{slug}.md", f"page types {note_types} differ from HTML {types}")


def check_home(items: list[dict]) -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<!-- LESSONS:START -->(.*?)<!-- LESSONS:END -->", text, re.S)
    if not m:
        bad("index.html", "LESSONS:START/END markers missing")
        return
    block = m.group(1)
    linked = re.findall(r'href="lessons/([^/"]+)/"', block)
    want = [it["slug"] for it in items]
    if linked != want:
        bad("index.html", f"cards {linked} differ from lessons.json {want}; run tools/build_index.py")


def main() -> int:
    for f in ("AGENTS.md", "CLAUDE.md", "NOTES.md", "log.md", ".nojekyll", "shared/style.css", "shared/deck.js"):
        if not (ROOT / f).exists():
            bad(f, "required file missing")
    items = check_registry()
    for it in items:
        if SLUG_RE.match(it.get("slug", "")):
            check_lesson(it)
    check_home(items)
    if problems:
        print(f"{len(problems)} PROBLEM(S):")
        for p in problems:
            print("  -", p)
        return 1
    print(f"checked {len(items)} lesson(s)")
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
