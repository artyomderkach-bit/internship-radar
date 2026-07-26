"""The sophomore-confidence score must stay honest.

Two invariants:
  1. Every hand-entered id in eligibility's tables refers to a real programme — a typo'd
     id silently becomes a no-op and the row keeps a flattering default.
  2. The default scores are derived from what we already know and are NEVER more
     optimistic than the evidence: ineligible pins to the floor, unverified sits below
     the confirmed band.
"""

from radar.eligibility import (
    CODING_PREFERRED,
    CODING_REQUIRED,
    GRAD_ELIGIBLE,
    GRAD_INELIGIBLE,
    SOPH_SCORE,
    soph_score,
)
from radar.registry import build


def all_ids() -> set[str]:
    return {p["id"] for p in build()}


def test_every_eligibility_id_is_a_real_programme():
    ids = all_ids()
    for table_name, table in [
        ("SOPH_SCORE", SOPH_SCORE),
        ("GRAD_ELIGIBLE", GRAD_ELIGIBLE),
        ("GRAD_INELIGIBLE", GRAD_INELIGIBLE),
        ("CODING_REQUIRED", CODING_REQUIRED),
        ("CODING_PREFERRED", CODING_PREFERRED),
    ]:
        unknown = set(table) - ids
        assert not unknown, (
            f"{table_name} has ids that match no programme (typo?): {sorted(unknown)}"
        )


def test_scores_are_bounded_and_carry_a_basis():
    for p in build():
        assert 0 <= p["soph_score"] <= 100, p["id"]
        assert p["soph_score_basis"].strip(), f"{p['id']} has a score with no basis"


def test_default_scores_never_flatter():
    # Verified-out is pinned to the floor.
    score, _ = soph_score("nonexistent", "ineligible", "claimed")
    assert score < 10
    # A bare curated claim must sit below the confirmed band...
    claimed, _ = soph_score("nonexistent", "unverified", "claimed")
    confirmed, _ = soph_score("nonexistent", "unverified", "confirmed")
    verified, _ = soph_score("nonexistent", "eligible", "claimed")
    assert claimed < 50 <= confirmed <= verified
    # ...and doubtful prose drags it further down.
    doubtful, _ = soph_score("nonexistent", "unverified", "doubtful")
    assert doubtful < claimed


def test_explicit_research_outranks_the_default():
    if not SOPH_SCORE:
        return  # table not yet populated — the defaults above still hold
    for pid, (score, basis) in SOPH_SCORE.items():
        assert 0 <= score <= 100, pid
        assert basis.strip(), pid
        assert soph_score(pid, "unverified", "claimed") == (score, basis)
