"""One-command pipeline (Step 54): raw data -> interim -> analysis reports -> key numbers -> figures -> report -> tests.

Run from the repository root with the venv active:

    python -m study_program_intelligence.pipeline              # rebuild everything from data/raw (no downloads)
    python -m study_program_intelligence.pipeline --ingest     # download first (cached files are kept)
    python -m study_program_intelligence.pipeline --list       # show the steps
    python -m study_program_intelligence.pipeline --from analysis.forecast   # resume at a step

Every step is the same `python -m ...` command as documented in the README, run in a subprocess and stopped at the
first failure. Before the run the manual inputs are checked; after it the new key numbers are compared with the
previous ones, so an unintended change is visible. The job-ad snapshot is never taken by default (it adds a dated
snapshot); use --snapshot on the snapshot dates. Outputs: reports/pipeline_log.md (steps, times, key-number changes)
and reports/pipeline_output.log (full console output).
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG = REPO_ROOT / "reports" / "pipeline_log.md"
OUT = REPO_ROOT / "reports" / "pipeline_output.log"
KEY_NUMBERS = REPO_ROOT / "reports" / "key_numbers.yaml"
P = "study_program_intelligence."

DOC_LISTS = [  # (config, out folder, manifest, pdf only)
    ("configs/competitor_modules.yaml", "data/raw/competitor modules", "docs/competitor_modules_manifest.json", True),
    ("configs/regional_documents.yaml", "data/raw/regional", "docs/regional_manifest.json", False),
    ("configs/labour_documents.yaml", "data/raw/labour", "docs/labour_manifest.json", True),
    ("configs/benchmark_documents.yaml", "data/raw/benchmarks", "docs/benchmark_manifest.json", False),
    ("configs/anchor_documents.yaml", "data/raw/anchors", "docs/anchor_manifest.json", True),
]

# (step name, stage, module, arguments)
INGEST = [("ingest.documents", "ingest", "ingest.documents", [])] + [
    (f"ingest.documents:{Path(c).stem}", "ingest", "ingest.documents",
     ["--config", c, "--out", o, "--manifest", m] + (["--pdf-only"] if pdf else [])) for c, o, m, pdf in DOC_LISTS
] + [("ingest.genesis", "ingest", "ingest.genesis", ["tables"]),
     ("ingest.studiensuche", "ingest", "ingest.studiensuche", ["harvest"])]
SNAPSHOT = [("ingest.jobsuche", "ingest", "ingest.jobsuche", ["snapshot"])]
BUILD = [
    ("transform.programmes", "transform", "transform.programmes", []),
    ("transform.modules", "transform", "transform.modules", []),
    ("transform.thm_modules", "transform", "transform.thm_modules", []),
    ("transform.school_leavers", "transform", "transform.school_leavers", []),
    ("analysis.first_look", "analysis", "analysis.first_look", []),
    ("analysis.trends", "analysis", "analysis.trends", []),
    ("analysis.theme_check:sample", "analysis", "analysis.theme_check", ["sample"]),   # only if the sheet is missing
    ("analysis.theme_check", "analysis", "analysis.theme_check", ["score"]),
    ("analysis.module_gaps", "analysis", "analysis.module_gaps", []),
    ("analysis.catchment:geo", "analysis", "analysis.catchment", ["geo"]),
    ("analysis.catchment:run", "analysis", "analysis.catchment", ["run"]),
    ("analysis.labour", "analysis", "analysis.labour", []),
    ("analysis.forecast", "analysis", "analysis.forecast", []),
    ("analysis.capture", "analysis", "analysis.capture", []),
    ("analysis.cannibalisation", "analysis", "analysis.cannibalisation", []),
    ("analysis.options", "analysis", "analysis.options", []),
    ("analysis.ranking", "analysis", "analysis.ranking", []),
    ("report.build", "report", "report.build", []),
    ("report.draft", "report", "report.draft", []),
    ("report.spotcheck", "report", "report.spotcheck", []),
]

# Inputs that no script can download (robots.txt, no API, or human work); see README "Manual downloads".
MANUAL = [
    ("data/raw/trends", "trends_*.csv", "Google Trends CSVs (docs/evidence_demand_trends.md)"),
    ("data/raw/oth modules", "*.pdf", "OTH module handbooks (OTH /fileadmin/ is disallowed for scripts)"),
]   # the hand-checked theme labels are committed (docs/theme_labels.csv), so they are not a manual input


# Steps that only run when their output is missing (name -> file). The labelling sheet is rebuilt from the catalogue
# with a fixed seed; it is never overwritten because the hand labels (docs/theme_labels.csv) are joined to its rows.
ONLY_IF_MISSING = {"analysis.theme_check:sample": REPO_ROOT / "data" / "interim" / "theme_labels.xlsx"}


def steps(args: argparse.Namespace) -> list[tuple]:
    s = (INGEST if args.ingest else []) + (SNAPSHOT if args.snapshot else []) + BUILD
    if args.start:
        names = [x[0] for x in s]
        if args.start not in names:
            sys.exit(f"Unknown step {args.start!r}; see --list")
        s = s[names.index(args.start):]
    return [x for x in s if x[0] not in (args.skip or [])]


def preflight(args: argparse.Namespace) -> list[str]:
    problems = []
    for folder, pattern, what in MANUAL:
        if not list((REPO_ROOT / folder).glob(pattern)):
            problems.append(f"missing manual input: {folder}/{pattern} - {what}")
    if args.ingest or args.snapshot:
        from .ingest.documents import load_env
        load_env()
        for var in ("GENESIS_TOKEN", "CONTACT_EMAIL"):
            if not os.environ.get(var):
                problems.append(f"missing {var} in .env (needed for downloads)")
    return problems


def _flat(path: Path) -> dict:
    if not path.exists():
        return {}
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {k: v["display"] for sec, items in d.items() if isinstance(items, dict) for k, v in items.items()
            if isinstance(v, dict) and "display" in v}


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rebuild all outputs from data/raw in one command.")
    ap.add_argument("--ingest", action="store_true", help="download the sources first (cached files are kept)")
    ap.add_argument("--snapshot", action="store_true", help="also take a dated job-ad snapshot (only on snapshot dates)")
    ap.add_argument("--from", dest="start", help="start at this step (see --list)")
    ap.add_argument("--skip", nargs="*", help="skip these steps")
    ap.add_argument("--no-tests", action="store_true", help="do not run the test suite at the end")
    ap.add_argument("--list", action="store_true", help="list the steps and exit")
    args = ap.parse_args(argv)
    plan = steps(args)
    if args.list:
        for name, stage, module, a in plan:
            print(f"{stage:<9} {name:<38} python -m {P}{module} {' '.join(a)}")
        return 0
    problems = preflight(args)
    if problems:
        print("Cannot start:\n  " + "\n  ".join(problems))
        return 2

    before = _flat(KEY_NUMBERS)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    rows, failed, t0 = [], None, time.time()
    with OUT.open("w", encoding="utf-8") as out:
        for i, (name, stage, module, a) in enumerate(plan, 1):
            cmd = [sys.executable, "-m", P + module, *a]
            print(f"[{i:>2}/{len(plan)}] {name} ...", end=" ", flush=True)
            if name in ONLY_IF_MISSING and ONLY_IF_MISSING[name].exists():
                print("skipped (output exists)")
                rows.append((stage, name, " ".join([f"python -m {P}{module}", *a]), "0", "skipped (output exists)"))
                continue
            out.write(f"\n===== {name}: {' '.join(cmd[1:])}\n")
            out.flush()
            t = time.time()
            r = subprocess.run(cmd, cwd=REPO_ROOT, stdout=out, stderr=subprocess.STDOUT)
            sec = time.time() - t
            # a download list exits with 1 when some documents could not be fetched (known gaps such as robots.txt
            # blocks or dead links, recorded in the manifest); that is not a reason to stop the rebuild
            gaps = stage == "ingest" and r.returncode == 1
            ok = r.returncode == 0 or gaps
            status = "ok, with gaps (see output log)" if gaps else ("ok" if ok else f"FAILED ({r.returncode})")
            print(f"{status} ({sec:.0f} s)")
            rows.append((stage, name, " ".join([f"python -m {P}{module}", *a]), f"{sec:.0f}", status))
            if not ok:
                failed = name
                break
        tests = "skipped"
        if failed is None and not args.no_tests:
            print("[tests] pytest ...", end=" ", flush=True)
            out.write("\n===== tests: pytest -q\n")
            out.flush()
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=REPO_ROOT, stdout=out, stderr=subprocess.STDOUT)
            tests = "passed" if r.returncode == 0 else f"FAILED ({r.returncode})"
            print(tests)

    after = _flat(KEY_NUMBERS)
    changed = [(k, before.get(k, "(new)"), v) for k, v in after.items() if before.get(k) != v]
    removed = [k for k in before if k not in after]
    lines = ["# Pipeline run (generated)", "",
             f"Run: {dt.datetime.now().isoformat(timespec='seconds')} · commit {git_commit()} · Python "
             f"{platform.python_version()} · {len(rows)} of {len(plan)} steps · total {time.time() - t0:.0f} s · tests: {tests}", "",
             "| Stage | Step | Command | Seconds | Status |", "|---|---|---|---|---|"]
    lines += [f"| {' | '.join(r)} |" for r in rows]
    lines += ["", f"## Key numbers compared with the previous run ({len(after)} now, {len(before)} before)", ""]
    if not before:
        lines.append("No previous key numbers to compare with.")
    elif not changed and not removed:
        lines.append("**All key numbers unchanged.**")
    else:
        lines += ["| Key | Before | After |", "|---|---|---|"] + [f"| {k} | {b} | {a} |" for k, b, a in changed]
        lines += [f"| {k} | removed | |" for k in removed]
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written: {LOG.relative_to(REPO_ROOT)}, {OUT.relative_to(REPO_ROOT)}")
    if before:
        print(f"Key numbers: {len(changed)} changed, {len(removed)} removed (of {len(before)}).")
    return 1 if failed or tests.startswith("FAILED") else 0


if __name__ == "__main__":
    sys.exit(main())
