"""Turn a state diff into an append-only event log.

Only this module writes events. Checkers never emit them, so there is exactly one place to
audit when asking "why does the feed say that?".

Infrastructure events (`watch_broke`, `blocked`, `watch_recovered`) are first-class and land
in the SAME feed as job events — a checker breaking during an application window is news he
needs, not a footnote on a status page.
"""

from __future__ import annotations

from .models import BLOCKED, BROKEN, Event, LiveState, OK, STALE

DOWN = {STALE, BROKEN, BLOCKED}


def diff(old: dict[str, LiveState], new: dict[str, LiveState], ts: str,
         run: str | None = None) -> list[Event]:
    events: list[Event] = []
    for pid, cur in new.items():
        prev = old.get(pid)
        if prev is None:
            events.append(Event(ts=ts, id=pid, kind="added", to=cur.status, src=run))
            continue

        if cur.status != prev.status:
            kind = {"open": "opened", "closed": "closed"}.get(cur.status, "status_changed")
            events.append(Event(ts=ts, id=pid, kind=kind, frm=prev.status, to=cur.status,
                                conf=cur.confidence, src=cur.source or run, url=cur.apply_url))

        # Health transitions in and out of "we can't see this".
        was_down, is_down = prev.health in DOWN, cur.health in DOWN
        if is_down and not was_down:
            events.append(Event(ts=ts, id=pid,
                                kind="blocked" if cur.health == BLOCKED else "watch_broke",
                                frm=prev.health, to=cur.health, src=cur.source or run,
                                note=cur.last_error))
        elif was_down and cur.health == OK:
            events.append(Event(ts=ts, id=pid, kind="watch_recovered",
                                frm=prev.health, to=cur.health, src=cur.source or run))

        if cur.apply_url and prev.apply_url and cur.apply_url != prev.apply_url:
            events.append(Event(ts=ts, id=pid, kind="url_changed",
                                frm=prev.apply_url, to=cur.apply_url, src=run))
    return events
