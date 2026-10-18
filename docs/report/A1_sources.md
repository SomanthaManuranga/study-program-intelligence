## A1 Data sources and access {-}

<!-- Generated table from configs/sources.yaml; edit the register, not this file. -->

The data sources used in this report, as registered in `configs/sources.yaml`. Downloads are recorded with their date
and, for downloaded files, URL and SHA-256 checksum in the manifests in `docs/` (for example
`docs/competitor_modules_manifest.json`, `docs/regional_manifest.json`).

{{table:sources}}

**Not used, by access rule.** The federal-state regional database (robots.txt disallows all automated access),
the Bavarian GENESIS web service (the login fell back to guest access), OTH staff profile pages (blocked for AI
crawlers; skipped on principle), the TH Mannheim module handbook (robots.txt), and the THI robotics and TH Augsburg
robotics module handbooks (no longer reachable). No blocked or login-protected source was circumvented; where a page was blocked we used only another permitted
route (the Hochschulkompass data through the BA Studiensuche API, TH Mannheim's module list from its programme page).
