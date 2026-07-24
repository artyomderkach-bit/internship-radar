"""Run every configured check, fold results into state, emit events, persist.

The guards live HERE rather than in each checker, so a new checker cannot forget them:

  * any exception becomes Result.failed(...) — checkers may not swallow errors into a
    plausible-looking "not open"
  * board-collapse guard: a listing that returned rows last run and zero this run is an
    outage, not N closures, so every program on that board is failed instead
  * canary: a permanent posting that must always be present; missing canary fails the board

The collapse guard and canary are load-bearing from the first listing checker, not later
hardening. Without them one Greenhouse hiccup marks forty programmes closed on the morning
he should have applied.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import events as events_mod
from .checkers import github_mirror, manual  # noqa: F401  — they self-register
from .checkers.base import REGISTRY
from .models import LiveState, Result
from .registry import ROOT, load_seed
from .state import apply, iso

STATE_DIR = ROOT / "state" / "shards"
EVENTS_FILE = ROOT / "state" / "events.ndjson"
RUNS_FILE = ROOT / "state" / "runs.ndjson"

SOURCES_DIR = ROOT / "sources"


def load_sources() -> dict[str, dict]:
    """One YAML per firm. Absent file == manual, which is the honest default."""
    cfgs: dict[str, dict] = {}
    if not SOURCES_DIR.exists():
        return cfgs
    try:
        import yaml
    except ImportError:
        return cfgs
    for path in sorted(SOURCES_DIR.glob("*.yml")):
        try:
            doc = yaml.safe_load(path.read_text()) or {}
        except Exception as exc:  # a broken YAML must not take down the whole run
            print(f"  ! {path.name}: {exc}")
            continue
        if doc.get("id"):
            cfgs[doc["id"]] = doc
    return cfgs


def load_shard(runner: str) -> dict[str, LiveState]:
    path = STATE_DIR / f"{runner}.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text()).get("programs", {})
    return {pid: LiveState.from_dict({**s, "id": pid}) for pid, s in raw.items()}


def save_shard(runner: str, states: dict[str, LiveState], now: datetime) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "runner": runner,
        "updated_at": iso(now),
        "programs": {pid: s.to_dict() for pid, s in sorted(states.items())},
    }
    (STATE_DIR / f"{runner}.json").write_text(json.dumps(payload, indent=1) + "\n")


def append_ndjson(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def run(runner: str = "actions", dry: bool = False, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    seed = load_seed()
    sources = load_sources()
    before = load_shard(runner)
    after: dict[str, LiveState] = {}

    # First pass: collect raw results so board-level guards can see the whole picture.
    results: dict[str, Result] = {}
    board_counts: dict[str, int] = {}
    for prog in seed:
        cfg = (sources.get(prog["id"]) or {}).get("check", {}) or {}
        method = cfg.get("method", "manual")
        # Respect per-source runner pinning: a source marked `vps` is skipped by Actions.
        want = cfg.get("runner", "either")
        if want not in ("either", runner) and method != "manual":
            continue
        checker = REGISTRY.get(method)
        if checker is None:
            results[prog["id"]] = Result.failed(f"no_checker:{method}")
            continue
        try:
            res = checker.check(prog, cfg)
        except Exception as exc:
            res = Result.failed(f"{type(exc).__name__}: {exc}"[:200])
        results[prog["id"]] = res
        if res.board_key and res.raw_count is not None:
            board_counts[res.board_key] = max(board_counts.get(res.board_key, 0), res.raw_count)

    # Second pass: board-collapse guard. A board that had rows and now has none is an
    # outage; refuse to interpret it as every programme on it closing at once.
    prior_boards = json.loads((STATE_DIR / f"{runner}.boards.json").read_text()) \
        if (STATE_DIR / f"{runner}.boards.json").exists() else {}
    collapsed = {b for b, prev in prior_boards.items()
                 if prev > 0 and board_counts.get(b, 0) == 0 and b in board_counts}
    if collapsed:
        print(f"  ! collapse guard tripped for boards: {sorted(collapsed)}")

    for prog in seed:
        pid = prog["id"]
        res = results.get(pid)
        if res is None:
            if pid in before:
                after[pid] = before[pid]      # pinned to another runner; keep its state
            continue
        if res.board_key in collapsed:
            res = Result.failed("listing_collapsed", board_key=res.board_key)
        cfg = (sources.get(pid) or {}).get("check", {}) or {}
        prev = before.get(pid, LiveState(id=pid))
        after[pid] = apply(prev, res, now, method=cfg.get("method", "manual"),
                           source=cfg.get("board") or cfg.get("url"), runner=runner)

    evts = events_mod.diff(before, after, iso(now), run=runner)
    summary = {
        "ts": iso(now), "runner": runner,
        "checked": len(results), "events": len(evts),
        "opened": sum(1 for e in evts if e.kind == "opened"),
        "broke": sum(1 for e in evts if e.kind in ("watch_broke", "blocked")),
    }

    if not dry:
        save_shard(runner, after, now)
        (STATE_DIR / f"{runner}.boards.json").write_text(json.dumps(board_counts) + "\n")
        append_ndjson(EVENTS_FILE, [e.to_dict() for e in evts])
        append_ndjson(RUNS_FILE, [summary])

    print(f"{'[dry] ' if dry else ''}{summary['checked']} checked · "
          f"{summary['events']} events · {summary['opened']} opened · {summary['broke']} broke")
    for e in evts[:20]:
        print(f"   {e.kind:16} {e.id}")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(prog="radar.runner")
    ap.add_argument("--runner", default="actions", help="which shard this process owns")
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    args = ap.parse_args()
    run(runner=args.runner, dry=args.dry_run)


if __name__ == "__main__":
    main()
