"""Every distinct season string in the seed, pinned.

These 17 strings are the entire vocabulary the 2026-07-23 curation used. If a future
curation adds an 18th, `windows_for` must return precision="unknown" for it rather than
guessing — `test_unparseable_is_flagged_not_guessed` is the guard for that.
"""

import pytest

from radar.predict import windows_for

# season string -> (start, end, precision)
SEED_SEASONS = {
    "Fall 2026":                          ("2026-09-01", "2026-11-30", "season"),
    "Fall 2026 (Sep–Nov)":                ("2026-09-01", "2026-11-30", "month_range"),
    "Fall 2026 (Sep–Dec)":                ("2026-09-01", "2026-12-31", "month_range"),
    "Fall 2026 (Sep–Oct)":                ("2026-09-01", "2026-10-31", "month_range"),
    "Fall 2026 (Aug–Oct)":                ("2026-08-01", "2026-10-31", "month_range"),
    "Fall 2026 (Aug–Oct, rolling)":       ("2026-08-01", "2026-10-31", "month_range"),
    "Fall 2026 (opens Aug, fills fast)":  ("2026-08-01", "2026-08-31", "month"),
    "Rolling — opens ~Sep 2026":          ("2026-09-01", "2026-09-30", "month"),
    "Sep–Oct 2026":                       ("2026-09-01", "2026-10-31", "month_range"),
    "Winter 2026–27":                     ("2026-12-01", "2027-02-28", "season"),
    "Winter 2026–27 (Nov–Jan)":           ("2026-11-01", "2027-01-31", "month_range"),
    "Winter 2026–27 (Dec–Jan)":           ("2026-12-01", "2027-01-31", "month_range"),
    "Winter 2026–27 (Dec–Feb)":           ("2026-12-01", "2027-02-28", "month_range"),
    "Winter 2026–27 (Jan–Feb)":           ("2027-01-01", "2027-02-28", "month_range"),
    "Winter/Spring 2027":                 ("2027-01-01", "2027-05-31", "season"),
    "Feb 2027":                           ("2027-02-01", "2027-02-28", "month"),
}


@pytest.mark.parametrize("season,expected", SEED_SEASONS.items())
def test_seed_seasons(season, expected):
    w = windows_for(season)[0]
    assert (w["start"], w["end"], w["precision"]) == expected


def test_two_windows_stay_two():
    """Oliver Wyman runs Oct AND Mar — one wide bar spanning both would be a lie."""
    w = windows_for("Oct 2026 & Mar 2027")
    assert len(w) == 2
    assert w[0]["start"] == "2026-10-01"
    assert w[1]["start"] == "2027-03-01"


@pytest.mark.parametrize("season", [
    "Rolling — opens ~Sep 2026",
    "Fall 2026 (Aug–Oct, rolling)",
])
def test_rolling_is_detected(season):
    """Rolling programs sort first everywhere — latency literally costs applications."""
    assert windows_for(season)[0]["rolling"] is True


def test_winter_tail_months_land_in_the_second_year():
    """The bug this guards: 'Winter 2026-27 (Jan-Feb)' meaning Jan 2026."""
    w = windows_for("Winter 2026–27 (Jan–Feb)")[0]
    assert w["start"].startswith("2027")


@pytest.mark.parametrize("junk", ["", "   ", "TBD", "ask the recruiter", "sometime soon"])
def test_unparseable_is_flagged_not_guessed(junk):
    """The core honesty rule: never invent a date. Flag it for curation instead."""
    w = windows_for(junk)
    assert len(w) == 1
    assert w[0]["precision"] == "unknown"
    assert "curation" in w[0]["basis"] or "parse" in w[0]["basis"]


def test_every_window_is_ordered_and_iso():
    for season in SEED_SEASONS:
        for w in windows_for(season):
            assert w["start"] <= w["end"], season
            assert len(w["start"]) == 10 and len(w["end"]) == 10
