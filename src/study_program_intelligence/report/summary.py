"""Plain-English project summary (Step 57), built like the report from placeholders.

Run from the repository root (after report.build):

    python -m study_program_intelligence.report.summary [--no-pdf]

Source: docs/summary/*.md in the order of docs/summary/summary.yaml. Same number rules as the report: numbers only as
{{key}} / {{val:key}} placeholders from reports/key_numbers.yaml, figures as {{fig:fNN_name}} with the plain caption
from summary.yaml; the build fails on typed numbers or unknown placeholders.
Readability check (reported, not enforced): average sentence length, sentences over the limit, technical terms used
in the text but missing from the glossary, and terms that should be avoided altogether.
Outputs: reports/final/project_summary.md, reports/final/project_summary.pdf, reports/final/summary_readability.md.
"""

from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

import yaml

from .draft import OUT_DIR, PLACEHOLDER, SRC as REPORT_SRC, figure_index, typed_numbers
from .key_numbers import load as load_numbers

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "docs" / "summary"
OUT = OUT_DIR / "project_summary.md"
PDF = OUT_DIR / "project_summary.pdf"
CHECK = OUT_DIR / "summary_readability.md"


def render(name: str, kn: dict, figs: dict, captions: dict, allowed: list[str]) -> tuple[str, list[str]]:
    raw = (SRC / name).read_text(encoding="utf-8")
    problems = [f"{name}: typed number '{x}'" for x in typed_numbers(raw, allowed)]
    raw = re.sub(r"<!--.*?-->\n?", "", raw, flags=re.S)

    def sub(m: re.Match) -> str:
        key = m.group(1)
        if key.startswith("fig:"):
            f = key[4:]
            if f not in figs or f not in captions:
                problems.append(f"{name}: figure {f} unknown or without a plain caption in summary.yaml")
                return m.group(0)
            cap = PLACEHOLDER.sub(lambda c: kn[c.group(1)]["display"] if c.group(1) in kn else c.group(0), captions[f])
            return f"![{cap}](../figures/{f}.png){{width=92%}}"
        bare = key.startswith("val:")
        key = key.removeprefix("val:")
        if key not in kn:
            problems.append(f"{name}: unknown key number {key}")
            return m.group(0)
        return str(kn[key]["value"]) if bare else kn[key]["display"]

    return PLACEHOLDER.sub(sub, raw).strip() + "\n", problems


def prose(text: str) -> str:
    """Running text only: no headings, tables, figures, code or link targets."""
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", " ", text)
    t = re.sub(r"^\s*\|.*$", " ", t, flags=re.M)
    t = re.sub(r"^#+ .*$", " ", t, flags=re.M)
    t = re.sub(r"`[^`]*`", " ", t)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    return re.sub(r"[*_\[\]]", "", t)


def sentences(text: str) -> list[str]:
    # paragraphs and list items end a sentence even without a full stop
    t = re.sub(r"^\s*(?:-|\d+\.)\s+", "\n\n", prose(text), flags=re.M)
    parts = []
    for block in re.split(r"\n\s*\n", t):
        block = re.sub(r"\s+", " ", block)
        parts += re.split(r"(?<!\bSt\.)(?<!e\.g\.)(?<!i\.e\.)(?<!B\.Sc\.)(?<!M\.Sc\.)(?<=[.!?])\s+(?=[A-Z0-9\"(])", block)
    return [p.strip() for p in parts if len(p.split()) >= 3]


def readability(body: str, glossary: str, cfg: dict) -> tuple[str, dict]:
    sents = sentences(body)
    lengths = [len(s.split()) for s in sents]
    avg = sum(lengths) / len(lengths) if lengths else 0
    limit = cfg["readability"]["max_sentence_words"]
    long = [(n, s) for n, s in zip(lengths, sents) if n > limit]
    low_body, low_gloss = body.lower(), glossary.lower()
    unexplained = [t for t in cfg["readability"]["terms"] if re.search(rf"\b{re.escape(t.lower())}\b", low_body)
                   and not re.search(rf"\*\*{re.escape(t.lower())}:?\*\*", low_gloss)]
    avoided = [t for t in cfg["readability"]["avoid"] if re.search(rf"\b{re.escape(t.lower())}\b", low_body)]
    lines = ["# Readability check of the project summary (generated)", "",
             f"Sentences: {len(sents)}; average length {avg:.1f} words (target <= {cfg['readability']['avg_sentence_words']}); "
             f"longer than {limit} words: {len(long)}.", "",
             "Technical terms used but not in the glossary: " + (", ".join(unexplained) or "none") + ".", "",
             "Terms that should be avoided but appear: " + (", ".join(avoided) or "none") + ".", "",
             "## Long sentences", ""] + [f"- ({n} words) {s}" for n, s in long]
    return "\n".join(lines) + "\n", {"avg": avg, "n": len(sents), "long": len(long), "unexplained": unexplained,
                                      "avoided": avoided}


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    cfg = yaml.safe_load((SRC / "summary.yaml").read_text(encoding="utf-8"))
    allowed = yaml.safe_load((REPORT_SRC / "report.yaml").read_text(encoding="utf-8"))["allowed_numbers"] + cfg.get("allowed_numbers", [])
    kn, figs = load_numbers(), figure_index()
    parts, problems = [], []
    for name in cfg["sections"]:
        t, p = render(name, kn, figs, cfg["captions"], allowed)
        parts.append((name, t))
        problems += p
    body = "\n\n".join(t for n, t in parts)
    glossary = "\n".join(t for n, t in parts if n == cfg["glossary_section"])
    report, stats = readability("\n\n".join(t for n, t in parts if n != cfg["glossary_section"]), glossary, cfg)
    CHECK.write_text(report, encoding="utf-8")
    meta = {"title": cfg["title"], "subtitle": cfg.get("subtitle"), "author": cfg["authors"],
            "date": dt.date.today().isoformat(), "lang": "en-GB",
            # keep each figure where it is in the text (no floating to a separate page)
            "header-includes": ["\\usepackage{float}", "\\floatplacement{figure}{H}"]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n" + body, encoding="utf-8")
    words = len(re.findall(r"[A-Za-z0-9][\w'’./%-]*", prose(body)))
    n_fig = body.count("](../figures/")
    pages = words / cfg["length"]["words_per_page"] + cfg["length"]["pages_per_figure"] * n_fig
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({words} words, {n_fig} figures, ~{pages:.1f} pages; "
          f"target {cfg['length']['target_pages'][0]}-{cfg['length']['target_pages'][1]})")
    print(f"Readability: average {stats['avg']:.1f} words per sentence ({stats['n']} sentences), {stats['long']} long; "
          f"terms not in glossary: {stats['unexplained'] or 'none'}; avoided terms used: {stats['avoided'] or 'none'} "
          f"-> {CHECK.relative_to(REPO_ROOT)}")
    if problems:
        print("FAILED checks:\n  " + "\n  ".join(problems))
        sys.exit(1)
    if "--no-pdf" not in argv:
        import pypandoc
        engine = next((e for e in ("xelatex", "lualatex", "pdflatex") if shutil.which(e)), None)
        if engine is None:
            print("PDF skipped: no LaTeX engine on PATH")
            return
        pypandoc.convert_file(str(OUT), "pdf", outputfile=str(PDF),
                              extra_args=[f"--resource-path={OUT_DIR.as_posix()}", "--toc", f"--pdf-engine={engine}",
                                          "-V", "geometry:margin=2.4cm", "-V", "fontsize=11pt", "-V", "linestretch=1.15"])
        print(f"Converted: {PDF.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
