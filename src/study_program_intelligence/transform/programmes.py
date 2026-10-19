"""Turn the raw Studiensuche pages into one programme table.

Run from the repository root:

    python -m study_program_intelligence.transform.programmes

Input : data/raw/studiensuche/<query>/page_*.json  (+ configs/studiensuche.yaml)
Output: data/processed/programmes.csv        one row per programme offer (id)
        data/processed/programme_fields.csv  one row per (programme, study field, level)
        docs/programmes_summary.md            counts for the source register (committed)

One programme can appear in several study fields (e.g. Informatik and
Wirtschaftsinformatik). programmes.csv keeps it once; programme_fields.csv
keeps every field it was found in.

Re-scope (R4): `--set full` builds the same tables from the full catalogue harvest (configs/studiensuche_full.yaml,
data/raw/studiensuche_full) into programmes_full.csv, programme_fields_full.csv and docs/programmes_full_summary.md.
The default set (13 fields) is the baseline and is not changed.
"""

from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW = REPO_ROOT / "data" / "raw" / "studiensuche"
CONFIG = REPO_ROOT / "configs" / "studiensuche.yaml"
OUT = REPO_ROOT / "data" / "processed"
SUMMARY = REPO_ROOT / "docs" / "programmes_summary.md"

# Reference points for distances (OTH Amberg-Weiden campuses).
AMBERG = (49.4448, 11.8483)   # Kaiser-Wilhelm-Ring 23, Amberg (approximate)
WEIDEN = (49.6765, 12.1544)   # Hetzenrichter Weg 15, Weiden (approximate)

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def clean_text(raw: str | None) -> str:
    """Strip HTML tags and entities, collapse whitespace."""
    if not raw:
        return ""
    text = raw.replace("<br/>", " ").replace("<br>", " ").replace("</p>", " ").replace("</h4>", ": ")
    text = html.unescape(TAG_RE.sub(" ", text)).replace("­", "")
    return SPACE_RE.sub(" ", text).strip()


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def _label(obj) -> str | None:
    return obj.get("label") if isinstance(obj, dict) else None


def _id(obj):
    return obj.get("id") if isinstance(obj, dict) else None


def parse_item(item: dict) -> dict:
    sa = item.get("studienangebot", item)
    ort = sa.get("studienort") or {}
    loc = ort.get("location") or {}
    lat, lon = loc.get("lat"), loc.get("lon")
    modelle = [clean_text(m.get("label")) for m in sa.get("studienmodelle") or [] if isinstance(m, dict)]
    row = {
        "programme_id": str(sa.get("id")),
        "title": clean_text(sa.get("studiBezeichnung")),
        "degree": _label(sa.get("abschlussgrad")),
        "degree_id": _id(sa.get("abschlussgrad")),
        "study_type": _label(sa.get("studientyp")),          # grundstaendig / weiterfuehrend
        "study_type_id": _id(sa.get("studientyp")),
        "institution": (sa.get("studienanbieter") or {}).get("name"),
        "institution_id": (sa.get("studienanbieter") or {}).get("banId"),
        "institution_type": _label(sa.get("hochschulart")),
        "institution_type_id": _id(sa.get("hochschulart")),
        "city": ort.get("ort"),
        "postcode": ort.get("postleitzahl"),
        "state": ort.get("bundesland") or _label(sa.get("region")),
        "state_code": (sa.get("region") or {}).get("Key"),
        "country": ort.get("staat"),
        "lat": lat,
        "lon": lon,
        "study_form": _label(sa.get("studienform")),          # Vollzeit / Teilzeit / ...
        "study_models": "; ".join(m for m in modelle if m),    # dual, praxisintegrierend, ...
        "is_dual": any("dual" in m.lower() for m in modelle),
        "start": sa.get("studiBeginn"),
        "subjects": "; ".join(sa.get("studienfaecher") or []),
        "content": clean_text(sa.get("studiInhalt")),
    }
    if lat is not None and lon is not None:
        row["km_amberg"] = round(haversine_km(AMBERG, (lat, lon)), 1)
        row["km_weiden"] = round(haversine_km(WEIDEN, (lat, lon)), 1)
        row["km_oth"] = min(row["km_amberg"], row["km_weiden"])
    return row


def _level(st) -> str:
    """0 = first degree (bachelor level), 1 = further degree (master level)."""
    return {0: "first degree", 1: "further degree"}.get(st, "other")


def build(raw: Path = RAW, config: Path = CONFIG) -> tuple[pd.DataFrame, pd.DataFrame]:
    queries = {q["id"]: q for q in yaml.safe_load(config.read_text(encoding="utf-8"))["queries"]}
    rows, links = [], []
    for qid, q in queries.items():
        for page in sorted((raw / qid).glob("page_*.json")):
            payload = json.loads(page.read_text(encoding="utf-8"))
            for item in payload.get("items", []):
                row = parse_item(item)
                rows.append(row)
                links.append({
                    "programme_id": row["programme_id"],
                    "query_id": qid,
                    "field_key": q.get("field_key"),
                    "field_label": q.get("label", "").split(" (")[0],
                    "level": _level(q["params"].get("st", row["study_type_id"])),
                })
    progs = pd.DataFrame(rows).drop_duplicates("programme_id").reset_index(drop=True)
    fields = pd.DataFrame(links).drop_duplicates().reset_index(drop=True)
    n_fields = fields.groupby("programme_id")["field_label"].nunique().rename("n_fields")
    progs = progs.merge(n_fields, on="programme_id", how="left")
    progs["is_oth"] = progs["institution"].fillna("").str.contains("Amberg-Weiden", case=False)
    return progs, fields


def _only_oth(fields: pd.DataFrame) -> int:
    in_fields = set(fields.loc[fields["field_key"] != "OTH", "programme_id"])
    oth = set(fields.loc[fields["field_key"] == "OTH", "programme_id"])
    return len(oth - in_fields)


def summary(progs: pd.DataFrame, fields: pd.DataFrame, listings: int, full: bool = False) -> str:
    lines = [
        "# Programme catalogue summary" + (" (full catalogue)" if full else ""),
        "",
        f"Source: Hochschulkompass data via BA Studiensuche API; raw pages in data/raw/{'studiensuche_full' if full else 'studiensuche'}/ (local).",
        "Built by `python -m study_program_intelligence.transform.programmes" + (" --set full`." if full else "`."),
        "",
        f"- Listings retrieved: {listings:,}",
        f"- Unique programme offers: {len(progs):,}",
        f"- Institutions: {progs['institution'].nunique():,}",
        f"- With coordinates: {progs['lat'].notna().sum():,}",
        f"- OTH Amberg-Weiden offers in the catalogue: {int(progs['is_oth'].sum())}"
        f" (of which found only by the all-OTH query: {_only_oth(fields)})",
        "",
        "## Offers by study field and level",
        "",
        "| Study field | First degree | Further degree |",
        "| --- | --- | --- |",
    ]
    by_field = fields[fields["field_key"] != "OTH"]  # the OTH coverage query is not a study field
    pivot = by_field.pivot_table(index="field_label", columns="level", values="programme_id", aggfunc="nunique", fill_value=0)
    for field, r in pivot.sort_values("first degree", ascending=False).iterrows():
        lines.append(f"| {field} | {r.get('first degree', 0)} | {r.get('further degree', 0)} |")
    lines += ["", "## Offers within 100 km of an OTH campus", ""]
    near = progs[progs["km_oth"] <= 100]
    lines.append(f"{len(near):,} offers at {near['institution'].nunique()} institutions.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="programme table from the Studiensuche harvest")
    ap.add_argument("--set", choices=["baseline", "full"], default="baseline")
    full = ap.parse_args(argv).set == "full"
    raw = REPO_ROOT / "data" / "raw" / "studiensuche_full" if full else RAW
    config = REPO_ROOT / "configs" / "studiensuche_full.yaml" if full else CONFIG
    sfx = "_full" if full else ""
    progs, fields = build(raw, config)
    OUT.mkdir(parents=True, exist_ok=True)
    progs.to_csv(OUT / f"programmes{sfx}.csv", index=False, encoding="utf-8")
    fields.to_csv(OUT / f"programme_fields{sfx}.csv", index=False, encoding="utf-8")
    summary_path = REPO_ROOT / "docs" / f"programmes{sfx}_summary.md"
    summary_path.write_text(summary(progs, fields, len(fields), full), encoding="utf-8")
    print(f"{len(progs):,} unique programme offers from {len(fields):,} listings")
    print(f"OTH Amberg-Weiden offers: {int(progs['is_oth'].sum())}")
    print(f"Written: data/processed/programmes{sfx}.csv, data/processed/programme_fields{sfx}.csv, {summary_path.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
