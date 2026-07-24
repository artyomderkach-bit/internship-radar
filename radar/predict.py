"""Turn the seed's human season strings into dated windows — without inventing precision.

The seed's `season` field is prose written by a human reading last cycle's pages. 48% of it
is the bare string "Fall 2026" with no month at all. The whole point of this module is that
those rows come out *marked* as imprecise rather than silently becoming a confident bar on a
Gantt chart. Anything this parser cannot read becomes precision="unknown" and shows up on
#/health as a curation to-do — never a guess.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import asdict, dataclass

# precision, worst to best. The UI renders opacity/width from this.
PRECISION_ORDER = ("unknown", "season", "quarter", "month", "month_range")

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Named seasons → (start month, end month, spans into next year)
SEASONS = {
    "fall": (9, 11, False),
    "autumn": (9, 11, False),
    "winter": (12, 2, True),
    "spring": (3, 5, False),
    "summer": (6, 8, False),
}

# Recruiting-cycle order, NOT calendar-month order. "Winter/Spring 2027" starts in winter;
# sorting by start month would put spring (3) ahead of winter (12) and invert the range.
CYCLE_ORDER = {"fall": 0, "autumn": 0, "winter": 1, "spring": 2, "summer": 3}


@dataclass(frozen=True)
class Window:
    start: str          # ISO date
    end: str            # ISO date
    precision: str      # one of PRECISION_ORDER
    basis: str          # where this came from, for the tooltip
    rolling: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _eom(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def _iso(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def _span(y1: int, m1: int, y2: int, m2: int, precision: str, basis: str,
          rolling: bool = False) -> Window:
    return Window(_iso(y1, m1, 1), _iso(y2, m2, _eom(y2, m2)), precision, basis, rolling)


def _years_in(text: str) -> list[int]:
    """Every 4-digit year, plus 2-digit tails of ranges like '2026–27'."""
    years: list[int] = []
    for m in re.finditer(r"\b(20\d{2})\s*[–\-—/]\s*(\d{2})\b", text):
        years.extend([int(m.group(1)), 2000 + int(m.group(2))])
    if not years:
        years = [int(y) for y in re.findall(r"\b20\d{2}\b", text)]
    return years


def _wraps_new_year(text: str) -> bool:
    """True when the named season crosses Dec 31 — i.e. 'Winter 2026-27'."""
    return any(k in text for k in SEASONS if SEASONS[k][2])


def _year_for_month(month: int, text: str, years: list[int], cycle_year: int) -> int:
    """Which calendar year does this month belong to?

    'Winter 2026-27 (Jan-Feb)' means January *2027*, not 2026. When a wrapping season
    names two years, late months belong to the first and early months to the second.
    """
    if not years:
        return cycle_year
    if len(years) > 1 and _wraps_new_year(text):
        return years[0] if month >= 9 else years[-1]
    return years[0]


def _month_tokens(text: str) -> list[tuple[int, int]]:
    """Month abbreviations with their character offsets, in order of appearance."""
    out = []
    for m in re.finditer(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b",
                         text, re.I):
        out.append((MONTHS[m.group(1).lower()], m.start()))
    return out


def parse_season(season: str, cycle_year: int = 2026) -> list[Window]:
    """Parse one seed `season` string into zero or more windows.

    Returns [] only when nothing at all could be read — the caller turns that into an
    explicit `unknown` window so the row still renders, visibly flagged.
    """
    if not season or not season.strip():
        return []

    raw = season.strip()
    text = raw.lower().replace("–", "-").replace("—", "-")
    rolling = "rolling" in text

    # "Oct 2026 & Mar 2027" — genuinely two separate application windows, not one long one.
    if "&" in text or " and " in text:
        parts = re.split(r"\s*(?:&|\band\b)\s*", text)
        windows: list[Window] = []
        for part in parts:
            windows.extend(parse_season(part, cycle_year))
        if len(windows) > 1:
            return windows

    years = _years_in(text)
    months = _month_tokens(text)

    # --- explicit month range: "(Sep-Nov)", "Sep-Oct 2026", "Winter 2026-27 (Nov-Jan)" ---
    range_match = re.search(
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*-\s*"
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*", text, re.I)
    if range_match:
        m1 = MONTHS[range_match.group(1).lower()]
        m2 = MONTHS[range_match.group(2).lower()]
        y1 = _year_for_month(m1, text, years, cycle_year)
        y2 = _year_for_month(m2, text, years, cycle_year)
        # A range that still runs backwards crossed a new year the years didn't spell out.
        if (y2, m2) < (y1, m1):
            y2 = y1 + 1
        return [_span(y1, m1, y2, m2, "month_range", f"season string: {raw!r}", rolling)]

    # --- single month: "opens ~Sep 2026", "opens Aug, fills fast", "Feb 2027" ---
    if len(months) == 1:
        m = months[0][0]
        year = _year_for_month(m, text, years, cycle_year)
        return [_span(year, m, year, m, "month", f"season string: {raw!r}", rolling)]

    # --- named season only: "Fall 2026", "Winter 2026-27", "Winter/Spring 2027" ---
    named = [k for k in SEASONS if k in text]
    if named:
        # "Winter/Spring 2027" spans from the first season's start to the last one's end.
        # Order by calendar position so "Winter/Spring" starts in winter, not alphabetically.
        named.sort(key=lambda k: CYCLE_ORDER[k])
        first, last = named[0], named[-1]
        s_m, s_end, s_wraps = SEASONS[first]
        _, e_m, _ = SEASONS[last]
        y1 = years[0] if years else cycle_year
        y2 = years[-1] if len(years) > 1 else y1

        if s_wraps:
            if len(years) > 1:
                # "Winter 2026-27" — Dec of the first year through Feb of the second.
                y2 = years[-1]
            else:
                # "Winter/Spring 2027" names one year: that year's Jan-Feb, not last Dec.
                s_m = 1
        if (y2, e_m) < (y1, s_m):
            y2 = y1 + 1
        return [_span(y1, s_m, y2, e_m, "season", f"season string: {raw!r}", rolling)]

    return []


def windows_for(season: str, cycle_year: int = 2026) -> list[dict]:
    """Public entry point. Always returns at least one window, honestly labelled."""
    parsed = parse_season(season, cycle_year)
    if parsed:
        return [w.to_dict() for w in parsed]
    # Unreadable. Cover the whole cycle and say so loudly rather than picking a plausible date.
    # Continuously-posted boards ("rolling", "year-round") land here by design: a wide,
    # explicitly-uncertain window is the honest shape for "could appear any time".
    rolling = "rolling" in (season or "").lower() or "year-round" in (season or "").lower()
    return [Window(f"{cycle_year}-08-01", f"{cycle_year + 1}-03-31", "unknown",
                   f"could not parse {season!r} — needs curation", rolling).to_dict()]
