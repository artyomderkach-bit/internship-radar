"""The honesty invariants.

If any test in this file starts failing, the tracker has become capable of telling Artyom
an application is closed when it isn't — which is the one failure that costs him a deadline.
Treat a failure here as a stop-the-line bug, not a flaky test.
"""

from datetime import datetime, timedelta, timezone

import pytest

from radar.models import (
    BLOCKED, CLOSED, LiveState, NOT_OPEN, OK, OPEN, Result, STATUSES, WATCH_ONLY,
)
from radar.state import apply, compute_health

NOW = datetime(2026, 8, 14, 13, 31, tzinfo=timezone.utc)

ERRORS = [
    "timeout", "403", "429", "connreset", "parse_error",
    "listing_collapsed", "canary_missing", "selector_empty", "dns_failure",
    "cloudflare_challenge", "unknown_error",
]


# --------------------------------------------------------------------- THE invariant
@pytest.mark.parametrize("status", STATUSES)
@pytest.mark.parametrize("error", ERRORS)
def test_failure_never_changes_status(status, error):
    """A failed check may degrade health. It may NEVER move status."""
    before = LiveState(id="x", status=status, first_seen_open="2026-08-01T00:00:00Z",
                       last_ok="2026-08-14T13:00:00Z")
    after = apply(before, Result.failed(error), NOW)
    assert after.status == before.status, f"{error} moved status off {status}"
    assert after.health != OK, f"{error} left health looking fine"
    assert after.failure_count == before.failure_count + 1


@pytest.mark.parametrize("error", ERRORS)
def test_failure_never_produces_closed(error):
    """The specific catastrophic case, stated separately so it can never be refactored away."""
    for status in STATUSES:
        before = LiveState(id="x", status=status, first_seen_open="2026-08-01T00:00:00Z")
        after = apply(before, Result.failed(error), NOW)
        if status != CLOSED:
            assert after.status != CLOSED


def test_repeated_failures_escalate_health_but_freeze_status():
    state = LiveState(id="x", status=OPEN, first_seen_open="2026-08-01T00:00:00Z",
                      last_ok="2026-08-14T13:00:00Z")
    for i in range(1, 6):
        state = apply(state, Result.failed("timeout"), NOW + timedelta(minutes=30 * i))
        assert state.status == OPEN
    assert state.health != OK
    assert state.failure_count == 5


def test_blocking_errors_get_their_own_health():
    """403 is 'they are refusing us' — actionable in a different way from a timeout."""
    for err in ("403", "429", "cloudflare_challenge"):
        after = apply(LiveState(id="x", status=NOT_OPEN), Result.failed(err), NOW)
        assert after.health == BLOCKED, err


# --------------------------------------------------------------------- closed requires evidence
def test_never_opened_cannot_close():
    """A program we never saw open has not 'closed' — it is simply not open."""
    after = apply(LiveState(id="x", status=WATCH_ONLY), Result.absent(), NOW)
    assert after.status == NOT_OPEN

    after2 = apply(LiveState(id="x", status=NOT_OPEN), Result.absent(), NOW)
    assert after2.status == NOT_OPEN


def test_closing_requires_having_been_open():
    was_open = LiveState(id="x", status=OPEN, first_seen_open="2026-08-01T00:00:00Z")
    after = apply(was_open, Result.absent(), NOW)
    assert after.status == CLOSED
    assert after.closed_at is not None


# --------------------------------------------------------------------- confidence gating
def test_low_confidence_open_needs_two_confirmations():
    """One flapping page-hash must not put a firm in the ACT NOW rail."""
    state = LiveState(id="x", status=NOT_OPEN)
    state = apply(state, Result.found("http://u", confidence="low"), NOW)
    assert state.status == NOT_OPEN, "believed a single low-confidence sighting"

    state = apply(state, Result.found("http://u", confidence="low"),
                  NOW + timedelta(minutes=30))
    assert state.status == OPEN


def test_high_confidence_open_is_immediate():
    state = apply(LiveState(id="x", status=NOT_OPEN), Result.found("http://u"), NOW)
    assert state.status == OPEN
    assert state.first_seen_open is not None
    assert state.apply_url == "http://u"


def test_indeterminate_success_stamps_clock_without_claiming_anything():
    """`manual` rows: we ran, we honestly learned nothing. Status must not drift."""
    before = LiveState(id="x", status=WATCH_ONLY)
    after = apply(before, Result.unwatched(), NOW)
    assert after.status == WATCH_ONLY
    assert after.last_checked is not None
    assert after.last_ok is not None
    assert after.health == OK


def test_first_seen_open_is_sticky_across_a_close_and_reopen():
    state = apply(LiveState(id="x", status=NOT_OPEN), Result.found("http://u"), NOW)
    first = state.first_seen_open
    state = apply(state, Result.absent(), NOW + timedelta(days=1))
    assert state.status == CLOSED
    state = apply(state, Result.found("http://u"), NOW + timedelta(days=2))
    assert state.status == OPEN
    assert state.first_seen_open == first


# --------------------------------------------------------------------- health is time-based
@pytest.mark.parametrize("hours_ago,expected", [
    (1, OK),          # fresh
    (5, OK),          # still inside the 6h window
    (7, "stale"),     # missed several 30-min cycles
    (60, "broken"),   # two and a half days dark
])
def test_health_degrades_with_age_even_without_failures(hours_ago, expected):
    """A checker that silently stopped running must not look healthy."""
    state = LiveState(id="x", status=NOT_OPEN,
                      last_ok=(NOW - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    assert compute_health(state, NOW) == expected


def test_success_clears_failure_count_and_recovers_health():
    state = LiveState(id="x", status=NOT_OPEN, failure_count=4, last_error="403",
                      last_ok=(NOW - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    recovered = apply(state, Result.absent(), NOW)
    assert recovered.failure_count == 0
    assert recovered.last_error is None
    assert recovered.health == OK
