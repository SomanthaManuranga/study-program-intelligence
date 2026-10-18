"""Number splitting for statistical PDF tables (transform/pdf_numbers.py)."""

from study_program_intelligence.transform.pdf_numbers import split, tokens


def test_tokens_keep_placeholders_and_digit_runs():
    assert tokens("12 345 - 6 x 789.") == ["12", "345", "-", "6", "x", "789", "."]


def test_thousands_separators_resolved_by_row_arithmetic():
    # "1 000 600 400" as three columns where total = part1 + part2
    assert split(tokens("1 000 600 400"), 3, lambda g: g[0] == g[1] + g[2]) == [[1000, 600, 400]]


def test_glued_numbers_are_cut_at_three_digits():
    # extracted text glues "19" onto "646": 39 646 | 19 646 | 20 000
    assert split(tokens("39 64619 646 20 000"), 3, lambda g: g[0] == g[1] + g[2]) == [[39646, 19646, 20000]]


def test_no_split_when_the_check_cannot_hold():
    assert split(tokens("10 20 31"), 3, lambda g: g[0] == g[1] + g[2]) == []


def test_extra_cut_found_when_needed():
    # "663 438 982" = 663 | 4 | 38 982 (one extra cut inside "438")
    found = split(tokens("663 438 982"), 3, lambda g: g[2] > 1000)
    assert [663, 4, 38982] in found
