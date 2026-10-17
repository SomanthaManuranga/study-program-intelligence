"""Split a row of numbers from statistical PDF tables where spaces are both thousands separators and column gaps.

Used by transform/school_leavers.py and analysis/labour.py. A row is split into n numbers so that a caller-supplied
check (the table's own arithmetic, e.g. "total = sum of parts") holds. Extracted text sometimes glues numbers
("9 04718 694" = 9 047 | 18 694; "663 438 982" = 663 | 4 | 38 982); digit tokens may therefore be cut. A piece
either starts a number (1-3 digits, no leading zero) or continues one (exactly 3 digits). Fewest extra cuts first;
all valid splits at that level are returned, so callers can resolve ties with a higher-level check.
"""

from __future__ import annotations

import re
from typing import Callable


def tokens(text: str) -> list[str]:
    """Digit runs and placeholders ('-', '.', 'x'); a dash glued to a number ("-14 405") becomes its own token."""
    return re.findall(r"\d+|[-.x]", text)


def _pieces(t: str, max_cuts: int):
    yield [t]
    if max_cuts:
        for k in range(1, len(t)):
            for rest in _pieces(t[k:], max_cuts - 1):
                yield [t[:k]] + rest


def split(toks: list[str], n: int, check: Callable[[list[int]], bool], max_cuts: int = 3) -> list[list[int]]:
    tok = []
    for t in toks:  # regular glue first: a token longer than 3 digits = end of a number (3 digits) + more
        t = "0" if t in ("-", ".", "x") else t
        while re.fullmatch(r"\d{4,}", t):
            tok.append(t[:3])
            t = t[3:]
        tok.append(t)

    def place(pcs: list[str], nums: tuple[str, ...]):
        if not pcs:
            yield nums
            return
        p, rest = pcs[0], pcs[1:]
        if nums and re.fullmatch(r"\d{3}", p):
            yield from place(rest, nums[:-1] + (nums[-1] + p,))
        if re.fullmatch(r"0|[1-9]\d{0,2}", p) and len(nums) < n:
            yield from place(rest, nums + (p,))

    def search(i: int, nums: tuple[str, ...], cuts: int):
        if i == len(tok):
            if len(nums) == n:
                g = [int(x) for x in nums]
                if check(g):
                    yield g
            return
        for pcs in _pieces(tok[i], cuts):
            for nxt in place(pcs, nums):
                yield from search(i + 1, nxt, cuts - (len(pcs) - 1))

    for c in range(max_cuts + 1):
        found = {tuple(g) for g in search(0, (), c)}
        if found:
            return [list(g) for g in sorted(found)]
    return []
