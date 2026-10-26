"""Resource need of each level in professor-equivalents, and cost per expected first-year (configs/cost.yaml).

Run from the repository root (after report.handcheck_sheet and analysis.first_years):

    python -m study_program_intelligence.analysis.cost

One professor-equivalent of teaching = the legal load of 18 SWS per semester (AVBayHIG § 4 Abs. 1 Nr. 1) in both
semesters = 36 SWS-semesters a year. New modules and teaching assignments: ECTS x 0.8 SWS, taught once a year.
New professorships count 1 each; the lab engineer counts as one full-time position (headcount convention).
Robotics path B's new teaching comes from the hand check (report/handcheck_sheet.py, Soma's verdicts).
First-years: projected steady state (analysis/first_years.py), and without the trend projection (the model's base-year
level) as a check. Lab and equipment cost: not estimated.
Outputs: data/interim/cost.csv, reports/cost.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "cost.yaml"
FIRST_YEARS = REPO_ROOT / "data" / "interim" / "candidate_first_years.csv"
OUT = REPO_ROOT / "data" / "interim" / "cost.csv"
REPORT = REPO_ROOT / "reports" / "cost.md"


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def robotics_new_teaching() -> dict:
    """T and N of robotics path B after Soma's verdicts, and N above the strict cap."""
    from study_program_intelligence.report import handcheck_sheet as H
    cfg, hc, rule = H.config()
    r = H.f1_f4(H.verdict_table("robotics_b", cfg, hc), rule)
    return {"T": float(r["T"]), "N": float(r["N"]), "N above cap": float(r["N"]) - rule["rule"]["F2_max_N_ects"]["bachelor"]}


def prof_eq(cfg: dict, ects: float = 0.0, professorships: float = 0.0, lab_engineers: float = 0.0) -> float:
    per_year = cfg["teaching_load_sws_per_semester"] * cfg["semesters_per_year"]
    return ects * cfg["sws_per_ects"] / per_year + professorships + lab_engineers


def table(cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or config()
    rob = robotics_new_teaching()
    fy = pd.read_csv(FIRST_YEARS)
    steady = lambda cand, sc, col="gross": float(fy[(fy["candidate"] == cand) & (fy["scenario"] == sc)
                                                 & (fy["phase"] == "steady state")][col].iloc[0])
    rows = []
    for key, lv in cfg["levels"].items():
        new_mod = {"from_handcheck_excess": rob["N above cap"], "from_handcheck_N": rob["N"]}.get(lv.get("new_modules_ects"), 0.0)
        ta = {"from_handcheck_T": rob["T"]}.get(lv.get("teaching_assignments_ects"), lv.get("teaching_assignments_ects", 0.0))
        profs, lab = lv.get("new_professorships", 0), lv.get("lab_engineers", 0)
        pe_teach = prof_eq(cfg, new_mod + ta)
        total = prof_eq(cfg, new_mod + ta, profs, lab)
        all_teach = prof_eq(cfg, new_mod + ta + lv.get("new_modules_by_new_professors_ects", 0))   # like for like
        row = {"level": lv["label"], "new modules by existing professors (ECTS)": round(new_mod, 2),
               "teaching assignments (ECTS)": round(float(ta), 2), "new teaching (SWS a year)": round((new_mod + ta) * cfg["sws_per_ects"], 2),
               "new professorships": profs, "lab engineers": lab, "professor-equivalents, teaching": round(pe_teach, 3),
               "professor-equivalents, total": round(total, 3),
               "professor-equivalents, all new teaching (no positions)": round(all_teach, 3), "lab and equipment cost": "not estimated"}
        if lv.get("first_years"):
            c, lo = steady(lv["first_years"], "central"), steady(lv["first_years"], "low")
            row.update({"first-years steady state, central / low": f"{c} / {lo}",
                        "professor-equivalents per first-year, central": round(total / c, 3),
                        "professor-equivalents per first-year, low": round(total / lo, 3)})
            c0, lo0 = (steady(lv["first_years"], sc, "gross (model, base year)") for sc in ("central", "low"))
            row.update({"first-years without trend projection, central / low": f"{c0} / {lo0}",
                        "per first-year without projection, central": round(total / c0, 3),
                        "per first-year without projection, low": round(total / lo0, 3),
                        "all new teaching per first-year, central / low": f"{round(all_teach / c, 3)} / {round(all_teach / lo, 3)}",
                        "all new teaching per first-year without projection, central / low":
                            f"{round(all_teach / c0, 3)} / {round(all_teach / lo0, 3)}"})
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    t = table()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT, index=False)
    md = "\n".join(["| " + " | ".join(t.columns) + " |", "|" + "---|" * len(t.columns)]
                   + ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in t.itertuples(index=False)])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("# Cost in professor-equivalents (generated)\n\nConfig: configs/cost.yaml.\n\n" + md + "\n", encoding="utf-8")
    pd.set_option("display.width", 250)
    print(t.T.to_string())


if __name__ == "__main__":
    main()
