"""School leavers with a university entrance qualification by Bavarian county, 2013/14-2023/24 (Step 42).

Run from the repository root:

    python -m study_program_intelligence.transform.school_leavers

Source: Bayerisches Landesamt für Statistik, Statistische Berichte B I/II 1 j "Bayerische Schulen - Eckzahlen
sämtlicher Schularten nach kreisfreien Städten und Landkreisen", Tabelle 5 (leavers from general and vocational
schools by general-education qualification and county); one PDF per year in data/raw/regional (report YYYY =
leavers of school year (YYYY-1)/YYYY). Counts are by SCHOOL location, not by residence.

Parsing: pypdf layout text; only the "zus." (total) rows. Numbers use a space as thousands separator and columns
are separated by spaces as well, so each row is split into numbers by the table's own arithmetic: the grouping
whose general-school and vocational-school totals both equal the sum of their parts. Rows are mapped to counties
by the official order (Regierungsbezirk, then county key), and checked: counties sum to their Bezirk, Bezirke to
Bavaria. Columns until 2022: general schools incl. "mit Fachhochschulreife"; from 2023 without it.
Output: data/interim/school_leavers_by.csv
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd
import pypdf

from ..analysis.catchment import counties

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW = REPO_ROOT / "data" / "raw" / "regional"
OUT = REPO_ROOT / "data" / "interim" / "school_leavers_by.csv"
YEARS = [2014, 2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024]  # report years; 2019 edition not in the archive
BEZIRKE = ["Oberbayern", "Niederbayern", "Oberpfalz", "Oberfranken", "Mittelfranken", "Unterfranken", "Schwaben"]
COLS_13 = ["gen_total", "gen_none", "gen_ms", "gen_mittel", "gen_fhr", "gen_ahr",
           "voc_total", "voc_none", "voc_ms", "voc_mittel", "voc_fhr", "voc_hr", "voc_no_gen"]
COLS_12 = [c for c in COLS_13 if c != "gen_fhr"]


def _pieces(t: str, max_cuts: int):
    """Ways to cut a digit token into pieces (a glued token holds the end of one number and the start of the next)."""
    yield [t]
    if max_cuts:
        for k in range(1, len(t)):
            for rest in _pieces(t[k:], max_cuts - 1):
                yield [t[:k]] + rest


def _numbers(tokens: list[str], n: int, max_cuts: int = 3) -> list[list[int]]:
    """Group tokens (digit groups, '-', '.') into n numbers so that both subtotals add up.
    Editions sometimes glue numbers ("9 04718 694" = 9 047 | 18 694; "663 438 982" = 663 | 4 | 38 982), so digit
    tokens may be cut; a piece either starts a number (1-3 digits, no leading zero) or continues one (exactly 3
    digits). Fewest cuts first; only a split where both subtotals add up is accepted."""
    tok = []
    for t in tokens:  # regular glue first: a token longer than 3 digits = end of a number (3 digits) + more
        t = "0" if t in ("-", ".", "x") else t
        while re.fullmatch(r"\d{4,}", t):
            tok.append(t[:3])
            t = t[3:]
        tok.append(t)
    gen_parts = 4 if n == 12 else 5

    def ok(g: list[int]) -> bool:
        gen, voc = g[: gen_parts + 1], g[gen_parts + 1:]
        return gen[0] == sum(gen[1:]) and voc[0] == sum(voc[1:])

    def place(pcs: list[str], nums: tuple[str, ...]):
        """All ways to attach the pieces of one token: each continues the last number (3 digits) or starts one."""
        if not pcs:
            yield nums
            return
        p, rest = pcs[0], pcs[1:]
        if nums and re.fullmatch(r"\d{3}", p):
            yield from place(rest, nums[:-1] + (nums[-1] + p,))
        if re.fullmatch(r"0|[1-9]\d{0,2}", p) and len(nums) < n:
            yield from place(rest, nums + (p,))

    def search(i: int, nums: tuple[str, ...], cuts: int):
        if i == len(tok):
            if len(nums) == n and ok([int(x) for x in nums]):
                yield [int(x) for x in nums]
            return
        for pcs in _pieces(tok[i], cuts):
            for nxt in place(pcs, nums):
                yield from search(i + 1, nxt, cuts - (len(pcs) - 1))

    for c in range(max_cuts + 1):  # all valid splits at the smallest number of extra cuts
        found = {tuple(g) for g in search(0, (), c)}
        if found:
            return [list(g) for g in sorted(found)]
    return []


def parse(year: int) -> pd.DataFrame:
    logging.disable(logging.WARNING)
    r = pypdf.PdfReader(RAW / f"by_eckzahlen_schulen_{year}.pdf")
    start = next(i for i in range(100, len(r.pages)) if re.search(r"(?<!Noch: )Tabelle 5\.", r.pages[i].extract_text() or ""))
    n = 13 if year <= 2022 else 12
    rows = []
    for i in range(start, len(r.pages)):
        for line in (r.pages[i].extract_text(extraction_mode="layout") or "").splitlines():
            m = re.match(r"^(.*?)\s*(zus\.|insges\.)\s*([\d\-.].*)$", line)  # 2014: "insges.176 512" (no space)
            if not m:
                continue
            options = _numbers(re.findall(r"\d+|[-.x]", m.group(3)), n)  # "-14 405": a dash glued to a number
            if not options:
                raise ValueError(f"{year} p{i + 1}: cannot split row {line!r}")
            rows.append({"label": m.group(1).strip(), "options": options})
    cols = COLS_13 if n == 13 else COLS_12
    d = pd.DataFrame([{"label": r["label"], "n_options": len(r["options"]), **dict(zip(cols, r["options"][0]))} for r in rows])
    d.attrs["options"] = [[dict(zip(cols, o)) for o in r["options"]] for r in rows]
    if "gen_fhr" not in d:
        d["gen_fhr"] = 0
    return d


def assign(d: pd.DataFrame, year: int, geo: pd.DataFrame) -> pd.DataFrame:
    """Map rows to Bavaria / Bezirk / county by the official order. Rows with several valid splits are resolved
    by the next level: the combination where the counties sum to their Bezirk (and the Bezirke to Bavaria)."""
    from itertools import product
    by = geo[geo["land"] == "09"].sort_values("county")
    order = [("Bayern", "09")]
    for k, name in enumerate(BEZIRKE, 1):
        order.append((name, f"09{k}"))
        order += [(c.county_name, c.county) for c in by[by["county"].str[2] == str(k)].itertuples()]
    if len(d) != len(order):
        raise ValueError(f"{year}: {len(d)} rows, expected {len(order)}")
    opts = d.attrs["options"]
    d = d.assign(area=[o[0] for o in order], key=[o[1] for o in order], year=year)
    val = COLS_13
    fill = lambda o: pd.Series({c: o.get(c, 0) for c in val})
    chosen = {}
    for k in range(1, 8):
        idx_b = d.index[d["key"] == f"09{k}"][0]
        idx_c = list(d.index[(d["key"].str.len() == 5) & (d["key"].str[2] == str(k))])
        for ob in opts[idx_b]:
            hit = next((combo for combo in product(*[opts[i] for i in idx_c])
                        if (sum((fill(o) for o in combo), pd.Series(0, index=val)) == fill(ob)).all()), None)
            if hit is not None:
                chosen[idx_b] = ob
                chosen.update(dict(zip(idx_c, hit)))
                break
        else:
            raise ValueError(f"{year}: counties do not sum to {BEZIRKE[k - 1]} for any valid split")
    tot = next((o for o in opts[0] if (sum((fill(chosen[i]) for i in chosen if d.at[i, "key"].__len__() == 3),
                                            pd.Series(0, index=val)) == fill(o)).all()), None)
    if tot is None:
        raise ValueError(f"{year}: Bezirke do not sum to Bavaria")
    chosen[0] = tot
    for i, o in chosen.items():
        for c in val:
            d.at[i, c] = o.get(c, 0)
    d["resolved_by_sums"] = d["n_options"] > 1
    return d


def main() -> None:
    geo = counties()
    out = []
    for y in YEARS:
        d = assign(parse(y), y, geo)
        out.append(d)
        b = d.iloc[0]
        print(f"{y}: {len(d)} rows, sums ok | Bavaria: Gymnasium Abitur {b.gen_ahr:,}, FOS/BOS FHR {b.voc_fhr:,} + HR {b.voc_hr:,}, "
              f"general-school FHR {b.gen_fhr:,}")
    res = pd.concat(out, ignore_index=True)
    res["school_year"] = res["year"].map(lambda y: f"{y - 1}/{str(y)[2:]}")
    res["abitur_gym"] = res["gen_ahr"]
    res["fos_bos"] = res["voc_fhr"] + res["voc_hr"]
    res["hzb_total"] = res["gen_ahr"] + res["gen_fhr"] + res["voc_fhr"] + res["voc_hr"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT, index=False)
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({len(res)} rows)")


if __name__ == "__main__":
    main()
