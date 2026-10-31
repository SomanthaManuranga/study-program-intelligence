"""Module gap analysis: competitor cybersecurity modules vs EMI modules (Step 41).

Run from the repository root:

    python -m study_program_intelligence.analysis.module_gaps

Method (decision log 2026-10-17)
- Text: content and learning outcomes of each module (form fields and literature removed),
  title prepended. Names-only sources (HS Aalen, TH Mannheim) use the title.
- Categories: "security" (title, or dense security vocabulary in the content), "general"
  (maths, programming, systems, soft skills, ...) and "frame" (thesis, internship, placeholder
  electives), which is left out of the coverage shares.
- Similarity 1: intfloat/multilingual-e5-base, "query: " prefix (symmetric task), 200-word chunks,
  mean of the normalised chunk embeddings, then centred PER HANDBOOK (each handbook's mean subtracted,
  re-normalised): raw e5 cosines are compressed (unrelated pairs ~0.9) and each handbook has a house style
  (template sentences); best-match AUC on the reference set 0.65 raw-centred -> 0.72 per-handbook.
  Similarity 2 (cross-check, independent of the model): character 3-5-gram TF-IDF.
- Comparison: competitor bachelor modules vs EMI bachelor modules; competitor master modules vs
  EMI bachelor and master modules. A module is "covered" if its best EMI match >= threshold.
- Thresholds: calibrated per method on a topic reference set: competitor/EMI pairs whose titles share
  a topic group (TOPICS) = positives, pairs with topics but none shared = negatives; Youden's J.
  Validated by a 20-pair hand check (10 near the threshold, 5 clearly covered, 5 clearly gap).
- Headline: ECTS-weighted share of each competitor programme's security (and general) ECTS that EMI
  covers; "typical" = median over the competitor bachelors (4) / masters (3). Missing ECTS = 5.
- CyBOK 1.1 knowledge areas assigned to security modules by ordered title rules (CYBOK_TITLE), else the
  OT flag -> Cyber-Physical Systems Security, else embedding similarity to short area descriptions.
  Two transparent pseudo-areas: "AI & security", "Broad / introductory security"; penetration testing and
  auditing kept as a practice area. OT/industrial flag: OT keyword in the title or >= 3 hits in the text. Aalen and Mannheim (names only) are reported as
  indicative, title-based, outside the headline.
Outputs: data/interim/module_scores.csv, reports/module_gaps.md, reports/module_gaps_check.md.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULES = REPO_ROOT / "data" / "interim" / "modules.csv"
CACHE = REPO_ROOT / "data" / "interim" / "embeddings_e5"
SCORES = REPO_ROOT / "data" / "interim" / "module_scores.csv"
REPORT = REPO_ROOT / "reports" / "module_gaps.md"
CHECK = REPO_ROOT / "reports" / "module_gaps_check.md"
MODEL = "intfloat/multilingual-e5-base"
CHUNK_WORDS = 200
SEED = 20261017

COMPETITOR_BA = ["fau_ba_its", "thi_ba_csi", "deg_ba_cy", "thws_ba_is"]
COMPETITOR_MA = ["thi_ma_cse", "deg_ma_cy", "hdbw_ma_cs"]
TITLE_ONLY = ["aalen_ma_csc", "thm_ma_ti"]
EMI_BA = ["oth_ba_ii", "oth_ba_mi", "oth_ba_eit", "oth_ba_ki"]
EMI_MA = ["oth_ma_ki", "oth_ma_ita", "oth_ma_aiia"]

CONTENT_START = re.compile(r"\b(Lerninhalte|Lehrinhalte|Inhalte?|Contents?|Lernziele|Lernergebnisse|Qualifikationsziele|"
                           r"Learning [Oo]utcomes|Kompetenzen|Modulziele)\b:?")
# A literature section heading, not the word in running text ("... der englischsprachigen Literatur ..."):
# no lowercase word directly before it.
LITERATURE = re.compile(r"(?<![a-zäöüß] )(?<![a-zäöüß]-)\b(Literatur(hinweise|liste|empfehlungen|verzeichnis)?|Empfohlene Literatur|"
                        r"Literature|Recommended (reading|literature)|Reading list)\b:?")
SEC = re.compile(r"secur|sicherheit|sichere[nrs]?\b|krypt|crypt|forensi|penetration|pentest|hacking|hacker|angriff|attack|malware|"
                 r"incident|intrusion|privacy|datenschutz|threat|bedrohung|vulnerab|schwachstell|exploit|firewall|authenti|"
                 r"zugriffskontrolle|access control|cyber(?!-?physi)|siem\b|\bsoc\b|resilien|abwehr|defen[cs]e|steganograph|"
                 r"anonymi|spionage|espionage|isms|bsi\b|iso ?27001|62443|compliance|it-recht|it law", re.I)
FRAME = re.compile(r"bachelorarbeit|masterarbeit|bachelor'?s? thesis|master'?s? thesis|\bthesis\b|masterthesis|bachelormodul|"
                   r"kolloquium|praxis(modul|phase|semester|seminar)|praktikum \(|praktisches studiensemester|internship|"
                   r"praxissemester|einführungsprojekt|allgemeines wahlpflichtmodul|studiengangsspezifische wahlpflichtmodule|"
                   r"wahlpflichtmodul projekt|wahlpflicht(modul|fach) \d|vertiefungsmodul \d|praxisseminar|seminar bachelorarbeit|masterseminar|"
                   r"^\s*(\[[^\]]*\]\s*)?(fw|sw|aw|kv)\d", re.I)
OT = re.compile(r"\bOT\b|operational technology|industrial (control|security|automation|communication|internet|network)|"
                r"industrielle[nr]? (kommunikation|netz|automati|steuerung|sicherheit|informationstechn)|\bICS\b|SCADA|\bSPS\b|\bPLC\b|"
                r"62443|industrie ?4\.0|industry ?4\.0|feldbus|fieldbus|profinet|opc ?ua|modbus|automotive|fahrzeug|"
                r"cyber-?physi|leitsystem|prozessleit|industrial (iot|internet of things)|\biiot\b", re.I)

# CyBOK 1.1 knowledge areas: short descriptions used to assign security modules (German and English keywords).
CYBOK = {
    "Risk Management & Governance": "risk management, governance, ISMS, ISO 27001, BSI IT-Grundschutz, security management, Sicherheitsmanagement, Risikoanalyse, Informationssicherheitsmanagement, security policy",
    "Law & Regulation": "law, regulation, IT-Recht, Datenschutzrecht, DSGVO, GDPR, compliance, legal aspects, NIS2, cybercrime law, Haftung, Vertragsrecht",
    "Human Factors": "human factors, usable security, social engineering, security awareness, Mensch, Nutzerverhalten, phishing awareness, psychology of security",
    "Privacy & Online Rights": "privacy, Datenschutz, anonymity, Anonymität, privacy enhancing technologies, tracking, surveillance, online rights, data protection by design",
    "Malware & Attack Technologies": "malware, viruses, worms, ransomware, exploits, attack techniques, Schadsoftware, Angriffstechniken, botnets, reverse engineering of malware",
    "Adversarial Behaviours": "adversaries, cybercrime, attackers, threat actors, threat intelligence, OSINT, espionage, Spionage, Täterverhalten, underground economy",
    "Security Operations & Incident Management": "security operations, SOC, SIEM, intrusion detection, monitoring, incident response, incident management, Notfallmanagement, Netzwerkmonitoring, logging, threat hunting",
    "Forensics": "digital forensics, Computerforensik, IT-Forensik, Beweissicherung, memory forensics, mobile forensics, Mobilfunkforensik, file system forensics, evidence",
    "Cryptography": "cryptography, Kryptographie, Kryptologie, encryption, Verschlüsselung, hash functions, digital signatures, number theory, ciphers, cryptanalysis",
    "Applied Cryptography": "applied cryptography, cryptographic protocols, TLS, PKI, certificates, key management, secure channels, cryptographic engineering",
    "Operating Systems & Virtualisation Security": "operating system security, Betriebssystemsicherheit, virtualisation, hypervisor, container security, kernel, isolation, system hardening, Härtung",
    "Distributed Systems Security": "distributed systems security, cloud security, blockchain, distributed ledger, peer-to-peer, consensus, verteilte Systeme Sicherheit",
    "Formal Methods for Security": "formal methods, formal verification, protocol verification, model checking, security proofs, theorem proving",
    "Authentication, Authorisation & Accountability": "authentication, Authentifizierung, authorisation, access control, Zugriffskontrolle, identity management, IAM, single sign-on, accountability",
    "Software Security": "software security, secure coding, sichere Programmierung, vulnerabilities, buffer overflow, static analysis, fuzzing, Schwachstellen",
    "Web & Mobile Security": "web security, Websicherheit, web application security, OWASP, browser security, mobile security, Android, iOS, app security",
    "Secure Software Lifecycle": "secure software development lifecycle, security engineering, threat modelling, security requirements, DevSecOps, secure design, Security by Design",
    "Network Security": "network security, Netzwerksicherheit, Netzsicherheit, firewalls, VPN, IPsec, network protocols attacks, wireless security, DNS security",
    "Hardware Security": "hardware security, side channels, Seitenkanalangriffe, trusted platform module, secure elements, embedded security hardware, chip security",
    "Cyber-Physical Systems Security": "cyber-physical systems security, industrial control systems, OT security, SCADA, PLC, IEC 62443, automotive security, IoT security, industrial security",
    "Physical Layer & Telecommunications Security": "physical layer security, telecommunications security, mobile networks, 5G security, radio, jamming, GSM, LTE security",
    "Penetration Testing & Auditing (not a CyBOK area; practice)": "penetration testing, Penetration Testing, ethical hacking, security auditing, Auditierung von IT-Systemen, vulnerability assessment, red teaming",
}


def clean(text: str, title: str) -> str:
    """Title + content/learning outcomes, without form fields and literature lists."""
    t = text or ""
    m = CONTENT_START.search(t, 80)
    if m:
        t = t[m.start():]
    lit = LITERATURE.search(t, 200)
    if lit:
        t = t[:lit.start()]
    title = re.sub(r"^\[[^\]]*\]\s*", "", title)
    title = re.sub(r"^[BM]-CY-\d+\s+", "", title)
    return re.sub(r"\s+", " ", f"{title}. {t}").strip()


def category(title: str, text: str) -> str:
    if FRAME.search(title):
        return "frame"
    if SEC.search(title):
        return "security"
    hits = len(SEC.findall(text))
    if hits >= 6 and hits / max(1, len(text)) * 1000 >= 3:
        return "security"
    return "general"


def chunks(text: str, n: int = CHUNK_WORDS) -> list[str]:
    w = text.split()
    return [" ".join(w[i:i + n]) for i in range(0, max(1, len(w)), n)] or [text]


def embed(texts: list[str]) -> np.ndarray:
    """Chunked e5 embeddings, cached per text hash."""
    CACHE.mkdir(parents=True, exist_ok=True)
    keys = [hashlib.sha256(t.encode("utf-8")).hexdigest()[:20] for t in texts]
    todo = [(k, t) for k, t in zip(keys, texts) if not (CACHE / f"{k}.npy").exists()]
    if todo:
        from sentence_transformers import SentenceTransformer   # only needed when a text is missing from the cache
        model = SentenceTransformer(MODEL)
        for k, t in todo:
            parts = chunks(t)
            e = model.encode([f"query: {p}" for p in parts], normalize_embeddings=True, batch_size=16)
            v = e.mean(axis=0)
            np.save(CACHE / f"{k}.npy", v / np.linalg.norm(v))
    return np.vstack([np.load(CACHE / f"{k}.npy") for k in keys])


def tfidf_matrix(texts: list[str], fit_on: list[bool] | None = None):
    """Character 3-5-gram TF-IDF (within word boundaries): robust to German compounds ("Netzwerksicherheit" vs
    "Netzsicherheit"). Chosen over word 1-2-grams by best-match AUC on the reference set (0.75 vs 0.67).
    fit_on: fit the vocabulary and IDF on these texts only and transform all (keeps earlier results fixed)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True, min_df=2, max_df=0.3, sublinear_tf=True)
    if fit_on is None:
        return v.fit_transform(texts)
    v.fit([t for t, k in zip(texts, fit_on) if k])
    return v.transform(texts)


def load() -> pd.DataFrame:
    d = pd.read_csv(MODULES)
    d["names_only"] = ~d["text_source"].str.startswith("handbook")
    d["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(d["text"], d["title"])]
    d.loc[d["names_only"], "clean"] = d.loc[d["names_only"], "title"].map(lambda t: re.sub(r"^\d{5}\s+", "", t))
    d["category"] = [category(ti, c) for ti, c in zip(d["title"], d["clean"])]
    d["ot"] = d["clean"].map(lambda c: len(OT.findall(c))) >= 3
    d.loc[d["title"].str.contains(OT), "ot"] = True
    d["ects_used"] = pd.to_numeric(d["ects"], errors="coerce")
    d["ects_imputed"] = d["ects_used"].isna()
    d["ects_used"] = d["ects_used"].fillna(5.0)
    d["side"] = np.where(d["programme_id"].str.startswith("oth_"), "emi", "competitor")
    return d.reset_index(drop=True)

# Topic groups for the calibration reference set (title level). A pair is a positive if both titles share a group.
TOPICS = {
    "mathematics": r"mathemati|lineare algebra|diskrete mathematik|\banalysis\b|algebra\b",
    "statistics": r"statisti|stochasti|wahrscheinlichkeit",
    "programming": r"programmier|programming|programmieren|\bpython\b|c\+\+|\bjava\b",
    "algorithms": r"algorithm",
    "databases": r"datenbank|database",
    "operating systems": r"betriebssystem|operating system",
    "networks": r"rechnernetz|computernetz|kommunikationsnetz|netzwerke\b|networks?\b(?!.*secur)|internettechnolog|internet technolog",
    "software engineering": r"software.?engineering|softwaretechnik|softwareentwicklung",
    "theory": r"theoretische informatik|formale sprachen|automatentheorie",
    "web": r"webtechnolog|web.?technolog|web-?anwendung|webentwicklung|web.?engineering|web.?programm",
    "ai/ml": r"machine learning|maschinelles lernen|künstliche intelligenz|artificial intelligence|deep learning|neuronale",
    "data": r"data analytics|data science|big data|data engineering|data mining",
    "cryptography": r"krypto|crypto",
    "network security": r"netz(werk)?sicherheit|network security|netzwerk.?sicherheit",
    "security basics": r"grundlagen der (it-|informations)?sicherheit|einführung in die it-sicherheit|security fundamentals|"
                       r"introduction to (it |cyber )?security|grundlagen cyber security|informationssicherheit\b",
    "law/privacy": r"\brecht|\blaw\b|datenschutz|privacy|legal",
    "project management": r"projektmanagement|project management",
    "cloud": r"\bcloud",
    "embedded/iot": r"embedded|eingebettet|\biot\b|internet of things|cyber-?physi",
    "computer architecture": r"digitaltechnik|digitale systeme|rechnerarchitektur|computer architecture|technische informatik",
    "quantum": r"quantum|quanten",
    "forensics": r"forensi",
    "soft skills": r"englisch|english|präsentation|schlüsselqualifikation|soft.?skills|\bethik|ethics|wissenschaftliches arbeiten",
    "business": r"betriebswirtschaft|\bbwl\b|business (administration|model)|unternehmensgründung|entrepreneurship",
}


def topics(title: str) -> set[str]:
    t = title.lower()
    return {k for k, p in TOPICS.items() if re.search(p, t)}


def centre(e: np.ndarray, groups: pd.Series | None = None) -> np.ndarray:
    """Subtract the mean embedding (per group if given, e.g. per handbook: removes each handbook's house style)."""
    c = e.copy()
    if groups is None:
        c -= c.mean(axis=0)
    else:
        for g in pd.unique(groups):
            m = (groups == g).to_numpy()
            c[m] -= c[m].mean(axis=0)
    return c / np.linalg.norm(c, axis=1, keepdims=True)


def youden(pos: np.ndarray, neg: np.ndarray) -> tuple[float, float, float, float]:
    """Threshold maximising TPR - FPR; returns (threshold, tpr, fpr, auc)."""
    from sklearn.metrics import roc_auc_score, roc_curve
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    s = np.r_[pos, neg]
    fpr, tpr, thr = roc_curve(y, s)
    k = int(np.argmax(tpr - fpr))
    return float(thr[k]), float(tpr[k]), float(fpr[k]), float(roc_auc_score(y, s))


def comparison_set(d: pd.DataFrame, level: str) -> np.ndarray:
    pids = EMI_BA if level == "BA" else EMI_BA + EMI_MA
    return d.index[d["programme_id"].isin(pids) & (d["category"] != "frame")].to_numpy()


def best_matches(d: pd.DataFrame, sims: dict[str, np.ndarray], rows: np.ndarray) -> pd.DataFrame:
    out = []
    for i in rows:
        cand = comparison_set(d, d.at[i, "level"])
        rec = {"row": i}
        for name, s in sims.items():
            k = cand[int(np.argmax(s[i, cand]))]
            rec[f"{name}_score"], rec[f"{name}_match"] = float(s[i, k]), int(k)
        out.append(rec)
    return pd.DataFrame(out).set_index("row")


# Title rules for CyBOK areas, most specific first. Two transparent pseudo-areas: "AI & security" and
# "Broad / introductory security" (fundamentals, seminars, projects spanning several areas).
CYBOK_TITLE = [
    ("Forensics", r"forensi"),
    ("Penetration Testing & Auditing (not a CyBOK area; practice)", r"penetration|pentest|hacking|audit"),
    ("Security Operations & Incident Management", r"incident|monitoring|intrusion|\bsoc\b|siem|security operations|secure operations|"
                                                  r"detection|cyber defen[cs]e|abwehr"),
    ("Malware & Attack Technologies", r"malware|exploit|reverse engineering|angriff|attack"),
    ("Distributed Systems Security", r"blockchain|ledger|kryptowähr|cloud"),
    ("Cryptography", r"krypt|crypt"),
    ("Hardware Security", r"hardware"),
    ("Cyber-Physical Systems Security", r"industrial|industrie|ot security|cyber-?physi|\biot\b|automotive|fahrzeug"),
    ("Software Security", r"sichere programmierung|softwaresicherheit|software security|secure coding|systemnahe programmierung|"
                          r"security testing|anwendungssicherheit|application security"),
    ("Secure Software Lifecycle", r"security engineering|security architektur|threat model|product development|requirements engineering|secure design|devsecops"),
    ("Web & Mobile Security", r"\bweb|mobile[rn]?\b|\bapp\b|smartphone"),
    ("Law & Regulation", r"recht|\blaw\b|legal"),
    ("Privacy & Online Rights", r"privacy|datenschutz|anonym"),
    ("Network Security", r"netz|network|protokoll|internetkommunikation"),
    ("Operating Systems & Virtualisation Security", r"systemsicherheit|system security|secure systems|härtung|hardening|betriebssystem|virtuali"),
    ("Authentication, Authorisation & Accountability", r"authenti|identity|identität|access control|zugriffs"),
    ("Human Factors", r"human|social engineering|awareness|ethik|ethics|gesellschaft"),
    ("Adversarial Behaviours", r"osint|open source intelligence|spionage|cybercrime|threat intelligence|kriminal"),
    ("Risk Management & Governance", r"management|governance|grc|risiko|risk|isms|\bism\b|grundschutz|maturity|reifegrad|compliance|"
                                     r"standards|\bbcm\b"),
    ("AI & security (not a CyBOK area)", r"künstliche[nr]? intelligenz|maschinelles lernen|machine learning|\bki\b|\bai\b"),
    ("Broad / introductory security (spans several areas)", r"grundlagen|fundamentals|einführung|introduction|basics|seminar|projekt|project|"
                                                            r"aktuelle themen|informationssicherheit|cybersicherheit|it-sicherheit|cyber security"),
]


def assign_cybok(d: pd.DataFrame, emb_c: np.ndarray, rows: np.ndarray) -> pd.DataFrame:
    """CyBOK area per security module: title rule, else OT flag -> CPS, else embedding similarity (fallback)."""
    fallback = _cybok_embedding(emb_c, rows)
    out = []
    for i in rows:
        t = re.sub(r"^\[[^\]]*\]\s*|^[BM]-CY-\d+\s+|^\d{5}\s+", "", d.at[i, "title"]).lower()
        hit = next((ka for ka, pat in CYBOK_TITLE if re.search(pat, t)), None)
        if hit:
            out.append((hit, "title rule"))
        elif d.at[i, "ot"]:
            out.append(("Cyber-Physical Systems Security", "OT flag"))
        else:
            out.append((fallback[i], "embedding"))
    return pd.DataFrame(out, index=rows, columns=["cybok", "cybok_how"])


def _cybok_embedding(emb_c: np.ndarray, rows: np.ndarray) -> pd.Series:
    names = list(CYBOK)
    ka = centre(embed([f"{n}: {CYBOK[n]}" for n in names]))  # area descriptions centred as their own group
    s = emb_c[rows] @ ka.T
    return pd.Series([names[int(k)] for k in s.argmax(axis=1)], index=rows)


def coverage_table(d: pd.DataFrame, flag: str) -> pd.DataFrame:
    """ECTS-weighted coverage per competitor programme and category."""
    rows = []
    for pid in COMPETITOR_BA + COMPETITOR_MA:
        p = d[(d["programme_id"] == pid) & (d["category"] != "frame")]
        rec = {"programme": pid, "level": "BA" if pid in COMPETITOR_BA else "MA"}
        for cat in ("security", "general"):
            c = p[p["category"] == cat]
            rec[f"{cat} ECTS"] = c["ects_used"].sum()
            rec[f"{cat} covered %"] = round(c.loc[c[flag], "ects_used"].sum() / max(c["ects_used"].sum(), 1) * 100, 1)
        a = p
        rec["all covered %"] = round(a.loc[a[flag], "ects_used"].sum() / max(a["ects_used"].sum(), 1) * 100, 1)
        rows.append(rec)
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(v).replace("|", "/").replace("\n", " ") for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


# Standard opening phrases (for the hand-check display only): skipped so the excerpt starts with the topic.
INTRO = re.compile(r"^(.*?\.\s*)?(Lernziele\s*/\s*Qualifikationen des Moduls|Qualifikationsziele des Moduls|Lernergebnisse( des Moduls)?:?|"
                   r"Lerninhalte:|Inhalte?)?\s*(Learning Outcomes)?\s*(Nach dem erfolgreiche[nm] Absolvieren des Moduls verfügen die "
                   r"Studierenden über die folgenden [^:]*:)?\s*(•\s*)?(Fachkompetenz:?)?\s*", re.S)


def excerpt(clean_text: str, n: int = 300) -> str:
    title, _, body = clean_text.partition(". ")
    return INTRO.sub("", body, count=1)[:n]


def short(t: str, n: int) -> str:
    t = re.sub(r"^\[[^\]]*\]\s*|^[BM]-CY-\d+\s+", "", str(t))
    return t if len(t) <= n else t[: n - 1] + "…"


def main() -> None:
    d = load()
    raw = embed(d["clean"].tolist())
    emb = centre(raw, d["source_file"])
    tf = tfidf_matrix(d["clean"].tolist())
    sims = {"e5": emb @ emb.T, "tfidf": (tf @ tf.T).toarray()}

    # --- calibration on the topic reference set (modules with text, frame excluded) ---
    comp_txt = d.index[(d["side"] == "competitor") & ~d["names_only"] & (d["category"] != "frame")]
    emi_txt = d.index[(d["side"] == "emi") & (d["category"] != "frame")]
    # The decision uses the BEST of many EMI candidates, so calibrate on best-match scores, not single pairs:
    # per competitor module, best score among same-topic EMI modules (positive) vs among other-topic ones (negative).
    tp = d["title"].map(topics)
    pos, neg = [], []
    calib = {}
    for name, s in sims.items():
        ps, ns = [], []
        for i in comp_txt:
            if not tp[i]:
                continue
            cand = comparison_set(d, d.at[i, "level"])
            same = [j for j in cand if tp[j] and tp[i] & tp[j]]
            other = [j for j in cand if tp[j] and not tp[i] & tp[j]]
            if same:
                ps.append(s[i, same].max())
            if other:
                ns.append(s[i, other].max())
        calib[name] = youden(np.array(ps), np.array(ns))
        pos, neg = ps, ns
    tau = {k: v[0] for k, v in calib.items()}

    # --- best EMI match for every competitor module ---
    comp = d.index[(d["side"] == "competitor") & (d["category"] != "frame")].to_numpy()
    bm = best_matches(d, sims, comp)
    d = d.join(bm)
    for name in sims:
        d[f"{name}_covered"] = d[f"{name}_score"] >= tau[name]
    sec = d.index[(d["category"] == "security")].to_numpy()
    ka = assign_cybok(d, emb, sec)
    d.loc[sec, "cybok"], d.loc[sec, "cybok_how"] = ka["cybok"], ka["cybok_how"]

    # incrementality: coverage by the two EMI programmes with an Informationssicherheit focus
    iimi = d.index[d["programme_id"].isin(["oth_ba_ii", "oth_ba_mi"]) & (d["category"] != "frame")].to_numpy()
    d.loc[comp, "e5_iimi_score"] = sims["e5"][np.ix_(comp, iimi)].max(axis=1)
    d["e5_iimi_covered"] = d["e5_iimi_score"] >= tau["e5"]

    SCORES.parent.mkdir(parents=True, exist_ok=True)
    keep = ["programme_id", "level", "title", "category", "ects", "ects_used", "ects_imputed", "ot", "cybok", "cybok_how", "names_only",
            "e5_score", "e5_match", "e5_covered", "tfidf_score", "tfidf_match", "tfidf_covered", "e5_iimi_score", "e5_iimi_covered",
            "source_file", "page"]
    d[keep].to_csv(SCORES, index_label="row")

    text_rows = d.loc[comp][~d.loc[comp, "names_only"]]
    agree = (text_rows["e5_covered"] == text_rows["tfidf_covered"]).mean()

    cov_e5, cov_tf = coverage_table(d, "e5_covered"), coverage_table(d, "tfidf_covered")
    cov_iimi = coverage_table(d, "e5_iimi_covered")
    head = []
    for lv in ("BA", "MA"):
        for cat in ("security", "general"):
            head.append({"competitor level": lv, "modules": cat,
                         "EMI covers (e5), median %": cov_e5.loc[cov_e5.level == lv, f"{cat} covered %"].median(),
                         "range %": f"{cov_e5.loc[cov_e5.level == lv, f'{cat} covered %'].min()}-{cov_e5.loc[cov_e5.level == lv, f'{cat} covered %'].max()}",
                         "TF-IDF, median %": cov_tf.loc[cov_tf.level == lv, f"{cat} covered %"].median(),
                         "Industrie-4.0-Inf. + Medieninf. only (e5), median %": cov_iimi.loc[cov_iimi.level == lv, f"{cat} covered %"].median()})
    head = pd.DataFrame(head)

    # --- CyBOK table (security modules with text, competitors) ---
    cs = d.loc[sec][(d.loc[sec, "side"] == "competitor")]
    cs_txt = cs[~cs["names_only"]]
    emi_sec = d.loc[sec][d.loc[sec, "side"] == "emi"]
    ka_rows = []
    for ka, g in cs_txt.groupby("cybok"):
        ects_prog = g.groupby("programme_id")["ects_used"].sum()
        gaps = g[~g["e5_covered"]]
        ka_rows.append({"CyBOK knowledge area": ka, "competitor programmes (of 7)": g["programme_id"].nunique(),
                        "modules": len(g), "median ECTS per programme": ects_prog.median(),
                        "covered by EMI (e5) %": round(g.loc[g["e5_covered"], "ects_used"].sum() / g["ects_used"].sum() * 100),
                        "OT/industrial modules": int(g["ot"].sum()),
                        "EMI security modules in this area": "; ".join(short(t, 40) for t in emi_sec.loc[emi_sec["cybok"] == ka, "title"]) or "-",
                        "example gaps": "; ".join(f"{short(t, 45)} ({p.split('_')[0].upper()})" for t, p in zip(gaps["title"][:3], gaps["programme_id"][:3])) or "-"})
    ka_tab = pd.DataFrame(ka_rows).sort_values(["competitor programmes (of 7)", "median ECTS per programme"], ascending=False)
    ot = cs_txt[cs_txt["ot"]][["programme_id", "title", "ects_used", "cybok", "e5_covered"]]
    title_only = d.loc[comp][d.loc[comp, "names_only"]][["programme_id", "title", "category", "ot", "cybok", "e5_covered"]]
    dis = text_rows[text_rows["e5_covered"] != text_rows["tfidf_covered"]]
    dis_tab = pd.DataFrame({"programme": dis["programme_id"], "module": dis["title"].map(lambda t: short(t, 60)), "category": dis["category"],
                            "e5": dis["e5_covered"].map({True: "covered", False: "gap"}), "e5 score": dis["e5_score"].round(3),
                            "TF-IDF": dis["tfidf_covered"].map({True: "covered", False: "gap"}), "TF-IDF score": dis["tfidf_score"].round(3),
                            "best EMI match (e5)": [short(d.at[int(k), "title"], 45) for k in dis["e5_match"]]})

    cal = pd.DataFrame([{"method": k, "threshold": round(v[0], 3), "TPR": round(v[1], 2), "FPR": round(v[2], 2), "AUC": round(v[3], 3)}
                        for k, v in calib.items()])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Module gap analysis (generated)", "",
        f"Competitor modules compared: {len(comp)} (frame modules excluded; {int(d.loc[comp, 'names_only'].sum())} names-only). "
        f"Calibration (best-match level): {len(pos)} competitor modules with a same-topic EMI module, {len(neg)} with an other-topic one.", "",
        "## Calibration", "", _md(cal), "",
        f"Agreement e5 vs TF-IDF on covered/gap (modules with text): {agree * 100:.1f} % ({len(text_rows)} modules).", "",
        "## Headline: ECTS-weighted coverage", "", _md(head), "",
        "### Per competitor programme (e5)", "", _md(cov_e5), "", "### Per competitor programme (TF-IDF)", "", _md(cov_tf), "",
        "## Gaps by CyBOK knowledge area (competitor security modules with text)", "", _md(ka_tab), "",
        "## OT/industrial security modules (competitors)", "", _md(ot), "",
        "## Names-only programmes (indicative, title-based)", "", _md(title_only), "",
        "## Disagreements e5 vs TF-IDF", "", _md(dis_tab), ""]), encoding="utf-8")

    # --- 20-pair check: 10 near the threshold, 5 clearly covered, 5 clearly gap (e5) ---
    pool = text_rows.assign(dist=(text_rows["e5_score"] - tau["e5"]).abs())
    near = pool.nsmallest(10, "dist")
    rest = pool.drop(near.index)
    hi, lo = rest.nlargest(5, "e5_score"), rest.nsmallest(5, "e5_score")
    rows = []
    for grp, part in (("near threshold", near), ("clearly covered", hi), ("clearly gap", lo)):
        for i, r in part.iterrows():
            j = int(r["e5_match"])
            t_pair = float(sims["tfidf"][i, j])  # TF-IDF verdict on the SAME pair, so one hand label grades both methods
            rows.append({"#": len(rows) + 1, "group": grp, "e5 score": round(r["e5_score"], 3), "e5 says": "covered" if r["e5_covered"] else "gap",
                         "TF-IDF score (same pair)": round(t_pair, 3), "TF-IDF says": "covered" if t_pair >= tau["tfidf"] else "gap",
                         "competitor module": f"{short(r['title'], 70)} ({r['programme_id']}, {Path(r['source_file']).name} p{int(r['page'])})",
                         "competitor ECTS": d.at[i, "ects"] if pd.notna(d.at[i, "ects"]) else "-",
                         "competitor text (first 300)": excerpt(d.at[i, "clean"]),
                         "best EMI module": f"{short(d.at[j, 'title'], 70)} ({d.at[j, 'programme_id']}, {Path(d.at[j, 'source_file']).name} p{int(d.at[j, 'page'])})",
                         "EMI ECTS": d.at[j, "ects"] if pd.notna(d.at[j, "ects"]) else "-",
                         "EMI text (first 300)": excerpt(d.at[j, "clean"])})
    CHECK.write_text("\n".join([
        "# Step 41 check: 20 competitor/EMI pairs (generated)", "",
        f"Thresholds: e5 {tau['e5']:.3f}, TF-IDF {tau['tfidf']:.3f}. For each pair: does the EMI module really cover "
        "the competitor module's topic? (yes/no)", "",
        _md(pd.DataFrame(rows)), ""]), encoding="utf-8")
    print(cal.to_string(index=False))
    print(f"agreement {agree * 100:.1f} % | modules with same-topic best match {len(pos)}, other-topic {len(neg)}")
    print(head.to_string(index=False))
    print(f"Written: {SCORES.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}, {CHECK.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
