"""Download the public documents listed in configs/documents.yaml.

Run from the repository root:

    python -m study_program_intelligence.ingest.documents            # download missing files
    python -m study_program_intelligence.ingest.documents --force    # re-download everything
    python -m study_program_intelligence.ingest.documents --only hrk_statistik_ws_2025_26
    python -m study_program_intelligence.ingest.documents --config configs/competitor_modules.yaml \
        --out "data/raw/competitor modules" --manifest docs/competitor_modules_manifest.json --pdf-only

Rules this script follows:
- checks each site's robots.txt and skips a URL the site disallows (a missing robots.txt, 4xx, counts as no
  restrictions declared; a server error or an unreachable robots.txt counts as blocked, retry later);
- identifies itself with a User-Agent that includes CONTACT_EMAIL from .env;
- waits between requests (3 s, or the site's robots.txt Crawl-delay if longer) and never re-downloads a file;
- records URL, retrieval time, size and SHA-256 for every file;
- with --pdf-only, rejects (and deletes) any reply that is not a PDF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "documents.yaml"
OUT_DIR = REPO_ROOT / "data" / "raw" / "documents"
MANIFEST = REPO_ROOT / "docs" / "download_manifest.json"
DELAY_SECONDS = 3
TIMEOUT_SECONDS = 60


def load_env(path: Path) -> None:
    """Read KEY=VALUE lines from .env into os.environ (no extra dependency)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.split("#", 1)[0].strip())


def user_agent() -> str:
    contact = os.environ.get("CONTACT_EMAIL", "").strip()
    base = "study-program-intelligence/0.1 (student research project, OTH Amberg-Weiden"
    return f"{base}; contact: {contact})" if contact else f"{base})"


_robots_cache: dict[str, robotparser.RobotFileParser | None] = {}
_BLOCK_ALL = robotparser.RobotFileParser()
_BLOCK_ALL.parse(["User-agent: *", "Disallow: /"])


def allowed_by_robots(url: str, agent: str) -> bool:
    parts = urlparse(url)
    root = f"{parts.scheme}://{parts.netloc}"
    if root not in _robots_cache:
        rp = robotparser.RobotFileParser()
        try:
            resp = requests.get(f"{root}/robots.txt", headers={"User-Agent": agent}, timeout=TIMEOUT_SECONDS)
            if 400 <= resp.status_code < 500:
                rp = None  # no robots.txt (4xx): no restrictions declared
            elif resp.status_code >= 500:
                rp = _BLOCK_ALL  # server error: treat as blocked rather than assume permission
            else:
                rp.parse(resp.text.splitlines())
        except requests.RequestException:
            rp = _BLOCK_ALL  # robots.txt unreachable: treat as blocked rather than assume permission
        _robots_cache[root] = rp
        time.sleep(delay_for(url, agent))  # robots.txt and the file are two requests to the same host
    rp = _robots_cache[root]
    return True if rp is None else rp.can_fetch(agent, url)


def delay_for(url: str, agent: str) -> float:
    """Seconds to wait between requests to this host: our 3 s, or the site's Crawl-delay if longer."""
    parts = urlparse(url)
    rp = _robots_cache.get(f"{parts.scheme}://{parts.netloc}")
    site = rp.crawl_delay(agent) if rp is not None else None
    return max(DELAY_SECONDS, float(site or 0))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def target_path(doc: dict, out_dir: Path = OUT_DIR) -> Path:
    suffix = Path(urlparse(doc["url"]).path).suffix.lower() or ".bin"
    return out_dir / f"{doc['id']}{suffix}"


def download(doc: dict, agent: str, force: bool, out_dir: Path = OUT_DIR, pdf_only: bool = False) -> dict:
    dest = target_path(doc, out_dir)
    record = {
        "id": doc["id"],
        "owner": doc.get("owner"),
        "title": doc.get("title"),
        "url": doc["url"],
        "mirror": bool(doc.get("mirror", False)),
        "file": dest.relative_to(REPO_ROOT).as_posix(),
    }
    record.update({k: doc[k] for k in ("programme", "version", "page") if k in doc})

    if dest.exists() and not force:
        record.update(status="cached", bytes=dest.stat().st_size, sha256=sha256(dest))
        return record

    if not allowed_by_robots(doc["url"], agent):
        record.update(status="skipped_robots")
        return record

    try:
        resp = requests.get(doc["url"], headers={"User-Agent": agent}, timeout=TIMEOUT_SECONDS, stream=True)
    except requests.RequestException as exc:
        record.update(status="error", error=str(exc))
        return record

    if resp.status_code != 200:
        record.update(status="error", error=f"HTTP {resp.status_code}")
        return record

    tmp = dest.with_suffix(dest.suffix + ".part")
    with tmp.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=1 << 16):
            fh.write(chunk)
    with tmp.open("rb") as fh:
        is_pdf = fh.read(5) == b"%PDF-"
    if pdf_only and not is_pdf:
        tmp.unlink()
        record.update(status="error", error=f"not a PDF ({resp.headers.get('Content-Type')})")
        return record
    tmp.replace(dest)

    record.update(
        status="downloaded",
        retrieved_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        content_type=resp.headers.get("Content-Type"),
        bytes=dest.stat().st_size,
        sha256=sha256(dest),
    )
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="re-download files that already exist")
    parser.add_argument("--only", nargs="*", default=None, help="document ids to fetch")
    parser.add_argument("--config", type=Path, default=CONFIG, help="YAML with a 'documents' list")
    parser.add_argument("--out", type=Path, default=OUT_DIR, help="output folder")
    parser.add_argument("--manifest", type=Path, default=MANIFEST, help="manifest JSON to write")
    parser.add_argument("--pdf-only", action="store_true", help="reject replies that are not PDFs")
    args = parser.parse_args(argv)
    config, out_dir, manifest = (p if p.is_absolute() else REPO_ROOT / p for p in (args.config, args.out, args.manifest))

    load_env(REPO_ROOT / ".env")
    agent = user_agent()
    docs = yaml.safe_load(config.read_text(encoding="utf-8"))["documents"]
    if args.only:
        docs = [d for d in docs if d["id"] in set(args.only)]

    out_dir.mkdir(parents=True, exist_ok=True)

    previous = {}
    if manifest.exists():
        previous = {r["id"]: r for r in json.loads(manifest.read_text(encoding="utf-8"))}

    results = []
    for i, doc in enumerate(docs):
        rec = download(doc, agent, args.force, out_dir, args.pdf_only)
        if rec["status"] == "cached" and doc["id"] in previous:
            # keep the original retrieval time for files we did not fetch again
            rec["retrieved_utc"] = previous[doc["id"]].get("retrieved_utc")
        results.append(rec)
        size = f"{rec.get('bytes', 0) / 1024:,.0f} KB" if rec.get("bytes") else ""
        print(f"[{rec['status']:>15}] {doc['id']:<40} {size} {rec.get('error', '')}")
        if rec["status"] != "cached" and i < len(docs) - 1:
            time.sleep(delay_for(doc["url"], agent))  # after every network attempt (site Crawl-delay if longer)

    merged = {**previous, **{r["id"]: r for r in results}}
    manifest.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nManifest written to {manifest.relative_to(REPO_ROOT).as_posix()}")

    failed = [r for r in results if r["status"] in {"error", "skipped_robots"}]
    if failed:
        print(f"{len(failed)} document(s) not downloaded. See the status column above.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
