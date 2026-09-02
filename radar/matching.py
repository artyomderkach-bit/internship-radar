"""Shared title matching, so every checker filters the same way.

Two jobs:

  is_coding_title  — Artyom does not write code. A "Software Engineer Intern" is not an
                     opening for him, and reporting one wastes an evening. Used by every
                     checker, not just the mirror, so the rule cannot drift between them.
  looks_like_intern— what counts as a student role at all.

Kept deliberately blunt. A false "this is a coding job" merely hides a row he could have
seen; a false "this is for you" sends him at something he cannot do. The asymmetry says
which way to lean.
"""

from __future__ import annotations

import re

CODING_TITLE = (
    "software", "swe", "developer", "engineer", "engineering", "machine learning",
    "data scien", "data engineer", "quantitative research", "quant research",
    "infrastructure", "systems", "platform", "fpga", "hardware", "devops", "security",
    "full stack", "backend", "front end", "frontend", "ml ", "ai/ml", "site reliability",
    "programmer", "architect", "ios", "android", "mobile",
)

# Words that mean "student/early-career role", used when a board has no employmentType.
# Matched on word boundaries, not substrings: "Performance Marketing Lead, International"
# put Polymarket's row in the ACT NOW rail on 2026-09-01 because "intern" is a substring
# of "International". The stems below still cover interns/internships/undergraduate.
INTERN_RE = re.compile(
    r"\b(?:"
    r"intern(?:ship)?s?"
    r"|co-?op"
    r"|summer analyst"
    r"|campus"
    r"|university"
    r"|student"
    r"|new grad"
    r"|sophomore"
    r"|first-year"
    r"|freshman"
    r"|undergrad(?:uate)?"
    r")\b"
)

# "Campus Recruiter" is a full-time job hiring students, not a job FOR one.
NOT_ACTUALLY_STUDENT = ("recruiter", "recruiting manager", "campus lead", "program manager")


def is_coding_title(title: str) -> bool:
    return any(frag in (title or "").lower() for frag in CODING_TITLE)


def looks_like_intern(title: str, employment_type: str | None = None) -> bool:
    low = (title or "").lower()
    if any(bad in low for bad in NOT_ACTUALLY_STUDENT):
        return False
    if employment_type and "intern" in employment_type.lower():
        return True
    return bool(INTERN_RE.search(low))


def wrong_season(title: str, want_year: str = "2027") -> bool:
    """True when a title names a different cycle than the one we're tracking.

    Polymarket's live posting is "Polymarket 2026 Summer Internship" — real, but last
    year's. Treating it as a 2027 opening would be a false alarm every single run.
    """
    low = (title or "").lower()
    other = {"2024", "2025", "2026", "2028"} - {want_year}
    return any(y in low for y in other) and want_year not in low
