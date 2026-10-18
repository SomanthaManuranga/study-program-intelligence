# 12. Where to find the details

<!-- Plain English. Paths are relative to the project repository. -->

Everything here can be traced and rebuilt from github.com/SomanthaManuranga/study-program-intelligence.

| What you want | Where it is |
|----------------------------------|------------------------------------------------------|
| The full technical report | built by the pipeline to `reports/final/report.pdf`; its texts are in `docs/report/` |
| The evidence for each finding | `docs/evidence_*.md`, several documents per question |
| Method decisions, most with reasons | `docs/decision_log.md` |
| The rules written in advance | `docs/kill_rules.md` and `configs/analysis.yaml` |
| Source of each number | `reports/key_numbers.yaml`, built from the evidence documents |
| All data sources | `configs/sources.yaml` |
| Answers to likely questions | `docs/defence_qa.md` |
| An interactive version | the dashboard: `streamlit run app/dashboard.py` |
| Rebuild everything | `python -m study_program_intelligence.pipeline`, once the files downloaded by hand are in place (README) |
