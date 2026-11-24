"""Rule-set sweep: which programmes can plausibly win? Settings in configs/crosscheck_verification.yaml."""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import yaml

from . import engine as E

VCONF = E.REPO / "configs" / "crosscheck_verification.yaml"
VDIR = E.OUT / "verification"


def draw(rng, ranges, agreed):
    r = copy.deepcopy(agreed)
    for path, spec in ranges.items():
        sec, name = path.split(".")
        if isinstance(spec, list):
            val = spec[rng.integers(len(spec))]
        elif "uniform" in spec:
            val = round(float(rng.uniform(*spec["uniform"])), 2)   # 2 decimals: calibration cache stays small
        elif "dirichlet_around_agreed" in spec:
            w = np.array([agreed[sec]["weights"][c] for c in E.CRITERIA], float)
            v = rng.dirichlet(spec["dirichlet_around_agreed"] * w / w.sum())
            val = {c: round(float(x), 4) for c, x in zip(E.CRITERIA, v)}
        r[sec][name] = val
    r["step7_ranking"]["mc_draws"] = 200          # P(first) is not used here; the winner is the top score
    return r


def rule_sets():
    conf = yaml.safe_load(VCONF.read_text())["sweep"]
    agreed = E.agreed_rules()
    rng = np.random.default_rng(conf["seed"])
    return conf, [draw(rng, conf["ranges"], agreed) for _ in range(conf["runs"])]


def chunk(start: int, stop: int):
    """Evaluate rule sets [start, stop) and save them (the device shell stops long jobs)."""
    conf, sets = rule_sets()
    prep = E.prepare()
    out = []
    for i in range(start, min(stop, len(sets))):
        res = E.run(prep, sets[i])
        k = res["kinds"]
        out.append({"run": i, "winners": res["winners"], "eligible": k[k.eligible].kind.tolist()})
    VDIR.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(out, VDIR / f"sweep_part_{start:05d}.pkl")
    return len(out)


def combine():
    conf, sets = rule_sets()
    parts = [x for p in sorted(VDIR.glob("sweep_part_*.pkl")) for x in pd.read_pickle(p)]
    assert sorted(x["run"] for x in parts) == list(range(conf["runs"])), "missing sweep parts"
    n = conf["runs"]
    W = pd.DataFrame([{"run": x["run"], "level": l, "winner": w} for x in parts for l, w in x["winners"].items()])
    L = pd.DataFrame([{"run": x["run"], "kind": k} for x in parts for k in x["eligible"]])
    share = W.groupby(["level", "winner"]).size().div(n).rename("win_share").reset_index().sort_values(
        ["level", "win_share"], ascending=[True, False])
    eshare = L.groupby("kind").size().div(n).rename("eligible_share").reset_index().sort_values(
        "eligible_share", ascending=False)
    share.to_csv(VDIR / "sweep_winners.csv", index=False)
    eshare.to_csv(VDIR / "sweep_eligible.csv", index=False)
    runs = pd.DataFrame([{"run": i, **{f"{s}.{n_}": (str(v) if isinstance(v, dict) else v)
                                       for s, d in r.items() for n_, v in d.items()}} for i, r in enumerate(sets)])
    runs.merge(W.pivot(index="run", columns="level", values="winner").add_prefix("winner_"), left_on="run",
               right_index=True).to_csv(VDIR / "sweep_runs.csv", index=False)
    return share, eshare


if __name__ == "__main__":
    import sys
    if sys.argv[1] == "chunk":
        print(chunk(int(sys.argv[2]), int(sys.argv[3])))
    else:
        s, e = combine()
        print(s.to_string(index=False))
        print(e.head(45).to_string(index=False))
