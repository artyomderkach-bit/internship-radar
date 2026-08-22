"""Compose seed + live state into the JSON the site reads.

All the bucketing/sorting/counting happens HERE, not in the browser. The client stays a
renderer: it should never have to re-derive "is this urgent". That also means the same
board.json can be inspected, diffed and tested without a browser.

Emits the same trio twice, once per board (see audience.py):
  site/data/{board,meta,events}.json         — Artyom's radar
  site/sister/data/{board,meta,events}.json  — his sister's radar
board.json is everything (~120 KB); meta.json is tiny and polled every 60s so the client
only refetches board.json on change.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

from .audience import for_artyom, for_sister
from .models import BLOCKED, BROKEN, CLOSED, LiveState, OPEN, STALE, WATCH_ONLY
from .registry import ROOT, load_seed

OUT_DIR = ROOT / "site" / "data"
SISTER_OUT_DIR = ROOT / "site" / "sister" / "data"
STATE_DIR = ROOT / "state" / "shards"

# Bucket order IS the page order. blind_spot sits above closed deliberately: a broken watch
# needs action today, a closed application does not.
BUCKETS = ("open_now", "blind_spot", "this_month", "next_60", "later", "closed")

BUCKET_LABELS = {
    "open_now":   "OPEN NOW",
    "blind_spot": "⚠ BLIND SPOTS — we cannot see these right now",
    "this_month": "OPENS THIS MONTH",
    "next_60":    "OPENS NEXT 60 DAYS",
    "later":      "LATER THIS CYCLE",
    "closed":     "CLOSED",
}

PRECISION_RANK = {"month_range": 0, "month": 0, "quarter": 1, "season": 2, "unknown": 3}

MONTH_ABBR = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _d(iso_date: str) -> date:
    return date.fromisoformat(iso_date)


def nearest_window(windows: list[dict], today: date) -> tuple[dict | None, int]:
    """The window that matters right now, and days until it opens (0 if we're inside one).

    Returns (window, days_until). days_until is 0 while inside a window, and for a window
    already past we fall through to the next one — Oliver Wyman's Oct/Mar pair is why.
    """
    if not windows:
        return None, 9999
    inside = [w for w in windows if _d(w["start"]) <= today <= _d(w["end"])]
    if inside:
        return inside[0], 0
    future = sorted((w for w in windows if _d(w["start"]) > today),
                    key=lambda w: w["start"])
    if future:
        return future[0], (_d(future[0]["start"]) - today).days
    # Every window is in the past.
    return sorted(windows, key=lambda w: w["end"])[-1], -1


def window_label(w: dict | None) -> str:
    """Human text that never implies more precision than we have."""
    if not w:
        return "unknown"
    s, e = _d(w["start"]), _d(w["end"])
    prec = w["precision"]
    if prec == "unknown":
        return "date unknown — needs curation"
    if prec == "month":
        return f"~{MONTH_ABBR[s.month]} {s.year}"
    span = f"{MONTH_ABBR[s.month]}–{MONTH_ABBR[e.month]} {e.year}"
    if prec == "season":
        return f"{span} (month unknown)"
    return span


def load_state() -> dict[str, LiveState]:
    """Merge the per-runner shards. Each runner owns one file, so this can't conflict."""
    merged: dict[str, LiveState] = {}
    if not STATE_DIR.exists():
        return merged
    for shard in sorted(STATE_DIR.glob("*.json")):
        if shard.name.endswith(".boards.json"):
            continue   # per-board row counts for the collapse guard, not program state
        for pid, raw in json.loads(shard.read_text()).get("programs", {}).items():
            state = LiveState.from_dict({**raw, "id": pid})
            prior = merged.get(pid)
            # Two runners checked the same program: keep the more recently successful one.
            if prior is None or (state.last_ok or "") > (prior.last_ok or ""):
                merged[pid] = state
    return merged


def bucket_for(prog: dict, state: LiveState, days_until: int, today: date) -> str:
    if state.status == OPEN:
        return "open_now"
    if state.health in (BROKEN, BLOCKED, STALE) and days_until == 0:
        # We're inside the predicted window and the watch is down. This is the one state
        # where the tool is actively failing him, so it outranks everything but OPEN.
        return "blind_spot"
    if state.status == CLOSED:
        return "closed"
    if days_until <= 31:
        return "this_month"
    if days_until <= 60:
        return "next_60"
    return "later"


def compose(now: datetime | None = None,
            keep: Callable[[dict], bool] = for_artyom) -> dict:
    now = now or datetime.now(timezone.utc)
    today = now.date()
    seed = [p for p in load_seed() if keep(p)]
    states = load_state()

    rows = []
    for prog in seed:
        state = states.get(prog["id"], LiveState(id=prog["id"]))
        # A human verified this one by hand. It counts ONLY while no automated checker owns
        # the row — the moment a real check exists, machine evidence wins. Rendered at
        # `medium` confidence and labelled "curated" so it never masquerades as a live check.
        curated = prog.get("curated_status")
        if curated and state.check_method == "manual":
            state = state.copy_with(
                status=curated,
                confidence="medium",
                evidence=prog.get("curated_evidence") or "curated by hand",
                apply_url=prog.get("apply_url") or state.apply_url,
                first_seen_open=state.first_seen_open or prog.get("curated_verified_on"),
            )
        win, days = nearest_window(prog["windows"], today)
        rolling = bool(win and win.get("rolling"))
        # Most "Fall 2026" rows resolve to the same Sep 1 start, so a flat 60-day bucket
        # would be a 51-row wall. Sub-grouping by month keeps it scannable and shows the
        # September crush for what it is.
        if win:
            start = _d(win["start"])
            month_group = f"{MONTH_ABBR[start.month]} {start.year}"
        else:
            month_group = "unknown"
        rows.append({
            **prog,
            "bucket": bucket_for(prog, state, days, today),
            "days_until": days,
            "month_group": month_group,
            "precision": win["precision"] if win else "unknown",
            "window_label": window_label(win),
            "window": win,
            "rolling": rolling,
            "watched": state.check_method != "manual",
            "status": state.status,
            "health": state.health,
            "confidence": state.confidence,
            "check_method": state.check_method,
            "apply_url": state.apply_url,
            "last_checked": state.last_checked,
            "last_ok": state.last_ok,
            "first_seen_open": state.first_seen_open,
            "last_error": state.last_error,
            "evidence": state.evidence,
            "deadline": prog.get("curated_deadline"),
            "curated_verified_on": prog.get("curated_verified_on"),
        })

    # Sort, in order of what actually decides his next action:
    #   bucket → when → HOW SURE we are of the when → rolling → his own score.
    # The precision term matters: 35 rows are bare "Fall 2026" and default to a Sep 1 start,
    # so without it a pile of "we don't really know" outranks the 11 we genuinely know open
    # in September. Certain dates come first; vague ones sink.
    rows.sort(key=lambda r: (BUCKETS.index(r["bucket"]), r["days_until"],
                             PRECISION_RANK.get(r["precision"], 3),
                             not r["rolling"], -r["overall"], r["firm"]))

    # Month histogram drives the season-density strip.
    months: dict[str, int] = {}
    for r in rows:
        months[r["month_group"]] = months.get(r["month_group"], 0) + 1

    counts = {b: sum(1 for r in rows if r["bucket"] == b) for b in BUCKETS}
    counts["total"] = len(rows)
    counts["imprecise"] = sum(1 for r in rows if PRECISION_RANK.get(r["precision"], 3) >= 2)
    counts["soon_14"] = sum(1 for r in rows
                            if r["bucket"] in ("this_month", "next_60") and r["days_until"] <= 14)

    coverage = {
        "auto": sum(1 for r in rows if r["check_method"] in
                    ("greenhouse", "lever", "ashby", "smartrecruiters", "workday")),
        "mirror": sum(1 for r in rows if r["check_method"] == "github_mirror"),
        "page_hash": sum(1 for r in rows if r["check_method"] == "page_hash"),
        "curated": sum(1 for r in rows if r["check_method"] == "manual"),
    }

    checked = [r["last_ok"] for r in rows if r["last_ok"]]
    meta = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "today": today.isoformat(),
        "last_ok": max(checked) if checked else None,
        "counts": counts,
        "months": months,
        "coverage": coverage,
        "bucket_labels": BUCKET_LABELS,
    }
    return {"meta": meta, "programs": rows}


EVENTS_LOG = ROOT / "state" / "events.ndjson"
FEED_LIMIT = 200


def recent_events(limit: int = FEED_LIMIT, ids: set[str] | None = None) -> list[dict]:
    """Newest-first tail of the append-only log — the feed is one small fetch, not the log.

    `ids` scopes the feed to one board's programmes, so neither sibling reads the
    other's news.
    """
    if not EVENTS_LOG.exists():
        return []
    rows = []
    for line in EVENTS_LOG.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue   # a torn final line must not break the whole build
    # "added" floods the very first run; it is bookkeeping, not news.
    news = [r for r in rows if r.get("kind") != "added"]
    if ids is not None:
        news = [r for r in news if r.get("id") in ids]
    return list(reversed(news[-limit:]))


def write_board(out_dir: Path, keep: Callable[[dict], bool], label: str) -> None:
    board = compose(keep=keep)
    ids = {r["id"] for r in board["programs"]}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "board.json").write_text(json.dumps(board, ensure_ascii=False) + "\n")
    (out_dir / "meta.json").write_text(json.dumps(board["meta"], ensure_ascii=False) + "\n")
    (out_dir / "events.json").write_text(
        json.dumps(recent_events(ids=ids), ensure_ascii=False) + "\n")
    c = board["meta"]["counts"]
    print(f"composed {label}: {c['total']} programs — " +
          " ".join(f"{b}:{c[b]}" for b in BUCKETS))


def main() -> None:
    write_board(OUT_DIR, for_artyom, "radar")
    write_board(SISTER_OUT_DIR, for_sister, "sister")


if __name__ == "__main__":
    main()
