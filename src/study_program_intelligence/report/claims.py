"""Claim sheet for the independent review (Step 55).

Run from the repository root (dashboard texts need the generated data):

    python -m study_program_intelligence.report.claims

Collects every factual statement that a reader sees: the report sections (docs/report/, placeholders rendered from
the key numbers), the dashboard pages (texts, captions and metrics as rendered by Streamlit's test runner) and the
README "Result" block. Each claim gets an ID, its location, the key numbers it contains (value and source doc) and the
evidence docs it should rest on. Output: docs/review_claims.md (the reviewers' input; verdicts go to
docs/review_verdicts.md).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from .draft import PLACEHOLDER, SRC, figure_index
from .key_numbers import load as load_numbers

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "docs" / "review_claims.md"
ALL_EVIDENCE = sorted(str(p.relative_to(REPO_ROOT).as_posix()) for p in (REPO_ROOT / "docs").glob("evidence_*.md")) + [
    "docs/overlap_test.md", "docs/kill_rules.md", "docs/theme_precision.md", "docs/decision_log.md"]
ABBREV = r"(?<!\bSt\.)(?<!e\.g\.)(?<!i\.e\.)(?<!\b[A-D]\.)(?<!B\.Sc\.)(?<!M\.Sc\.)"


def _docs_in(text: str) -> list[str]:
    found = re.findall(r"(?:\.\./\.\./)?(docs/[\w./-]+\.md|configs/[\w.-]+\.yaml)", text)
    return sorted(set(found))


def _sentences(block: str) -> list[str]:
    block = re.sub(r"\s+", " ", re.sub(r"^\s*(?:[-*] |\d+\. )", "", block)).strip()
    parts = re.split(ABBREV + r"(?<=[.:;])\s+(?=[A-Z*(])", block)
    return [p.strip() for p in parts if len(p.split()) >= 5]


def _render(text: str, kn: dict, figs: dict) -> tuple[str, list[str]]:
    keys = []

    def sub(m: re.Match) -> str:
        k = m.group(1)
        if k.startswith("fig:"):
            f = figs.get(k[4:], {})
            return f"[Figure: {f.get('title', k[4:])}. {f.get('message', '')}]"
        if k.startswith("table:"):
            return ""
        k = k.removeprefix("val:")
        keys.append(k)
        return kn[k]["display"] if k in kn else m.group(0)

    return PLACEHOLDER.sub(sub, text), keys


def report_claims(kn: dict, figs: dict) -> list[dict]:
    cfg = yaml.safe_load((SRC / "report.yaml").read_text(encoding="utf-8"))
    out = []
    for name in cfg["sections"] + cfg.get("appendix", []):
        raw = (SRC / name).read_text(encoding="utf-8")
        head = re.match(r"\s*#.*?\n\s*<!--(.*?)-->", raw, flags=re.S)
        docs = _docs_in(head.group(1)) if head else []
        docs = sorted(set(docs + _docs_in(raw))) or ALL_EVIDENCE
        body = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
        section = name.removesuffix(".md")
        blocks = re.split(r"\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#|\|))", body)
        for b in blocks:
            b = b.strip()
            if not b or b.startswith("#") or re.fullmatch(r"\|[-| ]+\|", b) or "{{table:" in b:
                continue
            if b.startswith("|"):
                if re.match(r"\|\s*(Stage and filter|Source|Option|Scenario|Security area|Keyword|Block|Date|Criterion|Bavaria, cyber proxy|\s*\|)", b):
                    continue                               # header rows
                items = [b]
            else:
                items = _sentences(b)
            for s in items:
                text, keys = _render(s, kn, figs)
                out.append({"where": f"report {section}", "claim": text.replace("|", "/"), "keys": keys, "docs": docs})
    return out


def dashboard_claims(kn: dict) -> list[dict]:
    from streamlit.testing.v1 import AppTest
    app = REPO_ROOT / "app"
    sys.path.insert(0, str(app))
    out = []
    for view in sorted((app / "views").glob("*.py")):
        src = view.read_text(encoding="utf-8")
        docs = _docs_in(src) or ALL_EVIDENCE
        at = AppTest.from_file(str(view), default_timeout=180)
        at.run()
        page = f"dashboard {view.stem}"
        for el in list(at.markdown) + list(at.caption):
            for s in _sentences(el.value):
                if s.startswith("**Evidence:**") or s.startswith("Evidence:"):
                    continue
                out.append({"where": page, "claim": s.replace("|", "/"), "keys": [], "docs": docs})
        for m in at.metric:
            key = re.search(r"\(key: (\w+)", m.proto.help).group(1)
            out.append({"where": page, "claim": f"Metric '{m.label}': {m.value}", "keys": [key], "docs": docs})
    return out


def readme_claims() -> list[dict]:
    t = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    block = t[t.index("## Result"):t.index("## How the argument")]
    out = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("| ") and not re.fullmatch(r"\|[-| ]+\|", line) and not line.startswith("| |"):
            out.append({"where": "README Result", "claim": line.replace("|", "/").strip("/ "), "keys": [], "docs": ALL_EVIDENCE})
        elif line and not line.startswith(("|", "#", "---")):
            for s in _sentences(line):
                out.append({"where": "README Result", "claim": s, "keys": [], "docs": ALL_EVIDENCE})
    # sentences may span lines: merge the paragraph text instead of single lines
    paras = [p for p in re.split(r"\n\s*\n", block) if p.strip() and not p.strip().startswith(("|", "#", "---"))]
    out = [c for c in out if c["claim"].startswith(("Ranking", "Expected", "New to", "Regional", "Demand", "Labour",
                                                    "Faculty", "Resources", "Recommendation"))]
    for p in paras:
        for s in _sentences(p):
            out.append({"where": "README Result", "claim": s, "keys": [], "docs": ALL_EVIDENCE})
    seen, uniq = set(), []
    for c in out:
        if c["claim"] not in seen:
            seen.add(c["claim"])
            uniq.append(c)
    return uniq


def main() -> None:
    kn, figs = load_numbers(), figure_index()
    claims = report_claims(kn, figs) + dashboard_claims(kn) + readme_claims()
    lines = ["# Claim sheet for the independent review (generated)", "",
             f"Built by `python -m study_program_intelligence.report.claims` from the report source (docs/report/), the "
             f"dashboard (app/views/, as rendered) and the README Result block. {len(claims)} claims. Key numbers are "
             "already checked automatically against their source docs (reports/key_numbers.yaml, in_source_doc); the "
             "review judges whether each statement as a whole is supported by the evidence docs.", "",
             "| ID | Where | Claim | Key numbers (value; source doc) | Evidence docs to check |", "|---|---|---|---|---|"]
    for i, c in enumerate(claims, 1):
        keys = "<br>".join(f"{k} = {kn[k]['display']} ({kn[k]['source_doc'].replace('docs/', '')})" for k in dict.fromkeys(c["keys"]) if k in kn)
        docs = ", ".join(d.replace("docs/", "") for d in c["docs"]) if c["docs"] != ALL_EVIDENCE else "all evidence docs"
        lines.append(f"| C{i:03d} | {c['where']} | {c['claim']} | {keys} | {docs} |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    by = {}
    for c in claims:
        by[c["where"].split()[0]] = by.get(c["where"].split()[0], 0) + 1
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({len(claims)} claims: {by})")


if __name__ == "__main__":
    main()
