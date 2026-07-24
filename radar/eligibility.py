"""Explicit, auditable eligibility classification.

Two questions the original curation never asked, both of which can waste an application:

  grad_2029  — Artyom graduates May 2029. Summer 2027 is his SOPHOMORE summer, not his
               penultimate one. A "Summer Analyst" programme that requires graduation
               between Dec 2027 and Jun 2028 is recruiting the class of 2028 and he is
               simply not eligible, however good the fit looks.
  coding     — he does not write Python/SQL. A posting that lists them as requirements is
               not a real option, and one that lists them as "preferred" is a stretch.

Both default to the honest answer, "unverified"/"unknown", rather than a flattering guess.
Everything unverified is listed on #/health as a curation to-do so the gap is visible
instead of silently optimistic.

Every entry below is a human judgement with its basis recorded. When a live checker or a
read of the actual posting contradicts one, fix it HERE — this is the single source.
"""

# ---------------------------------------------------------------- graduation year
# Verified NOT open to a May-2029 graduate for the Summer 2027 cycle.
GRAD_INELIGIBLE = {
    "castleton-commodities-cci-commercial-trading":
        "Artyom read the live Workday req 2026-07-24: requires graduation on or before "
        "spring 2028, i.e. the class of 2028. Not eligible for Summer 2027.",
}

# Explicitly open to first- or second-year students, or with no class-year gate at all.
GRAD_ELIGIBLE = {
    "kinder-morgan-finance": "BOLT states students entering sophomore, junior or senior year",
    "musket-corp-love-s-trading-commodities": "posting states sophomore+ explicitly",
    "deloitte-discovery": "open to all first- and second-years",
    "pwc-elevate": "open to any sophomore",
    "jane-street-first-year-trading": "programme is named for first-years/sophomores",
    "citadel-securities-discover-sophomore-trading": "first-year/sophomore programme",
    "susquehanna-sig-sophomore-trading": "sophomore programme",
    "optiver-sophomore-trading": "first-year/sophomore programme",
    "imc-trading-first-year-sophomore": "first-year/sophomore programme",
    "drw-sophomore": "sophomore programme",
    "akuna-capital-sophomore-trading": "sophomore programme",
    "point72-academy-sophomore-insight": "sophomore insight track",
    "blackrock-sophomore-future-analyst": "sophomore programme",
    "oliver-wyman-first-year-immersion": "first-year immersion",
    "ey-parthenon-emerging-leaders": "sophomore programme",
    "hudson-river-trading-inside-hrt-underclassmen": "HRT states first- and second-year eligibility",
    "millennium-management-meet-millennium-sophomore":
        "positioned for pre-penultimate students",
    "nyu-college-of-arts-science-dean-s-undergraduate":
        "FAST Grant is designed for first- and second-year students",
    "resources-for-the-future-rff-summer-research":
        "explicitly open to undergraduates, no class-year gate",
    "nyc-economic-development-corporation-summer-economic-research":
        "open to undergraduates, no class-year gate",
    "nyc-comptroller-s-office-bureau-budget-economic":
        "only requirement is being matriculated",
    "nyc-office-of-management-and-budget-summer-college-economic":
        "only requirement is undergraduate enrolment",
    "brookings-institution-research-economic-studies": "written for rising juniors",
    "council-on-foreign-relations-greenberg-center-geoeconomic":
        "requires the equivalent of two completed years — he will have two by summer 2027",
    "american-economic-association-aea-summer-training":
        "takes enrolled undergraduates including rising juniors",
    "federal-reserve-bank-of-ny-sophomore-career-exploration":
        "the programme is built for current sophomores",
    "predoc-opportunities-board-ra": "board lists roles open to current students",
}

# ---------------------------------------------------------------- coding requirement
# Postings that list programming as a REQUIREMENT. He does not code, so these are out.
CODING_REQUIRED = {
    "castleton-commodities-cci-data-science-technology":
        "cci.com/careers/students verbatim: 'strong foundation in programming, "
        "particularly in Python and/or SQL'",
    "hudson-river-trading-inside-hrt-underclassmen":
        "HRT is a quant-dev shop; stated fields are CS/maths and the work is programming",
    "predoc-opportunities-board-ra":
        "predoc/RA roles essentially always require Stata, R or Python",
    "federal-reserve-board-of-governors-research-assistant-research":
        "Fed RA roles require statistical programming (Stata/MATLAB/R)",
    "federal-reserve-bank-of-new-york-research-statistics-summer":
        "posting asks for SAS/Stata/MATLAB/Python plus large-database work",
    "federal-reserve-bank-of-dallas-research-data-analyst":
        "research/data analyst track is statistical-software based",
}

# Programming helps but is not gating — quantitative trading roles test probability and
# mental maths, not code, and most corporate finance roles run on Excel.
CODING_PREFERRED = {
    "jane-street-first-year-trading", "citadel-securities-discover-sophomore-trading",
    "susquehanna-sig-sophomore-trading", "optiver-sophomore-trading",
    "imc-trading-first-year-sophomore", "drw-sophomore", "akuna-capital-sophomore-trading",
    "point72-academy-sophomore-insight", "d-e-shaw-discovery-affinity",
    "resources-for-the-future-rff-summer-research",
    "nyc-comptroller-s-office-bureau-budget-economic",
    "dimensional-fund-advisors-summer",
}


def grad_2029(pid: str) -> tuple[str, str]:
    """Returns (status, basis). Default is the honest 'unverified'."""
    if pid in GRAD_INELIGIBLE:
        return "ineligible", GRAD_INELIGIBLE[pid]
    if pid in GRAD_ELIGIBLE:
        return "eligible", GRAD_ELIGIBLE[pid]
    return "unverified", "class-year requirement not yet read from the posting"


def coding(pid: str) -> tuple[str, str]:
    if pid in CODING_REQUIRED:
        return "required", CODING_REQUIRED[pid]
    if pid in CODING_PREFERRED:
        return "preferred", "quantitative role — programming helps but is not gating"
    return "unknown", "coding requirement not yet read from the posting"
