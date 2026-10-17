"""TH Mannheim, M.Sc. Technische Informatik: focus-area module tables from the programme page.

Run from the repository root:

    python -m study_program_intelligence.transform.thm_modules

The module handbook PDF is blocked by robots.txt (Disallow /fileadmin/), so the module
tables of the focus areas ("Schwerpunkt Security", "Schwerpunkt Industrial Internet of
Things") are taken from the cached programme page (downloaded by ingest/documents.py,
see configs/competitor_modules.yaml). Column "term" is the page's "Wann" (WS/SS: term in
which the module is offered), not a semester number.
"""

from __future__ import annotations

import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FOLDER = REPO_ROOT / "data" / "raw" / "competitor modules"
PAGE = FOLDER / "thm_ma_technische_informatik_page.html"
OUT = FOLDER / "thm_ma_technische_informatik_modules.csv"
MANIFEST = REPO_ROOT / "docs" / "competitor_modules_manifest.json"
FOCUS = ("Schwerpunkt Security", "Schwerpunkt Industrial Internet of Things")


class _Tables(HTMLParser):
    """Collect tables with the last text block before each (its heading)."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[tuple[str, list[list[str]]]] = []
        self._rows: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: str | None = None
        self._text, self._heading = "", ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._rows = []
        elif self._rows is not None and tag == "tr":
            self._row = []
        elif self._rows is not None and tag in ("td", "th"):
            self._cell = ""
        elif self._rows is None:
            self._text = ""

    def handle_endtag(self, tag):
        if self._cell is not None and tag in ("td", "th"):
            self._row.append(re.sub(r"\s+", " ", self._cell).strip())
            self._cell = None
        elif self._row is not None and tag == "tr":
            self._rows.append(self._row)
            self._row = None
        elif tag == "table" and self._rows is not None:
            self.tables.append((self._heading, self._rows))
            self._rows = None
        elif self._rows is None and self._text.strip():
            self._heading = re.sub(r"\s+", " ", self._text).strip()

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data
        elif self._rows is None:
            self._text += data


def extract(html: str) -> list[dict]:
    p = _Tables()
    p.feed(html)
    rows = []
    for heading, table in p.tables:
        if heading not in FOCUS:
            continue
        head = table[0]
        if head != ["Module", "Wann", "Semesterwochenstunden", "Credits"]:
            raise ValueError(f"unexpected header under {heading!r}: {head}")
        for module, term, sws, credits in table[1:]:
            rows.append({"focus_area": heading.removeprefix("Schwerpunkt "), "module": module,
                         "term": term, "sws": int(sws), "credits": int(credits)})
    found = {r["focus_area"] for r in rows}
    missing = [f for f in FOCUS if f.removeprefix("Schwerpunkt ") not in found]
    if missing:
        raise ValueError(f"focus areas not found on the page: {missing}")
    return rows


def main() -> None:
    rec = next(r for r in json.loads(MANIFEST.read_text(encoding="utf-8")) if r["id"] == PAGE.stem)
    rows = extract(PAGE.read_text(encoding="utf-8"))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[*rows[0], "source_url", "retrieved_utc"])
        w.writeheader()
        for r in rows:
            w.writerow({**r, "source_url": rec["url"], "retrieved_utc": rec["retrieved_utc"]})
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({len(rows)} modules)")


if __name__ == "__main__":
    main()
