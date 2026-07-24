"""The state machine. One rule matters more than everything else in this repo:

    A FAILED CHECK MAY NEVER CHANGE `status`.

`status` records what we last knew from positive evidence. `health` records whether we still
know it. A timeout, a 403, a parse error, a collapsed listing — all of those degrade `health`
and leave `status` exactly where it was, so the UI can say "we last knew: not open, 14h ago,
403 — GO LOOK" instead of the catastrophic lie "closed".

tests/test_state_machine.py pins this across every status x every error class.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import (
    BLOCKED, BLOCKING_ERRORS, BROKEN, CLOSED, DEGRADED, LiveState, NOT_OPEN, OK, OPEN,
    Result, STALE, WATCH_ONLY,
)

STALE_AFTER = timedelta(hours=6)
BROKEN_AFTER = timedelta(hours=48)

# A low-confidence checker (page-hash heuristics) must see "open" twice in a row before we
# believe it. One flapping selector should not put a firm in the ACT NOW rail.
LOW_CONF_CONFIRMATIONS = 2


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_health(state: LiveState, now: datetime) -> str:
    """Pure function of failure count and staleness. Never looks at `status`."""
    if state.failure_count and state.last_error:
        err = state.last_error.lower()
        if any(b in err for b in BLOCKING_ERRORS):
            return BLOCKED

    last_ok = _parse(state.last_ok)
    if last_ok is not None:
        age = now - last_ok
        if age >= BROKEN_AFTER:
            return BROKEN
        if age >= STALE_AFTER or state.failure_count >= 3:
            return STALE
    elif state.failure_count >= 3:
        return STALE

    if state.failure_count >= 1:
        return DEGRADED
    return OK


def apply(prev: LiveState, result: Result, now: datetime, *, method: str | None = None,
          source: str | None = None, runner: str | None = None) -> LiveState:
    """Fold one check result into state. Returns a new LiveState; never mutates `prev`."""
    now_s = iso(now)
    nxt = prev.copy_with(last_checked=now_s)
    if method:
        nxt.check_method = method
    if source:
        nxt.source = source
    if runner:
        nxt.runner = runner

    # ---------------------------------------------------------------- failure path
    # THE invariant. Touch health, counters, error. Never touch status.
    if not result.ok:
        nxt.failure_count = prev.failure_count + 1
        nxt.last_error = result.error or "unknown_error"
        nxt.health = compute_health(nxt, now)
        return nxt

    # ---------------------------------------------------------------- success path
    nxt.failure_count = 0
    nxt.last_error = None
    nxt.last_ok = now_s
    nxt.evidence = result.evidence or prev.evidence
    nxt.confidence = result.confidence
    if result.fingerprint:
        nxt.fingerprint = result.fingerprint
    if result.deadline:
        nxt.deadline = result.deadline

    # Indeterminate success (`manual`, or a checker that ran but can't tell). We honestly
    # learned nothing about open/closed — stamp the clock and leave status alone.
    if result.open is None:
        nxt.health = compute_health(nxt, now)
        return nxt

    if result.open:
        # Low-confidence sightings must repeat before they count.
        if result.confidence == "low" and prev.status != OPEN:
            nxt.pending_open = prev.pending_open + 1
            if nxt.pending_open < LOW_CONF_CONFIRMATIONS:
                nxt.health = compute_health(nxt, now)
                return nxt
        nxt.pending_open = 0
        nxt.apply_url = result.apply_url or prev.apply_url
        nxt.title_seen = result.title or prev.title_seen
        if prev.status != OPEN:
            nxt.status = OPEN
            nxt.last_change = now_s
            nxt.first_seen_open = prev.first_seen_open or now_s
            nxt.closed_at = None
    else:
        nxt.pending_open = 0
        # `closed` requires that we once saw it OPEN. Otherwise "not currently posted" is
        # not_open — a program that never opened has not closed.
        if prev.status == OPEN and prev.first_seen_open:
            nxt.status = CLOSED
            nxt.last_change = now_s
            nxt.closed_at = now_s
        elif prev.status in (WATCH_ONLY, NOT_OPEN):
            if prev.status != NOT_OPEN:
                nxt.last_change = now_s
            nxt.status = NOT_OPEN

    nxt.health = compute_health(nxt, now)
    return nxt
