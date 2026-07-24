"""Mirror the community Summer-2027 internship tracker repos.

Why this checker first: one fetch per repo covers every programme at once, the raw
githubusercontent host is never blocked from GitHub Actions, and it needs no per-firm
configuration. Best coverage-per-hour available.

Honest limitation, stated up front because it decides how much to trust a miss: **these
repos are overwhelmingly software-engineering and quant listings.** They cover trading firms
well and barely touch Houston commodities, Fed research, think tanks or city government —
which is most of what actually matters here. So:

    a mirror HIT is real signal; a mirror MISS means almost nothing.

Absent from a SWE-focused list is not evidence that a commodities desk is not hiring. This
checker therefore only ever reports `open` or `unknown`. It never reports `not_open`, so it
can never begin the chain that ends in a false `closed`.

Sources verified live on 2026-07-24:
  vanshb03/Summer2027-Internships          JSON listings, refreshed daily, SWE-heavy
  northwesternfintech/2027QuantInternships one YAML per firm, role-typed (QT/QR/SWE/FPGA)

SimplifyJobs has no Summer2027 repo yet (only Summer2026, still active) — it will appear
later in the cycle; add it here when it does. speedyapply publishes markdown tables only.
"""

from __future__ import annotations

import json
import re

from ..models import Result
from .base import register

LISTINGS_URL = "https://raw.githubusercontent.com/vanshb03/Summer2027-Internships/dev/.github/scripts/listings.json"
QUANT_INDEX = "https://api.github.com/repos/northwesternfintech/2027QuantInternships/contents/data"
QUANT_RAW = "https://raw.githubusercontent.com/northwesternfintech/2027QuantInternships/main/data/{}"

UA = ("internship-radar/1.0 "
      "(+https://github.com/artyomderkach-bit/internship-radar)")

# Role types in the quant repo. QT is the only one that is a trading seat rather than a
# programming job — which matters a lot here, because Artyom does not write code.
NON_CODING_ROLES = {"QT"}
CODING_ROLES = {"QR", "SWE", "FPGA", "SRE", "DEV"}

STOP = {"the", "and", "of", "for", "inc", "llc", "group", "corp", "co", "company",
        "capital", "trading", "securities", "management", "partners"}


def _norm(text: str) -> str:
    """Loose firm key: 'Castleton Commodities (CCI)' -> 'castletoncommodities'."""
    text = re.sub(r"\(.*?\)", " ", text or "")
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]
    return "".join(words)


# Title fragments that mean "this is a programming job". The general listings repo has no
# role typing, so without this filter it happily reports a Trading Systems Engineering req
# as the sophomore trading programme being open — which is worse than no signal at all,
# because he would spend an evening on a job he cannot do.
CODING_TITLE = (
    "software", "swe", "developer", "engineer", "engineering", "machine learning",
    "data scien", "data engineer", "quantitative research", "quant research",
    "infrastructure", "systems", "platform", "fpga", "hardware", "devops", "security",
    "full stack", "backend", "front end", "frontend", "ml ", "ai/ml",
)


# Substrings that mean "this req is gone", checked in BOTH the final URL and the body.
EXPIRED_MARKERS = ("jobexpired", "job-expired", "job_expired", "/expired",
                   "notfound", "page-not-found", "/404")


def _is_coding_title(title: str) -> bool:
    return any(frag in (title or "").lower() for frag in CODING_TITLE)


def _is_2027_intern(title: str) -> bool:
    low = (title or "").lower()
    if not any(w in low for w in ("intern", "co-op", "analyst", "sophomore", "first-year")):
        return False
    # A listing explicitly for another season is not evidence about this one.
    return "2027" in low or "2026" not in low


class GithubMirrorChecker:
    name = "github_mirror"

    def __init__(self) -> None:
        self._listings: dict[str, list[dict]] | None = None
        self._quant: dict[str, dict] | None = None
        self._errors: list[str] = []

    # ------------------------------------------------------------------ sources
    def _get(self, url: str, timeout: float = 25.0):
        import httpx
        return httpx.get(url, timeout=timeout, follow_redirects=True,
                         headers={"User-Agent": UA, "Accept": "application/json"})

    def _load_listings(self) -> dict[str, list[dict]]:
        if self._listings is not None:
            return self._listings
        index: dict[str, list[dict]] = {}
        try:
            resp = self._get(LISTINGS_URL)
            resp.raise_for_status()
            rows = json.loads(resp.text)
            for row in rows if isinstance(rows, list) else []:
                if not isinstance(row, dict) or not row.get("active", True):
                    continue
                key = _norm(row.get("company_name") or row.get("company") or "")
                if key:
                    index.setdefault(key, []).append(row)
        except Exception as exc:
            self._errors.append(f"listings:{type(exc).__name__}")
        self._listings = index
        return index

    def _load_quant(self) -> dict[str, dict]:
        """One YAML per firm. Fetched once, indexed by normalised firm name."""
        if self._quant is not None:
            return self._quant
        index: dict[str, dict] = {}
        try:
            import yaml
            resp = self._get(QUANT_INDEX)
            resp.raise_for_status()
            files = [f["name"] for f in resp.json()
                     if f["name"].endswith((".yaml", ".yml"))]
            for name in files:
                try:
                    raw = self._get(QUANT_RAW.format(name), timeout=15.0)
                    raw.raise_for_status()
                    doc = yaml.safe_load(raw.text) or {}
                except Exception:
                    continue
                key = _norm(doc.get("name") or name.rsplit(".", 1)[0])
                if key:
                    index[key] = doc
        except Exception as exc:
            self._errors.append(f"quant:{type(exc).__name__}")
        self._quant = index
        return index

    # ------------------------------------------------------------------ link validation
    def _link_live(self, url: str) -> tuple[bool, str, bool]:
        """Does this posting still exist?

        Verified 2026-07-24: two of five mirror hits pointed at dead reqs — Citadel
        Securities 404'd and Point72 redirected to /jobexpired. A community list is a
        snapshot of when a volunteer last looked, so "listed" and "still open" are
        different claims. Reporting an expired req as OPEN is the same class of error as
        reporting a blocked check as closed: it sends him somewhere on false confidence.
        """
        if not url:
            return False, "no_url", False
        try:
            import httpx
            resp = httpx.get(url, timeout=20.0, follow_redirects=True,
                             headers={"User-Agent": UA})
        except Exception as exc:
            # Network trouble is not proof the posting is gone — say we don't know.
            return False, f"unreachable:{type(exc).__name__}", False
        final = str(resp.url).lower()
        if resp.status_code in (404, 410):
            return False, f"http_{resp.status_code}", True     # the req is gone
        if resp.status_code >= 400:
            # 403/429 is a bot block, not an expiry. We learned nothing.
            return False, f"http_{resp.status_code}", False
        if any(m in final for m in EXPIRED_MARKERS):
            return False, "redirected_to_expired", True

        # Point72 (verified 2026-07-24) answers an expired req with HTTP 200 and a ~560-byte
        # body whose only content is a client-side redirect to /jobexpired. Checking the
        # status code and the final URL both pass; only reading the body catches it. Any ATS
        # that redirects in JavaScript will behave this way.
        body = resp.text[:8000].lower()
        if any(m in body for m in EXPIRED_MARKERS):
            return False, "body_says_expired", True
        if any(m in body for m in ("no longer accepting applications", "this job is no longer",
                                   "position has been filled", "posting has closed")):
            return False, "posting_closed", True
        # A page this small cannot be a real job description.
        if len(resp.text) < 900:
            return False, f"body_too_small:{len(resp.text)}b", True
        return True, "link_ok", True

    # ------------------------------------------------------------------ matching
    @staticmethod
    def _lookup(index: dict, key: str):
        if key in index:
            return index[key]
        # Substring fallback: "citadel" vs "citadelsecurities", "bp" vs "bpenergy".
        if len(key) >= 5:
            for k, v in index.items():
                if key in k or k in key:
                    return v
        return None

    def check(self, prog: dict, cfg: dict) -> Result:
        listings = self._load_listings()
        quant = self._load_quant()
        if not listings and not quant:
            return Result.failed(f"mirror_unreachable:{','.join(self._errors) or 'no data'}")

        key = cfg.get("mirror_key") or _norm(prog["firm"])
        total = len(listings) + len(quant)

        # --- quant repo first: it is role-typed, so it can tell trading from programming ---
        doc = self._lookup(quant, key)
        if isinstance(doc, dict):
            roles = doc.get("roles") or []
            wanted, coding_only = [], []
            for role in roles:
                rtype = (role.get("role_type") or "").upper()
                links = [l.get("url") for l in (role.get("links") or []) if l.get("url")]
                if not links:
                    continue
                (wanted if rtype in NON_CODING_ROLES else coding_only).append((rtype, links[0]))
            if wanted:
                rtype, url = wanted[0]
                live, why, definitive = self._link_live(url)
                if live:
                    return Result(ok=True, open=True, apply_url=url,
                                  evidence=f"mirror:quant2027 role={rtype} ({why})",
                                  title=f"{rtype} role listed", confidence="medium",
                                  board_key="mirror:quant2027", raw_count=total)
                # Only retract if the link is PROVABLY dead. We are withdrawing a claim we
                # ourselves made on the strength of that link — not inferring a closure from
                # silence, which the house rule forbids.
                return Result(ok=True, open=False if definitive else None,
                              evidence=f"mirror:quant2027 listed {rtype} but link {why}",
                              confidence="medium", board_key="mirror:quant2027",
                              raw_count=total)
            if coding_only:
                # Real listings exist, but every one is a programming seat. Saying "open"
                # here would send him at a job he cannot do.
                kinds = ",".join(sorted({r for r, _ in coding_only}))
                return Result(ok=True, open=None,
                              evidence=f"mirror:quant2027 only coding roles ({kinds})",
                              confidence="medium", board_key="mirror:quant2027",
                              raw_count=total)

        # --- general listings repo ---
        rows = self._lookup(listings, key) or []
        live = [r for r in rows if _is_2027_intern(r.get("title", ""))]
        non_coding = [r for r in live if not _is_coding_title(r.get("title", ""))]
        all_definitive, last_why = bool(non_coding), ""
        for best in non_coding:
            url = best.get("url") or best.get("application_link")
            live, why, definitive = self._link_live(url)
            last_why = why
            if not live and not definitive:
                all_definitive = False
            if live:
                return Result(ok=True, open=True, apply_url=url,
                              title=best.get("title"),
                              evidence=f"mirror:vanshb03-2027 \"{best.get('title', '')[:56]}\"",
                              confidence="medium", board_key="mirror:listings",
                              raw_count=total)
        if non_coding:
            return Result(ok=True, open=False if all_definitive else None,
                          evidence=f"mirror: listed, but every link is dead ({last_why})",
                          confidence="medium", board_key="mirror:listings", raw_count=total)
        if live:
            # The firm is posting for 2027, but every listing found is a programming seat.
            # Report that we cannot tell rather than pointing him at a job he cannot do.
            return Result(ok=True, open=None,
                          evidence=f"mirror: {len(live)} 2027 listing(s), all coding roles",
                          confidence="medium", board_key="mirror:listings",
                          raw_count=total)

        # Not a negative — see the module docstring.
        return Result(ok=True, open=None, evidence="mirror:no_match",
                      confidence="medium", board_key="mirror:index", raw_count=total)


register(GithubMirrorChecker())
