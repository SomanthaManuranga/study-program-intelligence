"""Module gap analysis: competitor cybersecurity modules vs EMI modules (Step 41).

WORK IN PROGRESS (paused 17 Oct 2026): main() only prints calibration statistics so far. The title-based
calibration below does not separate positives from random pairs; see CLAUDE.md "Where we stopped".

Run from the repository root:

    python -m study_program_intelligence.analysis.module_gaps

Method (decision log 2026-10-17)
- Text: content and learning outcomes of each module (form fields and literature removed),
  title prepended. Names-only sources (HS Aalen, TH Mannheim) use the title.
- Categories: "security" (title, or dense security vocabulary in the content), "general"
  (maths, programming, systems, soft skills, ...) and "frame" (thesis, internship, placeholder
  electives), which is left out of the coverage shares.
- Similarity 1: intfloat/multilingual-e5-base, "query: " prefix (symmetric task), 200-word chunks,
  mean of the normalised chunk embeddings. Similarity 2 (cross-check): word TF-IDF (1-2 grams).
- Comparison: competitor bachelor modules vs EMI bachelor modules; competitor master modules vs
  EMI bachelor and master modules. A module is "covered" if its best EMI match >= threshold.
- Thresholds: calibrated per method on a reference set (competitor/EMI pairs with near-identical
  titles = positives; random competitor/EMI pairs = negatives; Youden's J).
- CyBOK 1.1 knowledge areas assigned to security modules by embedding similarity to short area
  descriptions; OT/industrial flag by keywords.
Outputs: data/interim/module_scores.csv, reports/module_gaps.md, reports/module_gaps_check.md.
"""

from __future__ import annotations

import difflib
import hashlib
import json
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
LITERATURE = re.compile(r"\b(Literatur(hinweise|liste|empfehlungen)?|Empfohlene Literatur|Literature|Recommended (reading|literature)|"
                        r"Reading list|Lehr- und Lernmaterialien)\b:?")
SEC = re.compile(r"secur|sicherheit|sichere[nrs]?\b|krypt|crypt|forensi|penetration|pentest|hacking|hacker|angriff|attack|malware|"
                 r"incident|intrusion|privacy|datenschutz|threat|bedrohung|vulnerab|schwachstell|exploit|firewall|authenti|"
                 r"zugriffskontrolle|access control|cyber(?!-?physi)|siem\b|\bsoc\b|resilien|abwehr|defen[cs]e|steganograph|"
                 r"anonymi|spionage|espionage|isms|bsi\b|iso ?27001|62443|compliance|it-recht|it law", re.I)
FRAME = re.compile(r"bachelorarbeit|masterarbeit|bachelor'?s? thesis|master'?s? thesis|\bthesis\b|masterthesis|bachelormodul|"
                   r"kolloquium|praxis(modul|phase|semester|seminar)|praktikum \(|praktisches studiensemester|internship|"
                   r"praxissemester|einführungsprojekt|allgemeines wahlpflichtmodul|studiengangsspezifische wahlpflichtmodule|"
                   r"wahlpflichtmodul projekt|vertiefungsmodul \d|praxisseminar|seminar bachelorarbeit|masterseminar|"
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
    from sentence_transformers import SentenceTransformer
    CACHE.mkdir(parents=True, exist_ok=True)
    keys = [hashlib.sha256(t.encode("utf-8")).hexdigest()[:20] for t in texts]
    todo = [(k, t) for k, t in zip(keys, texts) if not (CACHE / f"{k}.npy").exists()]
    if todo:
        model = SentenceTransformer(MODEL)
        for k, t in todo:
            parts = chunks(t)
            e = model.encode([f"query: {p}" for p in parts], normalize_embeddings=True, batch_size=16)
            v = e.mean(axis=0)
            np.save(CACHE / f"{k}.npy", v / np.linalg.norm(v))
    return np.vstack([np.load(CACHE / f"{k}.npy") for k in keys])


STOP = ("der die das und in zu den von mit für im ist sind des dem ein eine einer eines auf als auch an bei werden wird "
        "können kann sowie oder nach über durch zur zum aus wie sie es sich nicht dieser diese dieses studierenden "
        "modul moduls module the and of to in for a an is are on with by as be can or this that students student "
        "lernen kennen verstehen grundlagen basics fachkompetenz methodenkompetenz sozialkompetenz kompetenzen "
        "lernziele learning outcomes inhalte content contents nach erfolgreichen absolvieren verfügen über folgenden").split()


def tfidf_matrix(texts: list[str]) -> np.ndarray:
    from sklearn.feature_extraction.text import TfidfVectorizer
    v = TfidfVectorizer(lowercase=True, stop_words=STOP, ngram_range=(1, 2), min_df=2, max_df=0.4, sublinear_tf=True,
                        token_pattern=r"(?u)\b[a-zäöüß][a-zäöüß0-9\-]{2,}\b")
    x = v.fit_transform(texts)
    return x


def key_title(t: str) -> str:
    t = re.sub(r"^\[[^\]]*\]\s*|^[BM]-CY-\d+\s+|\(.*?\)", " ", t.lower())
    return re.sub(r"[^a-zäöüß0-9]+", " ", t).strip()


def load() -> pd.DataFrame:
    d = pd.read_csv(MODULES)
    d["names_only"] = ~d["text_source"].str.startswith("handbook")
    d["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(d["text"], d["title"])]
    d.loc[d["names_only"], "clean"] = d.loc[d["names_only"], "title"].map(lambda t: re.sub(r"^\d{5}\s+", "", t))
    d["category"] = [category(ti, c) for ti, c in zip(d["title"], d["clean"])]
    d["ot"] = d["clean"].map(lambda c: len(OT.findall(c))) >= 2
    d.loc[d["title"].str.contains(OT), "ot"] = True
    d["ects_used"] = pd.to_numeric(d["ects"], errors="coerce")
    d["ects_imputed"] = d["ects_used"].isna()
    d["ects_used"] = d["ects_used"].fillna(5.0)
    d["side"] = np.where(d["programme_id"].str.startswith("oth_"), "emi", "competitor")
    return d.reset_index(drop=True)


def main() -> None:
    d = load()
    emb = embed(d["clean"].tolist())
    tf = tfidf_matrix(d["clean"].tolist())
    np.save(REPO_ROOT / "data" / "interim" / "module_emb.npy", emb)
    sims = {"emb": emb @ emb.T, "tfidf": (tf @ tf.T).toarray()}
    comp = d.index[d["side"] == "competitor"]
    emi = d.index[d["side"] == "emi"]
    pos, neg = [], []
    rng = np.random.default_rng(SEED)
    kt = d["title"].map(key_title)
    for i in comp:
        if d.at[i, "names_only"]:
            continue
        for j in emi:
            r = difflib.SequenceMatcher(None, kt[i], kt[j]).ratio()
            if r >= 0.9 and len(kt[i]) >= 6:
                pos.append((i, j))
    pairs = set(pos)
    comp_text = [i for i in comp if not d.at[i, "names_only"]]
    while len(neg) < 3000:
        i, j = int(rng.choice(comp_text)), int(rng.choice(emi))
        if (i, j) not in pairs:
            neg.append((i, j))
    out = {}
    for name, s in sims.items():
        ps = np.array([s[i, j] for i, j in pos])
        ns = np.array([s[i, j] for i, j in neg])
        out[name] = {"pos_n": len(ps), "pos_q": np.quantile(ps, [0.05, 0.25, 0.5]).round(3).tolist(),
                     "neg_q": np.quantile(ns, [0.5, 0.95, 0.99]).round(3).tolist()}
    print(json.dumps(out, indent=1))
    print("categories:", d.groupby(["side", "category"]).size().to_dict())
    print("positives sample:", [(d.at[i, "title"][:30], d.at[j, "title"][:30]) for i, j in pos[:12]])


if __name__ == "__main__":
    main()
