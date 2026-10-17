"""Build the shared report material in one go (Step 50): key numbers -> figures -> outline.

Run from the repository root after the analysis modules (data/interim must be current):

    python -m study_program_intelligence.report.build
"""

from __future__ import annotations

from . import figures, key_numbers, outline


def main() -> None:
    key_numbers.main()
    figures.main()
    outline.main()


if __name__ == "__main__":
    main()
