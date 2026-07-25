"""Direct job-board checkers: Ashby and Greenhouse.

These are the real thing — a firm's own board, no community volunteer in between. Both
expose a public unauthenticated JSON endpoint, verified working on 2026-07-24:

    Ashby       https://api.ashbyhq.com/posting-api/job-board/{board}
    Greenhouse  https://boards-api.greenhouse.io/v1/boards/{board}/jobs

Unlike the mirror, these CAN report a negative: the firm's own board is authoritative about
the firm's own postings. So an absent req really is evidence of absence — but only when the
fetch succeeded and the board looks healthy, which is what the guards below are for.

The collapse guard lives here rather than in runner.py for these because the natural canary
on a startup board is not one permanent req (they churn) but the total row count: a board
that returned 38 jobs yesterday and 0 today is an outage, not a company that fired everyone.
"""

from __future__ import annotations

from ..matching import is_coding_title, looks_like_intern, wrong_season
from ..models import Result
from .base import register

UA = ("internship-radar/1.0 "
      "(+https://github.com/artyomderkach-bit/internship-radar)")


def _fetch(url: str):
    import httpx
    return httpx.get(url, timeout=25.0, follow_redirects=True,
                     headers={"User-Agent": UA, "Accept": "application/json"})


def _decide(rows: list[dict], cfg: dict, board_key: str) -> Result:
    """Shared logic once a board has been normalised to {title, url, type}."""
    total = len(rows)
    min_rows = int(cfg.get("canary_min", 3))

    # Board-level sanity. Zero rows from a board that should have dozens is an outage.
    if total < min_rows:
        return Result.failed(f"board_too_small:{total}<{min_rows}", board_key=board_key,
                             raw_count=total)

    want_year = str(cfg.get("year", 2027))
    student = [r for r in rows if looks_like_intern(r["title"], r.get("type"))]
    if not student:
        return Result.absent(evidence=f"{board_key}: {total} roles, no student postings",
                             board_key=board_key, raw_count=total)

    current = [r for r in student if not wrong_season(r["title"], want_year)]
    usable = [r for r in current if not is_coding_title(r["title"])]

    if usable:
        best = usable[0]
        others = f" (+{len(usable) - 1} more)" if len(usable) > 1 else ""
        return Result(ok=True, open=True, apply_url=best["url"], title=best["title"],
                      evidence=f"{board_key}: \"{best['title']}\"{others}",
                      confidence="high", board_key=board_key, raw_count=total)

    # Student roles exist but none are usable. Say WHY, and stay indeterminate rather than
    # reporting "nothing here" — the distinction is the difference between "they're not
    # hiring students" and "they are, just not for you".
    if current:
        return Result(ok=True, open=None, confidence="high", board_key=board_key,
                      raw_count=total,
                      evidence=f"{board_key}: {len(current)} student role(s), all coding")
    return Result(ok=True, open=None, confidence="high", board_key=board_key,
                  raw_count=total,
                  evidence=f"{board_key}: {len(student)} student role(s), all a different cycle")


class AshbyChecker:
    name = "ashby"

    def check(self, prog: dict, cfg: dict) -> Result:
        board = cfg.get("board")
        if not board:
            return Result.failed("no_board_configured")
        key = f"ashby:{board}"
        try:
            resp = _fetch(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            return Result.failed(f"{type(exc).__name__}", board_key=key)

        rows = [{"title": j.get("title", ""),
                 "url": j.get("jobUrl") or j.get("applyUrl") or "",
                 "type": j.get("employmentType")}
                for j in (data.get("jobs") or []) if j.get("isListed", True)]
        return _decide(rows, cfg, key)


class GreenhouseChecker:
    name = "greenhouse"

    def check(self, prog: dict, cfg: dict) -> Result:
        board = cfg.get("board")
        if not board:
            return Result.failed("no_board_configured")
        key = f"greenhouse:{board}"
        try:
            resp = _fetch(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs")
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            return Result.failed(f"{type(exc).__name__}", board_key=key)

        rows = [{"title": j.get("title", ""), "url": j.get("absolute_url", ""), "type": None}
                for j in (data.get("jobs") or [])]
        return _decide(rows, cfg, key)


register(AshbyChecker())
register(GreenhouseChecker())
