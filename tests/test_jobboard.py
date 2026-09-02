"""Direct job-board checkers (Ashby / Greenhouse).

Unlike the community mirror, these MAY report a negative — a firm's own board is
authoritative about that firm's own postings. That power is exactly why the guards matter:
a board that fails to load must not read as "they aren't hiring students".
"""

import pytest

from radar.checkers.jobboard import _decide

KEY = "ashby:test"


def rows(*titles, type_=None):
    return [{"title": t, "url": f"http://x/{i}", "type": type_}
            for i, t in enumerate(titles)]


def test_a_usable_student_role_is_an_opening_at_high_confidence():
    res = _decide(rows("Summer Analyst Intern 2027", "Chef", "Lawyer"), {"year": 2027}, KEY)
    assert res.open is True
    # A firm's own board is authoritative, unlike a community list.
    assert res.confidence == "high"


def test_no_student_roles_is_a_real_negative():
    res = _decide(rows("Chef", "Lawyer", "Plumber"), {"year": 2027}, KEY)
    assert res.ok is True and res.open is False


def test_a_collapsed_board_fails_rather_than_reporting_nobody_is_hiring():
    """The whole point of canary_min: 0 rows from a 60-role board is an outage."""
    res = _decide(rows("Chef"), {"canary_min": 10}, KEY)
    assert res.ok is False
    assert res.open is None
    assert "board_too_small" in res.error


def test_coding_student_roles_are_not_reported_as_openings():
    res = _decide(rows("Software Engineer Intern", "Data Science Intern"),
                  {"year": 2027, "canary_min": 1}, KEY)
    assert res.open is None, "a coding internship is not an opening for him"
    assert "coding" in res.evidence


def test_a_different_cycle_is_not_this_cycle():
    """Polymarket's live posting is the 2026 programme — real, but last year's."""
    res = _decide(rows("Polymarket 2026 Summer Internship — Marketing & Finance"),
                  {"year": 2027, "canary_min": 1}, KEY)
    assert res.open is None
    assert "different cycle" in res.evidence


def test_campus_recruiter_is_a_job_hiring_students_not_a_job_for_one():
    res = _decide(rows("Campus Recruiter", "Chef", "Lawyer"), {"year": 2027}, KEY)
    assert res.open is False, "hiring a recruiter is not an internship opening"


def test_employment_type_counts_even_when_the_title_is_plain():
    res = _decide(rows("Markets Associate", "Chef", "Lawyer", type_="Intern"),
                  {"year": 2027}, KEY)
    assert res.open is True


def test_international_is_not_an_intern():
    """2026-09-01: "Performance Marketing Lead, International" put Polymarket in the ACT
    NOW rail because "intern" matched as a substring. Word boundaries, not substrings."""
    res = _decide(rows("Performance Marketing Lead, International", "Chef", "Lawyer"),
                  {"year": 2027}, KEY)
    assert res.open is False, "a Lead role is not a student posting"


def test_plural_and_stemmed_intern_titles_still_match():
    from radar.matching import looks_like_intern
    assert looks_like_intern("Summer Interns — Trading")
    assert looks_like_intern("2027 Internships, Houston")
    assert looks_like_intern("Undergraduate Analyst Program")
    assert not looks_like_intern("International Tax Manager")
    assert not looks_like_intern("Internal Audit Manager")
