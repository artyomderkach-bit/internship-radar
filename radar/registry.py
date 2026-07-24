"""Build `data/seed.json` from the 2026-07-23 curated dataset.

Adds four things the raw curation doesn't carry, all of them things the UI needs in order
to be honest:

  id               stable forever — the event log and his localStorage key off it
  windows          dated application windows + precision (see predict.py)
  soph_confidence  because `cls` says all 69 are sophomore-accessible and the notes disagree
  loc_bucket /     cheap filters, derived once here rather than re-parsed in JS
  elig_track
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from .eligibility import coding as coding_for, grad_2029, is_quant_role
from .predict import windows_for

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_seed_2026-07-23.json"
ADDITIONS = ROOT / "data" / "additions.json"      # later curation rounds
OVERRIDES = ROOT / "data" / "overrides.json"      # human corrections; outrank checkers
SEED = ROOT / "data" / "seed.json"
IDS_LOCK = ROOT / "data" / "ids.lock"

# Notes that CONTRADICT the `cls` column. These are the rows where the curated class year
# says sophomore but the prose says otherwise — the whole reason soph_confidence exists.
DOUBTFUL_MARKERS = ("penultimate", "final year", "lean junior", "summer before final")

# Notes that positively CONFIRM sophomore access, in the firm's own words.
CONFIRMED_MARKERS = (
    "explicitly sophomore", "explicitly open to", "open to all first/second-year",
    "open to any sophomore", "entering sophomore",
)

ELIG_TRACK = {"Open": "open", "Open/Div": "open_and_div", "Diversity": "div_only"}

STOPWORDS = {"the", "a", "an", "and", "of", "for", "program", "internship", "intern"}


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)


def mint_id(firm: str, program: str) -> str:
    """`vitol-commercial-trading`. Stable forever — see tests/test_ids_stable.py."""
    firm_part = slug(firm)
    words = [w for w in slug(program).split("-") if w and w not in STOPWORDS]
    return f"{firm_part}-{'-'.join(words[:3])}" if words else firm_part


def soph_confidence(row: dict) -> str:
    """confirmed | claimed | doubtful — derived from prose, not from the useless `cls`."""
    notes = (row.get("notes") or "").lower()
    if any(m in notes for m in DOUBTFUL_MARKERS):
        return "doubtful"
    # "Sophomore+ / Jr" is the curator hedging: it may really be a junior program.
    if "jr" in row.get("cls", "").lower():
        return "doubtful"
    if any(m in notes for m in CONFIRMED_MARKERS):
        return "confirmed"
    return "claimed"


def loc_bucket(loc: str) -> str:
    low = loc.lower()
    if "houston" in low:
        return "Houston"
    if "new york" in low or "nyc" in low:
        return "NYC"
    return "Other"


# Curated fields a row may carry beyond the original spreadsheet columns.
CURATED_PASSTHROUGH = ("curated_status", "curated_deadline", "curated_evidence",
                       "curated_verified_on", "apply_url")


def build() -> list[dict]:
    raw = json.loads(RAW.read_text())
    if ADDITIONS.exists():
        raw = raw + json.loads(ADDITIONS.read_text())
    overrides = json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}
    seen: dict[str, int] = {}
    out: list[dict] = []

    for row in raw:
        pid = mint_id(row["firm"], row["program"])
        # Collisions would silently merge two programs. Suffix instead, and shout in the diff.
        if pid in seen:
            seen[pid] += 1
            pid = f"{pid}-{seen[pid]}"
        else:
            seen[pid] = 1

        entry = {
            "id": pid,
            "firm": row["firm"],
            "program": row["program"],
            "sector": row["sector"],
            "sub": row["sub"],
            "loc": row["loc"],
            "loc_bucket": loc_bucket(row["loc"]),
            "cls": row["cls"],
            "soph_confidence": soph_confidence(row),
            "elig": row["elig"],
            "elig_track": ELIG_TRACK.get(row["elig"], "open"),
            "season_raw": row["season"],
            "windows": windows_for(row["season"]),
            "sel": row["sel"],
            "pres": row["pres"],
            # Later curation rounds only supply sel/pres; overall is their mean,
            # matching how the original 2026-07-23 spreadsheet computed it.
            "overall": row.get("overall", round((row["sel"] + row["pres"]) / 2, 1)),
            "notes": row["notes"],
            "link": row["link"],
        }
        # Two gates the original curation never checked, both of which can waste an
        # application: does a May-2029 graduate actually qualify, and does the posting
        # require code he doesn't write. Both default to "unverified", never to optimism.
        entry["grad_2029"], entry["grad_2029_basis"] = grad_2029(pid)
        entry["coding"], entry["coding_basis"] = coding_for(pid)
        entry["quant_role"] = is_quant_role(entry)
        for key in CURATED_PASSTHROUGH:
            if row.get(key) is not None:
                entry[key] = row[key]
        entry.update(overrides.get(pid, {}))
        out.append(entry)
    return out


def load_seed() -> list[dict]:
    return json.loads(SEED.read_text())


def main() -> None:
    programs = build()
    SEED.write_text(json.dumps(programs, indent=2, ensure_ascii=False) + "\n")
    IDS_LOCK.write_text("\n".join(sorted(p["id"] for p in programs)) + "\n")
    print(f"wrote {len(programs)} programs -> {SEED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
