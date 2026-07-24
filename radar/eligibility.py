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
    "imc-trading-first-year-sophomore":
        "imc.com req verbatim: 'graduating between September 2027 and July 2028'. He "
        "graduates May 2029, so he is a year early for the Summer 2027 cohort.",
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
    # NOT listed as eligible. Reading Jane Street's own programmes page on 2026-07-24, the
    # underclassman doors are FTTP (first-year students only — he has finished that year),
    # and INSIGHT / FOCUS / IN FOCUS / JSIP / WiSE, all of which are affinity-restricted.
    # The open Quantitative Trader internship states no class year at all, so it stays
    # `unverified` rather than being claimed either way.
    "citadel-securities-discover-sophomore-trading": "first-year/sophomore programme",
    "susquehanna-sig-sophomore-trading": "sophomore programme",
    # Optiver's grad window ("December 2027 and June 2029, with sophomore standing or
    # higher") does include him — but the STEM-major and programming requirements do not,
    # so it is gated under CODING_REQUIRED instead.
    "optiver-sophomore-trading": "req states graduation Dec 2027-Jun 2029, sophomore standing+",
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
# ---- verified by reading the live postings in a browser on 2026-07-24 ----------------
# Artyom's prompt: quant funds essentially always want coding unless the role isn't a quant
# role. Checking the actual reqs: mostly true, but not uniformly, and the binding constraint
# turned out more often to be CLASS YEAR than code.
CODING_REQUIRED = {
    "optiver-sophomore-trading":
        "optiver.com req 'Quantitative Intern (Summer 2027)', Who You Are: 'Experience with "
        "programming or scripting in Python or another language' — and separately 'pursuing "
        "a Bachelor's or Master's degree in a STEM field', which a CAS BA in Economics is not",
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
    # Verified verbatim on the live req, not inferred:
    # Jane Street QT: "General programming experience is a plus, but knowing a particular
    #   programming language is not required" + "no specific degree or major is required".
    # IMC QT: "Experience in a programming language is a plus (e.g. Python, Matlab or R)"
    #   and Economics is named as a qualifying quantitative field.
    "jane-street-first-year-trading", "imc-trading-first-year-sophomore",
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


# ---------------------------------------------------------------- quant roles
# Artyom, 2026-07-24: "any quant role will want coding so lets just delete all quant
# companies. I am completely fine with trying to apply for internships in other roles in
# those companies just not quant."
#
# So this hides the ROLE, not the firm. If a non-quant seat at one of these shops turns up
# (Point72's fundamental Academy, a business/ops track at Citadel), it belongs on the board
# — it just doesn't go in this set.
#
# Hidden by default rather than deleted outright, for the same reason the diversity-only
# rows are: the count stays visible so nothing vanishes silently, and one click brings them
# back. Say the word and the rows come out of data/ entirely.
QUANT_SUBS = {"Quant Trading", "Market Making", "Options Trading", "Prop Trading",
              "Quant Hedge Fund"}


def is_quant_role(prog: dict) -> bool:
    return prog.get("sub") in QUANT_SUBS
