"""Build the report draft (Step 51) from the section texts in docs/report/.

Run from the repository root after report.build (key numbers and figures must be current):

    python -m study_program_intelligence.report.draft

Section texts (docs/report/NN_*.md, order and settings in docs/report/report.yaml) contain no typed numbers:
  {{key}}        -> the key number's display text from reports/key_numbers.yaml
  {{fig:fNN_x}}  -> the shared figure reports/figures/fNN_x.png with a numbered caption (title, message, source)
  [@key]         -> author-year citation (docs/report/references.yaml, pandoc --citeproc)
  <!-- ... -->   -> author notes, removed from the output
Checks (the build fails on the first two): unknown placeholder; typed number in the text (percentages, decimals,
thousands separators, integers >= 10 unless allowed in report.yaml). Reported: missing sections, words vs. target.
Outputs: reports/final/report.md, plus report.docx / report.pdf via pandoc (PDF only if a LaTeX engine is found).
"""

from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

import yaml

from .key_numbers import load as load_numbers

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "docs" / "report"
FIG = REPO_ROOT / "reports" / "figures"
OUT_DIR = REPO_ROOT / "reports" / "final"
OUT = OUT_DIR / "report.md"
PLACEHOLDER = re.compile(r"\{\{\s*([\w:]+)\s*\}\}")
TYPED = re.compile(r"\d+(?:[.,]\d+)*\s?%|\b\d{1,3}(?:,\d{3})+\b|\b\d+\.\d+\b|\b\d{2,}\b")


def figure_index() -> dict[str, dict]:
    rows = (FIG / "index.md").read_text(encoding="utf-8").splitlines()[4:]
    out = {}
    for r in rows:
        c = [x.strip() for x in r.strip("|").split("|")]
        if len(c) == 4:
            out[c[0].removesuffix(".png")] = {"title": c[1], "message": c[2], "source": c[3]}
    return out


def _cell(x) -> str:
    return re.sub(r"\s+", " ", str(x if x is not None else "")).replace("|", "/").strip()


def table_sources() -> str:
    """All registered sources (configs/sources.yaml), one row each."""
    src = yaml.safe_load((REPO_ROOT / "configs" / "sources.yaml").read_text(encoding="utf-8"))["sources"]
    rows = ["| Source | Data | Used for | Access |", "|-------------|--------------------|----------------|------------------|"]
    for s in src:
        rows.append(f"| {_cell(s.get('owner'))} | {_cell(s.get('table') or s.get('title') or s.get('url'))} | "
                    f"{_cell(s.get('use'))} | {_cell(s.get('access') or s.get('status'))} |")
    return "\n".join(rows)


def table_scores() -> str:
    """Score sheet (configs/scores.yaml): low / central / high and evidence strength per option and criterion."""
    sc = yaml.safe_load((REPO_ROOT / "configs" / "scores.yaml").read_text(encoding="utf-8"))["options"]
    rows = ["| Option | Criterion | Low / central / high | Strength | Evidence |",
            "|----------|--------------|--------|------|------------------------------|"]
    for o, s in sc.items():
        for crit in ("student_demand", "labour_relevance", "institutional_fit", "feasibility", "differentiation", "regional_contribution"):
            e = s[crit]
            if crit == "student_demand":
                t = e["trend"]
                rng = f"model + trend {t['low']} / {t['central']} / {t['high']}"
                strength = f"model {e['capture']['strength']}, trend {t['strength']}"
                ev = f"{e['capture']['source']}; {t['evidence']}"
            elif crit == "regional_contribution":
                rng, strength, ev = "computed from (c)", e["strength"], e["source"]
            else:
                rng, strength, ev = f"{e['low']} / {e['central']} / {e['high']}", e["strength"], e["evidence"]
            rows.append(f"| {_cell(s['label'])} | {crit.replace('_', ' ')} | {_cell(rng)} | {_cell(strength)} | {_cell(ev)} |")
    return "\n".join(rows)


TABLES = {"sources": table_sources, "scores": table_scores}


def typed_numbers(text: str, allowed: list[str]) -> list[str]:
    t = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    t = PLACEHOLDER.sub(" ", t)
    t = re.sub(r"\[@[^\]]*\]|@\w+", " ", t)                  # citations
    t = re.sub(r"\]\([^)]*\)", "]", t)                        # link targets
    t = re.sub(r"`[^`]*`", " ", t)                            # code spans (file names, commands)
    t = re.sub(r"^#+ .*$", " ", t, flags=re.M)                # headings carry section numbers
    for a in allowed:
        t = re.sub(a, " ", t)
    return TYPED.findall(t)


def render_section(name: str, kn: dict, figs: dict, counter: list[int], allowed: list[str]) -> tuple[str, list[str]]:
    path = SRC / name
    if not path.exists():
        return f"\n*[{name}: section to be written]*\n", [f"missing section {name}"]
    raw = path.read_text(encoding="utf-8")
    problems = [f"{name}: typed number '{x}'" for x in typed_numbers(raw, allowed)]
    raw = re.sub(r"<!--.*?-->\n?", "", raw, flags=re.S)        # author notes never reach the output

    def sub(m: re.Match) -> str:
        key = m.group(1)
        if key.startswith("table:"):
            if key[6:] not in TABLES:
                problems.append(f"{name}: unknown table {key[6:]}")
                return m.group(0)
            return TABLES[key[6:]]()
        if key.startswith("fig:"):
            f = key[4:]
            if f not in figs:
                problems.append(f"{name}: unknown figure {f}")
                return m.group(0)
            counter[0] += 1
            i = figs[f]
            return (f"![{i['title']}. {i['message']} Source: {i['source']}.]"   # pandoc adds "Figure N:"
                    f"(../figures/{f}.png){{width=100%}}")
        bare = key.startswith("val:")          # {{val:key}} -> the plain value (e.g. 9 instead of "9 theme groups")
        key = key.removeprefix("val:")
        if key not in kn:
            problems.append(f"{name}: unknown key number {key}")
            return m.group(0)
        return str(kn[key]["value"]) if bare else kn[key]["display"]

    text = PLACEHOLDER.sub(sub, raw)
    return text.strip() + "\n", problems


def words(text: str) -> int:
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", " ", text)   # figure captions counted separately (small)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    return len(re.findall(r"[A-Za-zÄÖÜäöüß0-9][\w'’./%-]*", t))


def build() -> tuple[Path, list[str], dict]:
    cfg = yaml.safe_load((SRC / "report.yaml").read_text(encoding="utf-8"))
    kn, figs = load_numbers(), figure_index()
    counter = [0]
    allowed = cfg.get("allowed_numbers", [])
    main, appendix, problems = [], [], []
    for name in cfg["sections"]:
        t, p = render_section(name, kn, figs, counter, allowed)
        main.append(t)
        problems += p
    for name in cfg.get("appendix", []):
        t, p = render_section(name, kn, figs, counter, allowed)
        appendix.append(t)
        problems += p
    date = dt.date.today().isoformat() if cfg.get("date", "auto") == "auto" else cfg["date"]
    meta = {"title": cfg["title"], "subtitle": cfg.get("subtitle"), "author": cfg["authors"], "date": date,
            "lang": cfg.get("lang", "en-GB"), "bibliography": str((SRC / cfg["citations"]["bibliography"]).as_posix()),
            "link-citations": True, "reference-section-title": "References", "toc": True,
            "subject": cfg.get("supervisor_line")}
    body = ("\n\n".join(main) + "\n\n# References {-}\n\n::: {#refs}\n:::\n\n"
            + ("\\newpage\n\n# Appendix {-}\n\n" + "\n\n".join(appendix) if appendix else ""))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n" + body, encoding="utf-8")
    n_main = words("\n".join(main))
    lo, hi = cfg["length"]["target_pages"]
    wpp = cfg["length"]["words_per_page"]
    fig_pages = cfg["length"].get("pages_per_figure", 0.5)
    stats = {"words_main": n_main, "pages_main_est": round(n_main / wpp + fig_pages * counter[0], 1), "target_pages": (lo, hi),
             "figures": counter[0],
             "missing": [p for p in problems if p.startswith("missing")]}
    return OUT, problems, stats


def convert(cfg_formats: list[str]) -> list[str]:
    import pypandoc
    notes = []
    args = ["--citeproc", f"--resource-path={OUT_DIR.as_posix()}", "--toc", "--number-sections"]   # Summary = unnumbered, Method = 1
    if "docx" in cfg_formats:
        pypandoc.convert_file(str(OUT), "docx", outputfile=str(OUT_DIR / "report.docx"), extra_args=args)
        notes.append("reports/final/report.docx")
    if "pdf" in cfg_formats:
        engine = next((e for e in ("xelatex", "lualatex", "pdflatex") if shutil.which(e)), None)
        if engine is None:
            notes.append("PDF skipped: no LaTeX engine on PATH")
        else:
            try:
                pypandoc.convert_file(str(OUT), "pdf", outputfile=str(OUT_DIR / "report.pdf"),
                                      extra_args=args + [f"--pdf-engine={engine}", "-V", "geometry:margin=2.5cm",
                                                         "-V", "fontsize=11pt"])
                notes.append(f"reports/final/report.pdf ({engine})")
            except RuntimeError as e:
                notes.append(f"PDF failed ({engine}): {str(e).strip().splitlines()[-1][:200]}")
    return notes


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    out, problems, stats = build()
    hard = [p for p in problems if not p.startswith("missing")]
    print(f"Written: {out.relative_to(REPO_ROOT)}")
    print(f"Main text: {stats['words_main']} words = ~{stats["pages_main_est"]} pages incl. figures (target {stats['target_pages'][0]}-"
          f"{stats['target_pages'][1]}); figures: {stats['figures']}")
    if stats["missing"]:
        print("Not yet written:", ", ".join(m.split()[-1] for m in stats["missing"]))
    if hard:
        print("FAILED checks:\n  " + "\n  ".join(hard))
        sys.exit(1)
    if "--no-convert" not in argv:
        cfg = yaml.safe_load((SRC / "report.yaml").read_text(encoding="utf-8"))
        for n in convert(cfg.get("formats", [])):
            print("Converted:", n)


if __name__ == "__main__":
    main()
