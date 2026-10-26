"""Hand check part 1 (docs/criteria_handcheck_part1.md): recorded verdicts, sheet row numbers, quoted pages,
sensitivity completeness."""

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")
SOMA_PART1 = {1: "confirm", 2: "confirm", 3: "open", 4: "confirm", 5: "confirm", 6: "confirm", 7: "open", 8: "confirm",
              9: "open", 10: "confirm", 11: "reject", 12: "confirm", 13: "confirm", 14: "confirm", 15: "confirm",
              16: "confirm", 17: "confirm"}   # Soma's message, hand check part 1
PDFS = {"ref_visual_computing_coburg.pdf": "data/raw/references/ref_visual_computing_coburg.pdf",
        "oth_hb_ii_mi_ba.pdf": "data/raw/oth handbooks 2026/oth_hb_ii_mi_ba.pdf",
        "hske_ba_robotik.pdf": "data/raw/anchors/hske_ba_robotik.pdf",
        "Künstliche Intelligenz (B.Sc.).pdf": "data/raw/oth modules/Künstliche Intelligenz (B.Sc.).pdf",
        "oth_hb_ei_ba_2022.pdf": "data/raw/oth handbooks 2026/oth_hb_ei_ba_2022.pdf",
        "oth_hb_iki_ba.pdf": "data/raw/oth handbooks 2026/oth_hb_iki_ba.pdf"}


def sheet_cfg():
    return yaml.safe_load((REPO / "configs" / "handcheck_sheet.yaml").read_text(encoding="utf-8"))


def test_recorded_verdicts_match_somas_list_row_by_row():
    dec = sheet_cfg()["decisions"]
    assert {r: d["decision"] for r, d in dec.items()} == SOMA_PART1


def test_yaml_rows_are_1_to_17_without_gaps():
    rows = sorted(m["row"] for c in sheet_cfg()["candidates"].values() for m in c["modules"].values())
    assert rows == list(range(1, 18))


@needs("docs/handcheck_sheet.md")
def test_sheet_row_numbers_and_decisions_match_the_yaml():
    cfg = sheet_cfg()
    by_row = {m["row"]: mod for c in cfg["candidates"].values() for mod, m in c["modules"].items()}
    lines = [l for l in (REPO / "docs" / "handcheck_sheet.md").read_text(encoding="utf-8").splitlines() if re.match(r"^\| \d+ \|", l)]
    assert len(lines) == 17
    for l in lines:
        cells = [c.strip() for c in l.strip("|").split("|")]
        row, module, decision = int(cells[0]), cells[1], cells[-1]
        assert by_row[row] == module, row
        assert decision.split(":")[0] == cfg["decisions"][row]["decision"], row


@needs(*PDFS.values())
def test_every_quote_in_the_open_rows_doc_is_on_its_stated_page():
    import pypdf
    text = (REPO / "docs" / "handcheck_open_rows.md").read_text(encoding="utf-8")
    quotes = re.findall(r"„(.+?)“\s*\[([^\]]+?) p\. (\d+)\]", text, re.S)   # also quotes that wrap a line
    assert len(quotes) == text.count("„") - text.count("„Zufallsvektoren")
    comp = lambda s: re.sub(r"[^a-z0-9äöüß]", "", s.lower())
    pages = {}
    for q, f, p in quotes:
        if f not in pages:
            pages[f] = [comp(x.extract_text() or "") for x in pypdf.PdfReader(REPO / PDFS[f]).pages]
        assert comp(q) in pages[f][int(p) - 1], (f, p, q[:60])


@needs("data/interim/feasibility_modules.csv", "data/interim/feasibility_handcheck_candidates.csv")
def test_sensitivity_flips_every_row_once_and_matches_the_doc():
    from study_program_intelligence.report import handcheck_sheet as H
    cfg, hc, rule = H.config()
    t = H.sensitivity(cfg, hc, rule)
    assert sorted(t["#"]) == list(range(1, 18))
    assert set(t["candidate"]) == {"arvr", "robotics_b"} and t["other candidate"].str.endswith("no effect").all()
    doc = (REPO / "docs" / "evidence_tie_break.md").read_text(encoding="utf-8")
    assert H._md(t) in doc                                    # the doc shows the current table
    flips = dict(zip(t["#"], t["flips the gate"]))
    assert flips[6] == "no" and flips[9] == "yes" and flips[3] == "yes" and flips[7] == "yes"
