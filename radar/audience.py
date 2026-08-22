"""Who sees which programme — the single place board membership is decided.

Two boards, one pipeline. Artyom's board is the original radar (energy / finance /
consulting, quant rows included). His twin sister's board is HR & Talent ONLY — human
capital, people strategy, executive search, recruiting. Artyom, 2026-08-22: her doors
must be "hr or headhunting related [or] anything a psychology major would do in finance
or energy — not finance or energy roles". The people-work seats AT finance and energy
firms (a Phillips 66 or iCapital HR internship) qualify, and those are curated as
`HR & Talent` rows already; a trading or corp-finance seat never does.

She is his twin, so the class-of-2029 arithmetic is IDENTICAL: Summer 2027 is her
sophomore summer too, and every `grad_2029` verdict carries over unchanged.

The override sets below exist for the cases where the sector rule is wrong for one
specific id — e.g. a people-analytics seat curated under Finance that she should see.
List the id and the reason, same discipline as `eligibility.py`.
"""

from __future__ import annotations

# Her own sector. Rows here are curated FOR her and never shown to Artyom.
SISTER_SECTOR = "HR & Talent"

# Rule says one thing, a human decided otherwise. id -> reason, audited like eligibility.
SISTER_INCLUDE: dict[str, str] = {}
SISTER_EXCLUDE: dict[str, str] = {}


def for_artyom(prog: dict) -> bool:
    """Everything except his sister's HR & Talent rows — his 97 stay exactly his 97."""
    return prog["sector"] != SISTER_SECTOR


def for_sister(prog: dict) -> bool:
    if prog["id"] in SISTER_EXCLUDE:
        return False
    if prog["id"] in SISTER_INCLUDE:
        return True
    return prog["sector"] == SISTER_SECTOR
