"""Published first-years of dedicated cyber bachelors elsewhere (data-sufficiency audit G3, plausibility check only).

Run from the repository root (after the documents in configs/intake_benchmark_documents.yaml are downloaded):

    python -m study_program_intelligence.analysis.intake_benchmark

Not a new anchor: both universities that publish per-programme figures are research universities with large security
institutes, not HAW peers. The figures only show whether the capture anchors (THI capacity 25, TH Deggendorf "about
60" from one student review) lie in a plausible range.
Ruhr-Universität Bochum: first-years in the 1st subject semester by degree (columns: Bachelor 1-Fach, ..., Summe).
Universität des Saarlandes: Tabelle 1, per subject and degree: students, women, 1st subject semester.
Output: reports/intake_benchmark.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pypdf

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW = REPO_ROOT / "data" / "raw" / "intake_benchmark"
REPORT = REPO_ROOT / "reports" / "intake_benchmark.md"


def _pdf(stem: str) -> Path:
    return next(RAW.glob(f"{stem}*.pdf"))


def bochum() -> list[dict]:
    rows = []
    for p in pypdf.PdfReader(_pdf("rub_firstyears_2024")).pages:
        for line in (p.extract_text(extraction_mode="layout") or "").splitlines():
            m = re.match(r"^\s*(IT-Sicherheit / [^\d]+?)\s{2,}([\d\s]+)$", line)
            if m:
                nums = [int(x) for x in m.group(2).split()]
                name = m.group(1).strip()
                # Informationstechnik: Bachelor 1-Fach, Master 1-Fach, other, total; Netze und Systeme: Master only
                ba = nums[0] if len(nums) > 2 else 0
                rows.append({"university": "Ruhr-Universität Bochum", "programme": name, "term": "2024 (1st subject semester)",
                             "bachelor first-years": ba, "all degrees": nums[-1]})
    return rows


def saarland() -> list[dict]:
    rows = []
    for stem, term in (("uds_faecher_ws2024", "WS 2024/25"), ("uds_faecher_ws2025", "WS 2025/26")):
        seen = set()
        for p in pypdf.PdfReader(_pdf(stem)).pages:
            for line in (p.extract_text() or "").splitlines():
                m = re.match(r"^(Cybersicherheit|Cybersecurity \(engl\.\)) Bachelor KB ([\d ]+)$", line.strip())
                if not m or m.group(1) in seen:
                    continue
                nums = [int(x) for x in m.group(2).split()]
                if len(nums) != 5:          # Tabelle 1 rows: students, women, 1st subject semester, ...; Tabelle 2 has 15
                    continue
                seen.add(m.group(1))
                rows.append({"university": "Universität des Saarlandes", "programme": f"{m.group(1)} B.Sc.", "term": term,
                             "bachelor first-years": nums[2], "all degrees": nums[2], "students": nums[0]})
    return rows


def main() -> None:
    rows = bochum() + saarland()
    cols = ["university", "programme", "term", "bachelor first-years", "all degrees"]
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + \
         ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(["# Published first-years of dedicated cyber programmes (generated)", "",
                                 "Plausibility check only, not an anchor (research universities, not HAW peers). Sources: "
                                 "configs/intake_benchmark_documents.yaml, docs/intake_benchmark_manifest.json.", "", *md, ""]),
                      encoding="utf-8")
    for r in rows:
        print(r)
    print(f"\nWritten: {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
