"""Sentence-level spot check of the report draft (Step 51; reused in Step 55).

Run from the repository root:

    python -m study_program_intelligence.report.spotcheck [n] [seed]

Draws n sentences (default 10, seed 20261018) that contain at least one key number from the section texts in
docs/report/ (main text only), and prints a side-by-side table: section, the sentence as rendered, the key numbers
in it, their source doc and the text in that doc the number was matched against. Output: reports/final/spotcheck.md.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import yaml

from .draft import PLACEHOLDER, SRC
from .key_numbers import load as load_numbers

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "reports" / "final" / "spotcheck.md"


def sentences(text: str) -> list[str]:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"^\|.*\|$", " ", text, flags=re.M)          # tables are checked via their own key numbers
    blocks = re.split(r"\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#))", text)   # paragraphs, list items, headings
    out = []
    for b in blocks:
        b = re.sub(r"\s+", " ", re.sub(r"^\s*(?:[-*] |\d+\. |#+ )", "", b)).strip()
        # sentence ends at . or : but not after abbreviations such as "St.", "e.g." or list labels such as "C."
        out += [s.strip() for s in re.split(r"(?<!\bSt\.)(?<!e\.g\.)(?<!i\.e\.)(?<!\b[A-D]\.)(?<=[.:])\s+(?=[A-Z*])", b)
                if PLACEHOLDER.search(s)]
    return out


def context(kn_entry: dict, width: int = 70) -> str:
    """The line of the source doc that contains the checked text, shortened around it."""
    doc = (REPO_ROOT / kn_entry["source_doc"]).read_text(encoding="utf-8")
    chk = kn_entry["check"]
    flat = re.sub(r"\s+", " ", doc)
    i = flat.find(chk)
    if i < 0:
        return chk
    return ("..." + flat[max(0, i - width):i + len(chk) + width].strip() + "...").replace("|", "/")


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    n = int(argv[0]) if argv else 10
    seed = int(argv[1]) if len(argv) > 1 else 20261018
    cfg = yaml.safe_load((SRC / "report.yaml").read_text(encoding="utf-8"))
    kn = load_numbers()
    pool = [(name, s) for name in cfg["sections"] for s in sentences((SRC / name).read_text(encoding="utf-8"))
            if not any(k.startswith(("fig:", "table:")) for k in PLACEHOLDER.findall(s))]
    pick = random.Random(seed).sample(pool, min(n, len(pool)))
    rows = ["| # | Section | Sentence in the report | Key numbers | Source doc | Matched text in the source doc |",
            "|---|---|---|---|---|---|"]
    for i, (name, s) in enumerate(pick, 1):
        keys = [k.removeprefix("val:") for k in PLACEHOLDER.findall(s)]
        rendered = PLACEHOLDER.sub(lambda m: f"**{kn[m.group(1).removeprefix('val:')]['display']}**", s).replace("|", "/")
        src = "<br>".join(sorted({kn[k]["source_doc"].replace("docs/", "") for k in keys}))
        chk = "<br>".join(f"{k}: {context(kn[k])}" for k in keys)
        rows.append(f"| {i} | {name.removesuffix('.md')} | {rendered} | {', '.join(keys)} | {src} | {chk} |")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(f"# Spot check: {len(pick)} sentences (seed {seed}, pool {len(pool)})\n\n" + "\n".join(rows) + "\n",
                   encoding="utf-8")
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({len(pick)} of {len(pool)} sentences with key numbers, seed {seed})")


if __name__ == "__main__":
    main()
