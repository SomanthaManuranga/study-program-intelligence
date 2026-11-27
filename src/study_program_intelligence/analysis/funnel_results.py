"""Copies the final tables of the data-driven funnel (Steps 1-8) into results/, the one data folder that is committed.

Run from the repository root after the funnel has run:

    python -m study_program_intelligence.analysis.funnel_results

data/ stays git-ignored (raw downloads, third-party PDFs, internal timetables). results/ holds only derived tables
and step summaries: no raw download, no module text of another university, no internal file. Every file is listed in
results/MANIFEST.csv with its step, rows, hash and the commit that produced it.
"""

from __future__ import annotations

import json
import shutil

import pandas as pd

from .funnel_common import INTERIM, REPO_ROOT
from .funnel_types import sha

RESULTS = REPO_ROOT / "results"
FILES = {  # step folder: (file in data/interim, what it holds)
    "step2_types": [("funnel2_types.csv", "programme types found in all offers (one row per type)"), ("funnel2_step2.json", "Step 2 summary")],
    "step3_screen": [("funnel2_screen.csv", "every unit (type x level) with the four screens, EMI score, competition and regional gap"),
                     ("funnel2_candidates.csv", "the primary list"), ("funnel2_step3.json", "Step 3 summary")],
    "step4_demand": [("funnel2_demand.csv", "student trend of every unit's subject pool"), ("funnel2_pools.csv", "the subject pools"), ("funnel2_step4.json", "Step 4 summary")],
    "step5_jobs": [("funnel2_labour.csv", "job-ad measure of every unit"), ("funnel2_job_counts.csv", "every job-ad count (keyword x region, 15 Nov 2026)"), ("funnel2_step5.json", "Step 5 summary")],
    "step6_new_students": [("funnel2_capture.csv", "first-years and students new to OTH of every unit (Huff model)"), ("funnel2_step6.json", "Step 6 summary")],
    "step7_feasibility": [("funnel2_shortlist.csv", "pre-gate score of every primary unit"), ("funnel2_gate_order.csv", "the order in which candidates were tried"),
                          ("funnel2_step7a.json", "pre-gate summary"), ("funnel2_reference_tries.csv", "the offers tried as reference curricula"),
                          ("funnel2_gate_walk.csv", "the walk down the gate list"), ("funnel2_rows_final.csv", "every marked module with its final verdict (no module text)"),
                          ("funnel2_gate_references.csv", "overlap and new teaching per reference handbook"), ("funnel2_gate.csv", "gate verdict per candidate"),
                          ("funnel2_step7.json", "Step 7 summary"),
                          ("pass1_funnel2_gate_references.csv", "first marking pass (sensitivity)"), ("pass2_funnel2_gate_references.csv", "second marking pass (sensitivity)")],
    "step8_decision": [("funnel2_rank_inputs.csv", "low / central / high of every input"), ("funnel2_rank.csv", "values, scores and probabilities in each decision set"),
                       ("funnel2_factorial.csv", "stress grid: winners by factor level"), ("funnel2_step8.json", "decision, sentences and sensitivities"),
                       ("funnel2_listspecs.csv", "list-changing specs (8b)"), ("funnel2_step8b.json", "8b summary"),
                       ("funnel2_gate_references_sens.csv", "second-handbook check: a plain Informatik bachelor (TH Ingolstadt)"),
                       ("funnel2_step7_sens.json", "second-handbook check summary")],
}


def main() -> None:
    if RESULTS.exists():
        shutil.rmtree(RESULTS)
    rows = []
    for folder, files in FILES.items():
        (RESULTS / folder).mkdir(parents=True)
        for name, what in files:
            src = INTERIM / name
            if not src.exists():
                raise SystemExit(f"{name} is missing: run the funnel first")
            dst = RESULTS / folder / name.replace("funnel2_", "")
            shutil.copyfile(src, dst)
            n = len(pd.read_csv(dst, low_memory=False)) if dst.suffix == ".csv" else None
            commit = json.loads(src.read_text(encoding="utf-8")).get("stamp", {}).get("commit") if src.suffix == ".json" else None
            rows.append({"file": dst.relative_to(RESULTS).as_posix(), "what": what, "rows": n, "sha256 (16)": sha(dst), "commit of the run": commit})
    pd.DataFrame(rows).to_csv(RESULTS / "MANIFEST.csv", index=False)
    print(f"{len(rows)} files in {RESULTS}")


if __name__ == "__main__":
    main()
