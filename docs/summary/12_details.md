# 12. Where to find the details

<!-- Plain English. Paths are relative to the project repository. -->

Everything in this summary can be traced and rebuilt. The project repository is
github.com/SomanthaManuranga/study-program-intelligence.

| What you want | Where it is |
|------------------------|------------------------------------------------------------|
| The full technical report | built by the pipeline to `reports/final/report.pdf`; its texts are in `docs/report/` |
| The evidence for each finding | `docs/evidence_*.md`, several documents per question |
| Every method decision, most with the reason | `docs/decision_log.md` |
| The rules written in advance | `docs/kill_rules.md` and `configs/analysis.yaml` |
| Where each number comes from | `reports/key_numbers.yaml`, built from the evidence documents |
| All data sources | `configs/sources.yaml` |
| Answers to likely questions | `docs/defence_qa.md` |
| An interactive version | the dashboard: `streamlit run app/dashboard.py` |

To rebuild every number, figure and document, run one command:
`python -m study_program_intelligence.pipeline`. It needs the files we downloaded by hand to be in place; the README
explains the set-up.
