"""Compose-level guarantees, mostly about not overstating what we know."""

from datetime import datetime, timezone

from radar.compose import bucket_for, nearest_window, window_label
from radar.models import BLOCKED, LiveState, OPEN, WATCH_ONLY

TODAY = datetime(2026, 8, 14, tzinfo=timezone.utc).date()


def w(start, end, precision="month_range", rolling=False):
    return {"start": start, "end": end, "precision": precision, "basis": "t", "rolling": rolling}


def test_nearest_window_prefers_the_one_we_are_inside():
    win, days = nearest_window([w("2026-08-01", "2026-10-31"), w("2027-03-01", "2027-03-31")], TODAY)
    assert days == 0 and win["start"] == "2026-08-01"


def test_nearest_window_skips_past_windows():
    """Oliver Wyman runs Oct and Mar — once Oct passes, Mar is the live one."""
    win, days = nearest_window([w("2026-06-01", "2026-06-30"), w("2026-10-01", "2026-10-31")], TODAY)
    assert win["start"] == "2026-10-01" and days > 0


def test_labels_never_overstate_precision():
    assert "month unknown" in window_label(w("2026-09-01", "2026-11-30", "season"))
    assert "curation" in window_label(w("2026-08-01", "2027-03-31", "unknown"))
    assert window_label(w("2026-09-01", "2026-09-30", "month")).startswith("~")


def test_broken_watch_inside_the_window_becomes_a_blind_spot():
    """The one state where the tool is actively failing him — it must outrank everything."""
    state = LiveState(id="x", status="not_open", health=BLOCKED, last_error="403")
    assert bucket_for({}, state, 0, TODAY) == "blind_spot"


def test_broken_watch_outside_the_window_is_not_a_blind_spot():
    state = LiveState(id="x", status="not_open", health=BLOCKED, last_error="403")
    assert bucket_for({}, state, 90, TODAY) != "blind_spot"


def test_open_always_wins_the_bucket():
    state = LiveState(id="x", status=OPEN, health=BLOCKED)
    assert bucket_for({}, state, 200, TODAY) == "open_now"
