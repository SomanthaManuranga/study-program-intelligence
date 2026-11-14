"""Module texts and vectors of the funnel, and the neutral matching threshold (docs/criteria_funnel_step1b.md).

Run from the repository root:

    python -m study_program_intelligence.analysis.funnel_modules

vectors() is the one text preparation for module matching: Step 7 uses it for the reference curricula, and the
threshold is calibrated with it. The calibration reads EMI's own handbooks only (data/interim/modules_emi_2026.csv):
a module that appears under the same title in two handbooks, with texts that are not copies, is a true match; the
hardest wrong match is the most similar module of another handbook whose title shares no content word.
Outputs: data/interim/funnel2_threshold.json, reports/funnel2/step1b_threshold.md.
"""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, run_stamp
from .module_gaps import centre, clean, embed, youden

EMI_MODULES = INTERIM / "modules_emi_2026.csv"
OUT = INTERIM / "funnel2_threshold.json"
REPORT = REPORTS / "step1b_threshold.md"
COPY_JACCARD = 0.9          # two texts sharing at least this share of their words are one copied description
BOOTSTRAP, SEED = 1000, 42
FORMER = 0.285              # calibrated on the baseline's cybersecurity and robotics references; kept as a stress value
GENERIC = set("""grundlagen einfuehrung einfuhrung introduction basics fundamentals praktikum praxis practical projekt project projektarbeit
    modul module seminar vorlesung uebung lecture ausgewaehlte selected kapitel topics themen angewandte applied advanced fortgeschrittene
    und and der die das des for fuer von with mit zur zum the wahlpflichtmodul wahlpflichtfach teil part""".split())


def norm_title(t: str) -> str:
    t = re.sub(r"\(.*?\)", " ", str(t).lower())
    t = t.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def content_words(title: str) -> frozenset[str]:
    return frozenset(w for w in norm_title(title).split() if len(w) >= 3 and not w.isdigit() and w not in GENERIC)


def cleaned(d: pd.DataFrame) -> pd.Series:
    return pd.Series([clean(t if isinstance(t, str) else "", ti) for t, ti in zip(d["text"], d["title"])], index=d.index)


def vectors(d: pd.DataFrame, handbook: str = "source_file") -> np.ndarray:
    """Encoder vectors of the cleaned module texts, centred per handbook and normalised. Used by the calibration and by Step 7."""
    return centre(embed(cleaned(d).tolist()), d[handbook])


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-zäöüß]{3,}", text.lower()))


def pair_values(d: pd.DataFrame, s: np.ndarray) -> tuple[pd.DataFrame, dict]:
    """One row per anchor module: its positive value (best same-title partner that is not a copy) and its negative value
    (best module of another handbook whose title shares no content word). d has a default index matching s."""
    nt = d["title"].map(norm_title)
    cw = d["title"].map(content_words)
    txt = cleaned(d).map(words)
    file, prog = d["source_file"].to_numpy(), d["programme_id"].to_numpy()
    pairs = copies = 0
    partners: dict[int, list[int]] = {}
    for _, idx in nt.groupby(nt).groups.items():
        idx = list(idx)
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                i, j = idx[a], idx[b]
                if file[i] == file[j] or prog[i] == prog[j]:
                    continue
                pairs += 1
                jac = len(txt[i] & txt[j]) / max(1, len(txt[i] | txt[j]))
                if jac >= COPY_JACCARD:
                    copies += 1
                    continue
                partners.setdefault(i, []).append(j)
                partners.setdefault(j, []).append(i)
    rows, no_words = [], 0
    for i, ps in sorted(partners.items()):
        pos = float(max(s[i, j] for j in ps))
        if cw[i]:
            other = [j for j in d.index if file[j] != file[i] and not (cw[i] & cw[j])]
            neg = float(max(s[i, j] for j in other)) if other else float("nan")
        else:                                       # a title made of generic words only: the rule for the negative cannot be applied
            neg, no_words = float("nan"), no_words + 1
        rows.append({"module": i, "title": d.at[i, "title"], "handbook": d.at[i, "programme_id"], "positive": pos, "negative": neg})
    return pd.DataFrame(rows), {"same_title_pairs": pairs, "copies_left_out": copies, "anchors": len(rows), "anchors_without_content_word": no_words}


def threshold_of(v: pd.DataFrame) -> tuple[float, float, float, float]:
    return youden(v["positive"].dropna().to_numpy(), v["negative"].dropna().to_numpy())


def calibrate_neutral() -> dict:
    d = pd.read_csv(EMI_MODULES, low_memory=False).reset_index(drop=True)
    v = vectors(d)
    values, counts = pair_values(d, v @ v.T)
    tau, tpr, fpr, auc = threshold_of(values)
    rng = np.random.default_rng(SEED)
    boot = []
    for _ in range(BOOTSTRAP):
        sample = values.iloc[rng.integers(0, len(values), len(values))]
        if sample["positive"].notna().sum() and sample["negative"].notna().sum():
            boot.append(threshold_of(sample)[0])
    pos, neg = values["positive"].dropna(), values["negative"].dropna()
    at = lambda t: {"tpr": round(float((pos >= t).mean()), 2), "fpr": round(float((neg >= t).mean()), 2)}
    return {"value": round(tau, 3), "tpr": round(tpr, 2), "fpr": round(fpr, 2), "auc": round(auc, 3),
            "positives": int(len(pos)), "negatives": int(len(neg)), **counts,
            "bootstrap_interval": [round(float(np.percentile(boot, 2.5)), 3), round(float(np.percentile(boot, 97.5)), 3)], "bootstrap_resamples": len(boot),
            "positive_quartiles": [round(float(x), 3) for x in pos.quantile([0.25, 0.5, 0.75])],
            "negative_quartiles": [round(float(x), 3) for x in neg.quantile([0.25, 0.5, 0.75])],
            "former_value": FORMER, "former_value_on_this_set": at(FORMER), "weak": bool(auc < 0.70),
            "modules_read": len(d), "handbook_files": int(d["source_file"].nunique()), "source": EMI_MODULES.relative_to(REPO_ROOT).as_posix()}


def main() -> None:
    stamp = run_stamp()
    r = {"stamp": stamp, **calibrate_neutral()}
    OUT.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Funnel step 1b: neutral matching threshold (generated)", "",
             f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}. Source: {r['source']} only "
             f"({r['modules_read']} modules, {r['handbook_files']} handbook files).", "",
             f"- Same-title pairs across different handbooks: {r['same_title_pairs']}; copies left out: {r['copies_left_out']}; anchors: {r['anchors']} "
             f"({r['anchors_without_content_word']} without a content word in the title, so without a negative value).",
             f"- Positive values: {r['positives']} (quartiles {r['positive_quartiles']}); negative values: {r['negatives']} (quartiles {r['negative_quartiles']}).",
             f"- **Threshold (Youden): {r['value']}**; true-positive rate {r['tpr']}, false-positive rate {r['fpr']}, AUC {r['auc']}"
             f"{' (WEAK: below 0.70)' if r['weak'] else ''}.",
             f"- Bootstrap interval of the threshold ({r['bootstrap_resamples']} resamples): {r['bootstrap_interval'][0]} to {r['bootstrap_interval'][1]}.",
             f"- The former value {r['former_value']} on this set: true-positive rate {r['former_value_on_this_set']['tpr']}, false-positive rate {r['former_value_on_this_set']['fpr']}."]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
