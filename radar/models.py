"""Core types.

The one idea worth reading: `Result.ok` and `Result.open` are different questions.

    ok    — did the CHECK succeed? did I learn anything at all?
    open  — is the posting live? (None = the check worked but was indeterminate)

Conflating those two is the bug class that turns a 403 into "applications closed" on the
morning he should have applied. Every guard in runner.py exists to keep them separate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any

# --- status: what we last KNEW. Only positive evidence moves it. ---
WATCH_ONLY = "watch_only"    # no checker configured; the window is a prediction and we say so
NOT_OPEN = "not_open"        # a check SUCCEEDED and found no posting
OPEN = "open"                # a check SUCCEEDED and found a live posting
CLOSED = "closed"            # succeeded, absent from an authoritative listing, was once open
STATUSES = (WATCH_ONLY, NOT_OPEN, OPEN, CLOSED)

# --- health: whether we still know it. Failures move ONLY this. ---
OK = "ok"
DEGRADED = "degraded"        # 1-2 consecutive failures
STALE = "stale"              # 3+ failures, or no success in 6h
BROKEN = "broken"            # no success in 48h
BLOCKED = "blocked"          # 403/429/Cloudflare — a distinct, actionable kind
HEALTHS = (OK, DEGRADED, STALE, BROKEN, BLOCKED)

CONFIDENCES = ("high", "medium", "low")

# Errors that mean "they are actively refusing us", not "we broke".
BLOCKING_ERRORS = ("403", "429", "cloudflare", "captcha", "blocked")


@dataclass(frozen=True)
class Result:
    """What a checker returns. Checkers never mutate state; they only report."""
    ok: bool
    open: bool | None = None
    evidence: str = ""
    apply_url: str | None = None
    title: str | None = None
    deadline: str | None = None
    fingerprint: str | None = None
    confidence: str = "high"
    error: str | None = None
    raw_count: int | None = None      # rows the listing returned; 0 is suspicious
    board_key: str | None = None      # groups programs sharing one job board

    @classmethod
    def found(cls, url: str, **kw: Any) -> Result:
        return cls(ok=True, open=True, apply_url=url, evidence="req_found", **kw)

    @classmethod
    def absent(cls, **kw: Any) -> Result:
        return cls(ok=True, open=False, evidence="absent_from_listing", **kw)

    @classmethod
    def failed(cls, error: str, **kw: Any) -> Result:
        return cls(ok=False, open=None, error=error, evidence="check_failed", **kw)

    @classmethod
    def unwatched(cls) -> Result:
        """`manual` rows: the check "succeeded" in that we honestly know nothing new."""
        return cls(ok=True, open=None, evidence="manual", confidence="medium")


@dataclass
class LiveState:
    id: str
    status: str = WATCH_ONLY
    health: str = OK
    confidence: str = "high"
    check_method: str = "manual"
    runner: str | None = None
    source: str | None = None
    apply_url: str | None = None
    title_seen: str | None = None
    deadline: str | None = None
    last_checked: str | None = None
    last_ok: str | None = None
    last_change: str | None = None
    first_seen_open: str | None = None
    closed_at: str | None = None
    failure_count: int = 0
    last_error: str | None = None
    evidence: str | None = None
    fingerprint: str | None = None
    pending_open: int = 0        # consecutive low-confidence "open" sightings, for debouncing

    def to_dict(self) -> dict:
        return asdict(self)

    def copy_with(self, **kw: Any) -> LiveState:
        return replace(self, **kw)

    @classmethod
    def from_dict(cls, d: dict) -> LiveState:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass(frozen=True)
class Event:
    ts: str
    id: str
    kind: str
    frm: str | None = None
    to: str | None = None
    conf: str | None = None
    src: str | None = None
    url: str | None = None
    note: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["from"] = d.pop("frm")     # `from` is a Python keyword; the JSON uses the real word
        return d
