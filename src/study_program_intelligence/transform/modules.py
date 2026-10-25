"""One module table from all module handbooks (competitors + EMI), Step 40.

Run from the repository root:

    python -m study_program_intelligence.transform.modules

Method (decision log 2026-10-17)
- Text per PDF page via pypdf. Lines repeated on many pages (headers/footers) are removed.
- Module list = the handbook's table of contents (TOC): titles in order; section headings
  are dropped by EXCLUDE. TOC page numbers are NOT used (several OTH handbooks restart
  numbering), so each title is searched forward in the body as a heading line.
- Module text = from its heading to the next module's heading.
- ECTS: first credit value near the heading; semester: first "N. Semester" style hit.
- Aalen (module lists) and TH Mannheim (programme page CSV) give names only (text empty).
Outputs: data/interim/modules.csv, reports/modules_check.md.

Re-scope (week 1): `--set emi2026` parses the CURRENT handbooks of all EMI programmes (configs/oth_handbooks_documents.yaml,
data/raw/oth handbooks 2026) into data/interim/modules_emi_2026.csv and reports/modules_emi_2026_check.md, for the
feasibility gate and the recombination step. The default set (competitors + earlier EMI copies) is the baseline and is
not changed.
"""

from __future__ import annotations

import csv
import random
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import pypdf

REPO_ROOT = Path(__file__).resolve().parents[3]
COMP = REPO_ROOT / "data" / "raw" / "competitor modules"
OTH = REPO_ROOT / "data" / "raw" / "oth modules"
OUT = REPO_ROOT / "data" / "interim" / "modules.csv"
REPORT = REPO_ROOT / "reports" / "modules_check.md"
SEED = 20261017
SHORT = 200  # characters; a module text below this counts as short

EXCLUDE = re.compile(
    r"^(\d+(\.\d+)*\.?\s|inhalt|table of content|historie|vorbemerk|preliminary|studienplan|studiengangsaufbau|"
    r"modulbeschreibung|module descriptions|übersicht|einführung$|einführende|glossar|index$|anhang|schlussbemerkung|"
    r"studienabschnitt|\d\.\s*semester|semester \d|pflichtmodule|wahlpflichtmodule|wahlmodule|basismodule|"
    r"required modules|elective modules|full time|part time|vertiefungsmodule|lehrveranstaltungsformen|"
    r"inhalt des studiengangs|aufbau und struktur|zielsetzung|zulassungsvoraussetzungen|zielgruppe|"
    r"interdisziplinäre wahlpflichtmodule|fachwissenschaftliche wahlpflichtmodule|leistungsnachweise|literatur$|"
    r"modulübersicht|vertiefungs\s*-?\s*und|curriculumsübersicht|studienverlaufsplan|\.+$)", re.I)


@dataclass
class Handbook:
    file: Path
    programme_id: str
    institution: str
    level: str
    toc_pages: list[int]
    toc_style: str = "dotted"  # dotted | tabbed | code
    programmes: dict[str, str] = field(default_factory=dict)  # section keyword -> programme_id (joint handbooks)
    exclude: str = ""  # extra regex for TOC lines to drop
    label: str = ""  # per-module field label; a 2nd one inside a module = a module missing from the TOC
    unordered: bool = False  # TOC order differs from body order: search missed titles again from the body start
    strict_ects: bool = False  # ignore numbers that are part of a code such as "3.3.4" (EMI 2026 set)
    plan_pages: list[int] = field(default_factory=list)  # study-plan pages with "ID code title SWS ECTS ..." rows
    ects_rule: str = ""  # "sum_lp": credits split by teaching form ("Vorlesung: 2 SWS 3 LP Praktikum: 2 SWS 2 LP") -> sum
    code_re: str = r"[BM]-CY-\d+"  # module code at the start of a "code" style TOC line
    body_prefix: str = ""  # regex stripped from body lines before matching headings ("103 Thesis" -> "Thesis")
    code_page: bool = False  # "code" TOC lines end with a page number ("101 - Computational Thinking 6")
    heading_first: bool = False  # a module heading opens a page (FH Dortmund: one module starts per page)


HANDBOOKS = [
    Handbook(COMP / "fau_ba_informatik_it_sicherheit.pdf", "fau_ba_its", "FAU Erlangen-Nürnberg", "BA", [1, 2]),
    Handbook(COMP / "thi_ba_cybersicherheit.pdf", "thi_ba_csi", "TH Ingolstadt", "BA", [2, 3]),
    Handbook(COMP / "thi_ma_cloud_applications_security_engineering.pdf", "thi_ma_cse", "TH Ingolstadt", "MA", [2]),
    Handbook(COMP / "deg_ba_cyber_security.pdf", "deg_ba_cy", "TH Deggendorf", "BA", [2, 3], "code"),
    Handbook(COMP / "deg_ma_cyber_security.pdf", "deg_ma_cy", "TH Deggendorf", "MA", [2]),
    Handbook(COMP / "thws_ba_informationssicherheit.pdf", "thws_ba_is", "THWS Würzburg-Schweinfurt", "BA", [2, 3]),
    Handbook(COMP / "hdbw_ma_cyber_security.pdf", "hdbw_ma_cs", "HDBW München", "MA", [2]),
    Handbook(OTH / "industrie-40-informatik.pdf", "oth_ba_ii|oth_ba_mi", "OTH Amberg-Weiden", "BA", [2, 3],
             programmes={"Industrie-4.0-Informatik": "oth_ba_ii", "Medieninformatik": "oth_ba_mi"}, label="Modul-ID"),
    Handbook(OTH / "Elektro- und Informationstechnik (B.Eng.).pdf", "oth_ba_eit", "OTH Amberg-Weiden", "BA", [2], label="Modul-ID"),
    Handbook(OTH / "Künstliche Intelligenz (B.Sc.).pdf", "oth_ba_ki", "OTH Amberg-Weiden", "BA", [2, 3], "tabbed", label="Modul-ID"),
    Handbook(OTH / "Künstliche Intelligenz (M.Sc.).pdf", "oth_ma_ki", "OTH Amberg-Weiden", "MA", [2], "tabbed", label="Modul-ID"),
    Handbook(OTH / "IT und Automation (M.Eng.).pdf", "oth_ma_ita", "OTH Amberg-Weiden", "MA", [4, 5]),
    Handbook(OTH / "AI for Industrial Applications (M.Sc.).pdf", "oth_ma_aiia", "OTH Amberg-Weiden", "MA", [2]),
]
OTH26 = REPO_ROOT / "data" / "raw" / "oth handbooks 2026"
OUT_2026 = REPO_ROOT / "data" / "interim" / "modules_emi_2026.csv"
REPORT_2026 = REPO_ROOT / "reports" / "modules_emi_2026_check.md"
_O = "OTH Amberg-Weiden"
EMI_2026 = [  # current handbooks of every EMI programme (KI B.Sc.: no newer handbook online, earlier copy)
    Handbook(OTH26 / "oth_hb_dd_ba.pdf", "oth26_ba_dd", _O, "BA", [2, 3], "tabbed"),
    Handbook(OTH26 / "oth_hb_ei_ba_2022.pdf", "oth26_ba_ei", _O, "BA", [2, 3], label="Modul-ID"),
    Handbook(OTH26 / "oth_hb_gi_ba.pdf", "oth26_ba_gi", _O, "BA", [2, 3], unordered=True),
    Handbook(OTH26 / "oth_hb_iki_ba.pdf", "oth26_ba_iki", _O, "BA", [2, 3], "tabbed"),
    Handbook(OTH26 / "oth_hb_mt_ba.pdf", "oth26_ba_mt", _O, "BA", [2, 3], "numbered", plan_pages=[6]),
    Handbook(OTH26 / "oth_hb_ii_mi_ba.pdf", "oth26_ba_ii|oth26_ba_mi", _O, "BA", [2, 3],
             programmes={"Industrie-4.0-Informatik": "oth26_ba_ii", "Medieninformatik": "oth26_ba_mi"}, label="Modul-ID"),
    Handbook(OTH / "Künstliche Intelligenz (B.Sc.).pdf", "oth26_ba_ki", _O, "BA", [2, 3], "tabbed", label="Modul-ID"),
    Handbook(OTH26 / "oth_hb_mapr_ma.pdf", "oth26_ma_mapr", _O, "MA", [2]),
    Handbook(OTH26 / "oth_hb_edu_ma.pdf", "oth26_ma_edu", _O, "MA", [2], "tabbed"),
    Handbook(OTH26 / "oth_hb_mp_ma.pdf", "oth26_ma_mp", _O, "MA", [2, 3], "numbered", plan_pages=[5, 6]),
    Handbook(OTH26 / "oth_hb_mai_ma.pdf", "oth26_ma_mai", _O, "MA", [2]),
    Handbook(OTH26 / "oth_hb_ia_ma.pdf", "oth26_ma_ia", _O, "MA", [4, 5]),
    Handbook(OTH26 / "oth_hb_mki_ma.pdf", "oth26_ma_mki", _O, "MA", [2], "tabbed"),
]
OUT_REF = REPO_ROOT / "data" / "interim" / "modules_references.csv"
REPORT_REF = REPO_ROOT / "reports" / "modules_references_check.md"
REF = REPO_ROOT / "data" / "raw" / "references"
REFERENCES = [  # reference curricula for options without a handbook in the baseline set (re-scope feasibility check)
    Handbook(REPO_ROOT / "data" / "raw" / "anchors" / "hske_ba_robotik.pdf", "hske_ba_rob", "Hochschule Kempten", "BA", [2, 3, 4],
             "numbered", exclude=r"^(?!RO\s?\d)", ects_rule="sum_lp"),
    # equal-evidence candidates (configs/reference_documents.yaml)
    Handbook(REF / "ref_autonomous_deggendorf.pdf", "thd_ba_em", "TH Deggendorf", "BA", [2, 3], "code", code_re=r"EM-\d+"),
    Handbook(REF / "ref_energydata_dortmund.pdf", "fhdo_ba_eedm", "FH Dortmund", "BA", [2], body_prefix=r"^\d{3,6}\s+",
             ects_rule="art", heading_first=True),
    Handbook(REF / "ref_visual_computing_coburg.pdf", "hsc_ba_vc", "Hochschule Coburg", "BA", [6, 7, 8],
             body_prefix=r"^Modulbezeichnung\s+"),
    Handbook(REF / "ref_geodata_hm.pdf", "hm_ba_gds", "Hochschule München", "BA", [2, 3], "code", unordered=True,
             code_re=r"\d{3} -", code_page=True),
]
NAME_ONLY = [  # (file, programme_id, institution, level)
    (COMP / "aalen_ma_cyber_security_pflichtmodule.pdf", "aalen_ma_csc", "HS Aalen", "MA"),
    (COMP / "aalen_ma_cyber_security_wahlpflichtmodule.pdf", "aalen_ma_csc", "HS Aalen", "MA"),
]
THM_CSV = COMP / "thm_ma_technische_informatik_modules.csv"


def norm(s: str) -> str:
    s = s.replace("\t", " ").replace("–", "-").replace("—", "-").replace("’", "'").replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"^\[[^\]]*\]\s*", "", s.strip())  # "[ SK1 ]  Title", "[ SEK=SWE1 ]  Title"
    return re.sub(r"\s+", " ", s).strip().lower()


def compact(s: str) -> str:
    """Letters and digits only: robust to line breaks, hyphenation and punctuation."""
    return re.sub(r"[^a-z0-9äöüß]", "", norm(s))


def read_pages(path: Path) -> list[str]:
    return [(p.extract_text() or "") for p in pypdf.PdfReader(path).pages]


def boilerplate(pages: list[str]) -> set[str]:
    """Normalised lines on >= 30 % of pages (headers/footers)."""
    freq = Counter(norm(l) for p in pages for l in set(p.splitlines()) if l.strip())
    return {l for l, n in freq.items() if n >= max(3, 0.3 * len(pages))}


def strip_boilerplate(pages: list[str]) -> list[list[str]]:
    """Lines per page without headers/footers: the contiguous run of repeated lines (on >= 30 % of pages),
    bare page numbers and "Stand: ... Seite N" lines at the top and bottom of each page. Repeated field
    labels inside the page ("ECTS-Credits") stay."""
    common = boilerplate(pages)
    header = re.compile(r"^(stand: ?[\d.]+ ?)?(seite|page) \d+( von \d+)?$|^stand: ?[\d.]+$|^\d{1,3}$")

    def edge(l: str) -> bool:
        return norm(l) in common or bool(header.match(norm(l)))

    out = []
    for p in pages:
        ls = [l.rstrip() for l in p.splitlines() if l.strip()]
        a, b = 0, len(ls)
        while a < b and edge(ls[a]):
            a += 1
        while b > a and edge(ls[b - 1]):
            b -= 1
        out.append([l for l in ls[a:b] if not re.fullmatch(r"\s*\d{1,3}\s*", l)])
    return out


def toc_titles(hb: Handbook, pages: list[str]) -> list[tuple[str, str]]:
    """(title, section) in TOC order. Lines without a page number directly before an entry are a wrapped title."""
    out, section, carry = [], "", []
    extra = re.compile(hb.exclude, re.I) if hb.exclude else None
    common = boilerplate(pages)
    for n in hb.toc_pages:
        for raw in pages[n - 1].splitlines():
            line = raw.replace("\t", " ").strip()
            if not line or norm(line) in common:
                continue
            if hb.toc_style == "numbered":  # "1.2 Title ....." or "2.1.3 Title 17": numbered entries, page optional
                m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+?)\s*(?:(?:[\.…]\s?){3,}.*|\s\d{1,3})?\s*$", line)
                if not m:
                    continue
                title = m.group(2).strip()
                if "." not in m.group(1):          # level 1 = a section heading ("2 TECHNIK UND PRODUKTION ...")
                    section = title
                    continue
                if "(vgl." in title or re.match(r"(?i)wahlpflichtmodule\b", title):   # cross-reference or group heading
                    continue
                if extra and extra.search(title):
                    continue
                out.append((title, section))
                continue
            if hb.toc_style == "code":
                m = re.match(rf"^({hb.code_re})\s+(.+)$", line)
                if m:
                    rest = re.sub(r"\s+\d{1,3}$", "", m.group(2).strip()) if hb.code_page else m.group(2).strip()
                    out.append((f"{m.group(1)} {rest}", section))
                elif out and out[-1][0].endswith((",", "-", "(", "und")):
                    out[-1] = (f"{out[-1][0]} {line}", out[-1][1])  # wrapped title
                continue
            pat = (r"^(.*?)\s*(?:(?:[\.…]\s?){4,}|\s\.)\s*\d{1,3}\s*$" if hb.toc_style == "dotted"
                   else r"^(.*?\S)\s+\d{1,3}\s*$")  # dotted leader, or a single " . 96"
            m = re.match(pat, line)
            if not m:
                wrap = len(line) > 3 and not EXCLUDE.match(norm(line)) and not re.search(r"\d\s*$|\bseite \d", norm(line))
                carry = (carry + [line])[-3:] if wrap else []
                continue
            own = m.group(1).strip()
            # pypdf sometimes puts two entries on one line: "Title A . 96 Title B"
            parts = [x.strip() for x in re.split(r"(?<=[A-Za-zäöüß)])\s*(?:\.\s?)+\s*\d{1,3}\s+(?=[A-ZÄÖÜ\[])", own) if x.strip()]
            if not parts:  # entry line holds only dots and page: the title is on the line(s) before
                parts = [" ".join(carry)] if carry else []
                carry = []
                if not parts:
                    continue
            parts[0] = " ".join(carry + [parts[0]]) if carry and not EXCLUDE.match(norm(parts[0])) else parts[0]
            carry = []
            for title in parts:
                t = norm(title)
                if re.match(r"^\d+(\.\d+)*\.?\s", t) or title.isupper():
                    section = title
                if not t or EXCLUDE.match(t) or (extra and extra.search(title)) or title.isupper():
                    continue
                out.append((title, section))
    return out


def locate(lines: list[tuple[int, str]], titles: list[str], start: int, strip_numbers: bool = False,
           prefix: str = "", first: bool = False) -> list[int | None]:
    """Index in `lines` of each title's heading, searched forward in TOC order. strip_numbers: body headings carry the
    TOC numbering ("1.1 Mathematik 1"); compare without it (numbered handbooks only). prefix: other body-only prefix."""
    if strip_numbers:
        lines = [(p, re.sub(r"^\s*\d+(?:\.\d+)+\.?\s+", "", l)) for p, l in lines]
    if prefix:
        lines = [(p, re.sub(prefix, "", l)) for p, l in lines]
    pos, cursor = [], start
    for title in titles:
        t = compact(title)
        key = t[:40]
        found = None
        for i in range(cursor, len(lines)):
            a = compact(lines[i][1])
            if len(a) < 4 or len(a) > 2 * len(t) + 30 or not t.startswith(a[:4]):
                continue
            if first and i > 0 and lines[i - 1][0] == lines[i][0]:   # not the first line of its page: e.g. a course row
                continue
            joined = compact(" ".join(l for _, l in lines[i:i + 3]))
            if not (a.startswith(key) or (len(a) < len(key) and joined.startswith(key))):
                continue
            rest = norm(" ".join(l for _, l in lines[i:i + 3]))[len(norm(title)):]
            if re.match(r"^\s*\d+([,.]\d)?\s+\d", rest):  # study-plan table row: "Title 5 4 SU/Ü ..."
                continue
            found = i
            break
        pos.append(found)
        if found is not None:
            cursor = found + 1
    return pos


NUM = r"(?<![A-Za-z0-9.,])(\d{1,2}(?:[,.]5)?)(?![0-9])"
ECTS = [r"Number of Credits\s.{0,160}?(?:modul|Modul\)|module)[^0-9]{0,25}?" + NUM,  # OTH table: "... SK1 Pflichtmodul 5"
        r"(?:ECTS|\bCP\b|Credits?|Leistungspunkte|\bLP\b|Credit Points)[^0-9\n]{0,40}?" + NUM,
        NUM + r"\s*(?:ECTS|CP|LP|Credits?)\b"]


def find_ects(text: str, strict: bool = False) -> str:
    head = text[:2500]
    pats = [x.replace(NUM, NUM + r"(?![.,]\d)") for x in ECTS] if strict else ECTS
    for pat in pats:
        for m in re.finditer(pat, head, re.I | re.S):
            v = float(m.group(1).replace(",", "."))
            if 1 <= v <= 30:
                return m.group(1).replace(",", ".")
    return ""


CONTENT = re.compile(r"\b(Lerninhalte|Lehrinhalte|Inhalte?|Contents?|Lernziele|Lernergebnisse|Qualifikationsziele|"
                     r"Learning [Oo]utcomes|Kompetenzen)\b:?")


def plan_ects(hb: Handbook, pages: list[str]) -> dict[str, str]:
    """ECTS per module from the study-plan table: rows "1.3 MPT Title ... 4 5 4 5" = (SWS, ECTS) per semester;
    the module's ECTS is the sum of every second number. Rows can wrap over several lines."""
    out = {}
    for n in hb.plan_pages:
        text = pages[n - 1].replace("\t", " ")
        for chunk in re.split(r"(?m)^(?=\s*\d+(?:\.\d+)*\.?\s)", text):   # every numbered row starts a chunk
            m = re.match(r"\s*\d+(?:\.\d+)+\.?\s+[A-Z][A-Za-z0-9]{0,5}\s+(.+?)\s+((?:\d{1,2}(?:,5)?\s+)*\d{1,2}(?:,5)?)\s*$",
                         " ".join(chunk.split()))
            if not m:
                continue
            nums = [float(x.replace(",", ".")) for x in m.group(2).split()]
            if len(nums) >= 2 and len(nums) % 2 == 0:
                v = sum(nums[1::2])
                out[compact(m.group(1))] = f"{v:g}"
    return out


def sum_lp(text: str) -> str:
    """Sum of the "N LP" values in the German teaching-methods field (before the English "Lecture:" repeat)."""
    m = re.search(r"Lehrmethoden.*?(?=Lecture:|Arbeitsaufwand|Workload)", text[:4000], re.S)
    vals = [float(x.replace(",", ".")) for x in re.findall(r"(\d{1,2}(?:,\d)?)\s*LP\b", m.group(0))] if m else []
    return f"{sum(vals):g}" if vals else ""


def art_ects(text: str) -> str:
    """Credits in the module-type column of a header table ("... Art des Moduls ECTS ... Pflichtfach 14")."""
    m = re.search(r"\b(?:Wahlpflichtfach|Pflichtfach|Wahlfach|Wahlpflichtmodul|Pflichtmodul)\s+(\d{1,2})\b", text[:1500])
    return m.group(1) if m else ""


def content_excerpt(text: str, n: int = 250) -> str:
    """Start of the content / learning-outcome part (skips the form fields at the top)."""
    m = CONTENT.search(text, 150)
    return text[m.start():m.start() + n] if m else text[:n]


def find_semester(text: str) -> str:
    m = re.search(r"\b([1-7])\.\s*(?:Fach)?[Ss]emester\b|[Ss]emester\D{0,25}?\b([1-7])\b", text[:2500])
    return (m.group(1) or m.group(2)) if m else ""


def parse(hb: Handbook) -> tuple[list[dict], dict]:
    pages = read_pages(hb.file)
    clean = strip_boilerplate(pages)
    lines = [(n + 1, l) for n, page in enumerate(clean) for l in page]
    entries = toc_titles(hb, pages)
    body_start = next(i for i, (p, _) in enumerate(lines) if p > max(hb.toc_pages))
    pos = locate(lines, [t for t, _ in entries], body_start, strip_numbers=hb.toc_style == "numbered", prefix=hb.body_prefix, first=hb.heading_first)
    if hb.unordered:  # second pass for titles the forward search missed; never reuse a heading already taken
        taken = {i for i in pos if i is not None}
        for k, (title, _) in enumerate(entries):
            if pos[k] is None:
                hit = locate(lines, [title], body_start, strip_numbers=hb.toc_style == "numbered", prefix=hb.body_prefix, first=hb.heading_first)[0]
                if hit is not None and hit not in taken:
                    pos[k] = hit
                    taken.add(hit)
    found = [(i, e) for i, e in zip(pos, entries) if i is not None]
    extra = []
    if hb.label:  # modules missing from the TOC: a 2nd label block inside one module
        helper = re.compile(r"^(zuordnung zum|curriculum|classification)$")
        for k, (i, (_, section)) in enumerate(found):
            end = found[k + 1][0] if k + 1 < len(found) else len(lines)
            labels = [j for j in range(i + 1, end) if lines[j][1].strip().startswith(hb.label)]
            for j in labels[1:]:
                s = j - 1
                while s > i and helper.match(norm(lines[s][1])):
                    s -= 1
                extra.append((s, (re.sub(r"\s{2,}", " | ", lines[s][1].strip()), section)))
    found = sorted(found + extra, key=lambda x: x[0])
    texts = []
    for k, (i, _) in enumerate(found):
        end = found[k + 1][0] if k + 1 < len(found) else len(lines)
        texts.append(re.sub(r"\s+", " ", " ".join(l for _, l in lines[i + 1:end])).strip())
    starts = [lines[i][0] for i, _ in found]
    plan = plan_ects(hb, pages) if hb.plan_pages else {}
    rows, dropped = [], []
    for k, (i, (title, section)) in enumerate(found):
        text, source = texts[k], "handbook"
        ref = re.search(r"siehe Seite (\d+)", text, re.I)
        if ref and len(text) < 300:  # "see page 36": description shared with another module
            target = max((j for j, s in enumerate(starts) if s <= int(ref.group(1))), default=None)
            if target is not None and target != k:
                text, source = texts[target], f"handbook (cross-reference to p{ref.group(1)})"
        if len(text) < 50:  # a group heading in the TOC, not a module
            dropped.append(title)
            continue
        if hb.programmes:
            hit = [pid for kw, pid in hb.programmes.items() if kw.lower() in section.lower()]
            pids = hit or list(hb.programmes.values())
        else:
            pids = [hb.programme_id]
        for pid in pids:
            rows.append({"programme_id": pid, "institution": hb.institution, "level": hb.level,
                         "module_id": f"{pid}:{len([r for r in rows if r['programme_id'] == pid]) + 1:03d}",
                         "title": title, "section": section,
                         "ects": {"sum_lp": sum_lp, "art": art_ects}.get(hb.ects_rule, lambda _: "")(text) or find_ects(text, hb.strict_ects)
                                 or next((v for k, v in plan.items() if k.startswith(compact(title)[:25])), ""),
                         "semester": find_semester(text),
                         "text": text, "text_chars": len(text), "source_file": hb.file.relative_to(REPO_ROOT).as_posix(),
                         "page": lines[i][0], "text_source": source})
    missing = [t for i, (t, _) in zip(pos, entries) if i is None]
    return rows, {"file": hb.file.name, "programme_id": hb.programme_id, "toc": len(entries), "found": len(found) - len(extra),
                  "missing": missing, "dropped": dropped, "not in TOC (label split)": "; ".join(t for _, (t, _) in extra) or "-"}


def name_only() -> list[dict]:
    rows = []
    for path, pid, inst, level in NAME_ONLY:
        txt = " ".join(read_pages(path))
        for code, title in re.findall(r"\b(25\d{3})\s+(.+?)(?=\s+25\d{3}\b|\s+Studienschwerpunkt|\s+Wahlpflicht|\s+Betriebswirtschaft|"
                                      r"\s+Informatik\s+25|\s+Wirtschaftsinformatik\s+25|\s*\*|$)", txt):
            rows.append({"programme_id": pid, "institution": inst, "level": level, "module_id": "", "title": f"{code} {title.strip()}",
                         "section": "Pflichtmodule" if "pflichtmodule" in path.stem and "wahl" not in path.stem else "Wahlpflichtmodule",
                         "ects": "", "semester": "", "text": "", "text_chars": 0,
                         "source_file": path.relative_to(REPO_ROOT).as_posix(), "page": 1, "text_source": "module list (names only)"})
    seen, out = set(), []
    for r in rows:  # a module can appear in several focus areas: keep once per programme
        if (r["programme_id"], r["title"]) not in seen:
            seen.add((r["programme_id"], r["title"]))
            out.append(r)
    with THM_CSV.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.append({"programme_id": "thm_ma_ti", "institution": "TH Mannheim", "level": "MA", "module_id": "",
                        "title": r["module"], "section": f"Schwerpunkt {r['focus_area']}", "ects": r["credits"], "semester": r["term"],
                        "text": "", "text_chars": 0, "source_file": THM_CSV.relative_to(REPO_ROOT).as_posix(), "page": "",
                        "text_source": "programme page (names only)"})
    for pid in {r["programme_id"] for r in out}:
        for k, r in enumerate([r for r in out if r["programme_id"] == pid], 1):
            r["module_id"] = f"{pid}:{k:03d}"
    return out


COLUMNS = ["programme_id", "institution", "level", "module_id", "title", "section", "ects", "semester",
           "text", "text_chars", "source_file", "page", "text_source"]


def _md(rows: list[dict], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols) + " |" for r in rows]
    return "\n".join(out)


def report(rows: list[dict], checks: list[dict]) -> str:
    hb = [r for r in rows if r["text_source"].startswith("handbook")]
    per = []
    for c in checks:
        mine = [r for r in hb if r["source_file"].endswith(c["file"])]
        uniq = {(r["title"], r["page"]) for r in mine}
        short = sum(1 for r in mine if r["text_chars"] < SHORT) // max(1, len(c["programme_id"].split("|")))
        per.append({**c, "modules": len(uniq), "short (<200 chars)": short,
                    "no ECTS": sum(1 for r in mine if not r["ects"]) // max(1, len(c["programme_id"].split("|"))),
                    "missing": "; ".join(c["missing"]) or "-", "dropped (group headings)": "; ".join(c["dropped"]) or "-",
                    "not in TOC": c["not in TOC (label split)"]})
    uniq_all = {(r["source_file"], r["title"], r["page"]): r for r in hb}
    n_short = sum(1 for r in uniq_all.values() if r["text_chars"] < SHORT)
    random.seed(SEED)
    sample = random.sample(sorted(uniq_all.values(), key=lambda r: (r["source_file"], r["page"])), 10)
    spot = [{"#": k, "file": Path(r["source_file"]).name, "PDF page": r["page"], "extracted title": r["title"], "ECTS": r["ects"] or "-",
             "first 300 characters of text": r["text"][:300], "content excerpt": content_excerpt(r["text"])}
            for k, r in enumerate(sample, 1)]
    names = Counter(r["programme_id"] for r in rows if not r["text_source"].startswith("handbook"))
    return "\n".join([
        "# Module table check (generated)", "",
        f"Rows: {len(rows)} (programme x module). Unique handbook modules: {len(uniq_all)}; "
        f"short texts (<{SHORT} chars): {n_short} ({n_short / max(1, len(uniq_all)) * 100:.1f} %). "
        f"Names-only rows: " + ", ".join(f"{k} {v}" for k, v in sorted(names.items())) + ".", "",
        "## Per handbook: TOC entries vs modules found", "",
        _md(per, ["file", "programme_id", "toc", "found", "modules", "short (<200 chars)", "no ECTS", "missing", "dropped (group headings)", "not in TOC"]), "",
        "## Spot check (10 random handbook modules, seed 20261017)", "",
        "Compare each row with the PDF page: is the title right, is the ECTS value right, does the text belong to this module?", "",
        _md(spot, ["#", "file", "PDF page", "extracted title", "ECTS", "first 300 characters of text", "content excerpt"]), ""])


def main(argv: list[str] | None = None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description="module table from module handbooks")
    ap.add_argument("--set", choices=["baseline", "emi2026", "references"], default="baseline")
    args = ap.parse_args(argv)
    handbooks, out, report_path = {"emi2026": (EMI_2026, OUT_2026, REPORT_2026), "references": (REFERENCES, OUT_REF, REPORT_REF),
                                   "baseline": (HANDBOOKS, OUT, REPORT)}[args.set]
    if args.set in ("emi2026", "references"):   # numbered codes ("3.3.4") sit next to the credit field in some current handbooks
        for hb in handbooks:
            hb.strict_ects = True
    rows, checks = [], []
    for hb in handbooks:
        r, c = parse(hb)
        rows += r
        checks.append(c)
        print(f"{hb.file.name:<55} TOC {c['toc']:>3}  found {c['found']:>3}  missing {len(c['missing'])}")
    if args.set == "baseline":
        rows += name_only()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report(rows, checks), encoding="utf-8")
    print(f"Written: {out.relative_to(REPO_ROOT)} ({len(rows)} rows), {report_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
