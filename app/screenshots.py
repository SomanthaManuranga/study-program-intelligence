"""Screenshots of every dashboard page as a backup for the presentation (Step 52).

Start the dashboard first (streamlit run app/dashboard.py), then, from the repository root:

    python app/screenshots.py [base_url]

Uses a locally installed Chrome or Edge in headless mode with a throw-away profile (the normal browser profile is not
touched). Output: reports/figures/dashboard/NN_<page>.png at 1440 px width.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reports" / "figures" / "dashboard"
PAGES = [("", "overview", 1150), ("demand", "demand", 2050), ("capture", "capture", 1750), ("fit", "fit", 1300),
         ("outlet", "outlet", 1700), ("cannibalisation", "cannibalisation", 1650), ("ranking", "ranking", 2200),
         ("sources", "sources", 3400)]
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "google-chrome", "chromium", "msedge"]


def browser() -> str:
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b
    sys.exit("No Chrome or Edge found for headless screenshots.")


def main() -> None:
    base = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501").rstrip("/")
    OUT.mkdir(parents=True, exist_ok=True)
    exe = browser()
    with tempfile.TemporaryDirectory() as profile:
        for i, (path, name, height) in enumerate(PAGES):
            out = OUT / f"{i:02d}_{name}.png"
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                            f"--window-size=1440,{height}", "--virtual-time-budget=20000", f"--screenshot={out}",
                            f"{base}/{path}"], check=True, capture_output=True, timeout=120)
            print(f"Written: {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
