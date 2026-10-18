## A1 Data sources and access {-}

<!-- Generated table from configs/sources.yaml; edit the register, not this file. -->

The data sources used in this report, as registered in `configs/sources.yaml`. Automated downloads are recorded with their
date and, for downloaded files, URL and SHA-256 checksum in the manifests in `docs/` (for example
`docs/competitor_modules_manifest.json`, `docs/regional_manifest.json`); manual downloads (EMI module handbooks,
Google Trends files) are listed in the register only.

{{table:sources}}

**Not used, by access rule.** The federal-state regional database (robots.txt disallows all automated access),
the Bavarian GENESIS web service (the login fell back to guest access), OTH staff profile pages (blocked for AI
crawlers; skipped on principle), the TH Mannheim module handbook (robots.txt), and the THI robotics and TH Augsburg
robotics module handbooks (no longer reachable). No blocked or login-protected source was circumvented; where a page was blocked for scripts we used only another
permitted route (the Hochschulkompass data through the BA Studiensuche API, TH Mannheim's module list from its programme
page) or downloaded the public file by hand (the EMI module handbooks under OTH's /fileadmin/, which robots.txt closes
to scripts).
