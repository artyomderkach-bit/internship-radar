"""Program ids are permanent.

They key the append-only event log AND his browser-local application tracker. If an id
changes, his "applied" flags silently detach from the programmes they belong to — a data
loss he would not notice until it mattered. `data/ids.lock` freezes the set.
"""

import json
from pathlib import Path

from radar.registry import IDS_LOCK, build, mint_id

ROOT = Path(__file__).resolve().parent.parent


def test_ids_are_unique():
    ids = [p["id"] for p in build()]
    assert len(ids) == len(set(ids)), "duplicate ids would silently merge two programmes"


def test_ids_match_lockfile():
    locked = set(IDS_LOCK.read_text().split())
    current = {p["id"] for p in build()}
    removed = locked - current
    assert not removed, (
        f"ids disappeared: {sorted(removed)}. Renaming an id detaches its event history "
        f"and the user's saved application status. Add an alias instead, or update "
        f"data/ids.lock deliberately."
    )


def test_mint_id_is_deterministic_and_slugged():
    assert mint_id("Castleton Commodities (CCI)", "Commercial / Trading Internship") == \
        "castleton-commodities-cci-commercial-trading"
    # Stopwords are dropped so "X Internship Program" and "X Program" don't diverge.
    assert mint_id("Acme", "Summer Internship Program") == "acme-summer"


def test_every_program_has_required_shape():
    for p in build():
        assert p["windows"], f"{p['id']} has no window at all"
        assert p["soph_confidence"] in ("confirmed", "claimed", "doubtful")
        assert p["elig_track"] in ("open", "open_and_div", "div_only")
        assert p["loc_bucket"] in ("Houston", "NYC", "Other")
        assert p["link"].startswith("http")
