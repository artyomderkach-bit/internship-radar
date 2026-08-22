"""Who sees which programme — the single place board membership is decided.

Two boards, one pipeline. Artyom's board is the original radar (energy / finance /
consulting, quant rows included). His twin sister's board is HR & Talent — human capital,
people strategy, executive search, recruiting — plus the finance and energy doors she can
actually use: NYC/Houston rows that are not quant/trading seats.

She is his twin, so the class-of-2029 arithmetic is IDENTICAL: Summer 2027 is her
sophomore summer too, and every `grad_2029` verdict carries over unchanged.

Rules are derived from fields the seed already carries (`sector`, `loc_bucket`,
`quant_role`) so a new curated row lands on the right board with no extra bookkeeping.
The override sets below exist for the cases where the rule is wrong for one specific id —
list the id and the reason, same discipline as `eligibility.py`.
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
    if prog["sector"] == SISTER_SECTOR:
        return True
    # Shared doors: finance and energy where she'd actually go (NYC / Houston),
    # minus quant/trading seats — those recruit a profile she isn't selling.
    return (prog["sector"] in ("Finance", "Energy")
            and prog["loc_bucket"] in ("Houston", "NYC")
            and not prog.get("quant_role", False))
