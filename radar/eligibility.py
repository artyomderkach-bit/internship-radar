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
    "castleton-commodities-cci-merchant-operations-finance":
        "CCI Workday req R1338 'Operations & Finance Leadership Internship Program "
        "(Summer 2027 Start)', read 2026-07-24, verbatim: 'Expected graduation date of "
        "Winter 2027 or Spring 2028'. Same class-of-2028 gate as the trading req. "
        "(Excel/VBA is only 'a plus' — it is the class year that rules him out.)",
    "castleton-commodities-cci-data-science-technology":
        "same CCI Summer 2027 cohort, and separately requires Python/SQL",
    "imc-trading-first-year-sophomore":
        "imc.com req verbatim: 'graduating between September 2027 and July 2028'. He "
        "graduates May 2029, so he is a year early for the Summer 2027 cohort.",
    "castleton-commodities-cci-commercial-trading":
        "Artyom read the live Workday req 2026-07-24: requires graduation on or before "
        "spring 2028, i.e. the class of 2028. Not eligible for Summer 2027.",
    # ---- 2026-07-25 research sweep: read from the firm's own page or live req ----------
    "capital-group-associate":
        "capitalgroup.com CAP page verbatim: 'Undergraduate students in their junior "
        "(penultimate) year may apply for a 10-week CAP Summer Internship'. Summer 2027 "
        "recruits the class of 2028.",
    "alliancebernstein-summer":
        "alliancebernstein.com students FAQ verbatim: 'We only offer opportunities to "
        "juniors and seniors at this time' and 'students who have successfully completed "
        "their junior year'. Explicit bar on sophomores.",
    "analysis-group-sophomore-analyst":
        "analysisgroup.com summer-analyst page verbatim: interns are 'rising seniors and "
        "first-year master's students'. Not a sophomore programme despite the curated row.",
    "the-brattle-group-research-associate":
        "brattle.com summer-internships page verbatim: 'Rising seniors pursuing a "
        "Bachelor's degree in a quantitative discipline'. Summer 2027 = class of 2028.",
    "nera-economic-consulting-analyst":
        "nera.com student FAQ verbatim: 'we offer summer internships to final-year "
        "undergraduate candidates as well as current master's and PhD students'.",
    "macquarie-group-commodities-global-markets":
        "macquarie.com US programs page verbatim: 'students heading into their penultimate "
        "year of study are invited to apply'. The 2027 intake (apps open Aug 2026) recruits "
        "the class of 2028; his window is the 2028 intake, applying Aug 2027.",
    "dimensional-fund-advisors-summer":
        "careers.dimensional.com verbatim: internships are for 'students the summer before "
        "their final year of school'. Summer 2027 excludes him; Summer 2028 (apply Aug-Dec "
        "2027) is his window.",
    "trafigura-commercial-graduate":
        "Live Workday req R-018269 (Houston Commercial Graduate Programme, read "
        "2026-07-25): a post-degree trainee programme requiring a completed quantitative "
        "degree by Sept 2027 — impossible for a May-2029 grad. No undergraduate summer "
        "internship exists at Trafigura US.",
    "vitol-commercial-trading":
        "vitol.com careers (read 2026-07-25): the only early-careers route is London-based "
        "and asks 'Are you in your final year of study or a recent graduate?'. No US "
        "internship or sophomore programme exists.",
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
    "deloitte-discovery": "open to all first- and second-year students",
    "pwc-elevate": "open to any sophomore",
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
    # ---- 2026-07-25 research sweep: read from the firm's own page or live req ----------
    "t-rowe-price-summer":
        "Summer 2027 Equity Research req LIVE on troweprice.gr8people.com (read "
        "2026-07-25) verbatim: 'expected graduation date of December 2027 – May/June "
        "2029' — the class of 2029 is explicitly in range. GPA 3.5 minimum.",
    "fidelity-investments-summer-analyst-sophomore":
        "jobs.fidelity.com/students verbatim: 'You apply during the fall of your sophomore "
        "or junior year'; Summer 2027 applications open Fall 2026 — maps exactly to his "
        "sophomore year.",
    "vanguard-sophomore-early-talent":
        "vanguardjobs.com/students verbatim: College to Corporate internship is for "
        "'college sophomores and juniors who are currently enrolled'. Apps typically open "
        "in August.",
    "wellington-management-sophomore-early-insight":
        "wellington.com campus-programs verbatim: the 10-week summer internship takes "
        "'current sophomores and juniors'. (The HBCU Scholars sibling is "
        "diversity-restricted; this row is the open programme.)",
    "calpine-finance":
        "calpine.com/careers/internships verbatim: 'At least Sophomore status (30 credit "
        "hours)', GPA 3.0+ — a rising junior in Summer 2027 clears the floor comfortably.",
    "centerpoint-energy-finance":
        "centerpointenergy.com undergraduate business internships page: 'Junior or senior "
        "standing preferred' — a stated preference, not a gate, so a sophomore may apply "
        "(expect an uphill field).",
    "accenture-student-leadership":
        "accenture.com Student Leadership Program page verbatim: 'Second-year students "
        "enrolled in a four-year undergraduate program' (2026-edition language; 2027 "
        "registration not yet open). A semester leadership programme feeding Summer "
        "Analyst recruiting, not itself an internship.",
    "kalshi-internships-rolling-no":
        "live Ashby req (read 2026-07-25): college enrollment is only a 'nice-to-have' — "
        "no class-year gate at all; hiring is rolling/ad-hoc rather than a structured "
        "summer programme.",
    "polymarket-summer-marketing-finance":
        "Ashby general-interest posting (live 2026-07-25): 'currently pursuing an "
        "undergraduate degree in marketing, finance, economics, business...' — no "
        "class-year gate; the 2027 programme has not formally launched.",
    "goldman-sachs-emerging-leaders-series":
        "goldmansachs.com programme page verbatim: 'Undergraduate students graduating "
        "between December 2028 - June 2029'; applications open fall 2026.",
    "citi-early-id-leadership":
        "jobs.citi.com pre-internships page verbatim: 'US sophomores enrolled in a "
        "four-year bachelor's degree'; December cohort apps open in November, March "
        "cohort in February.",
    "jpmorganchase-career-edyou-academy":
        "jpmorganchase.com programme page verbatim: 'designed for college sophomores "
        "studying in the United States'.",
    "jpmorganchase-fellowship-sophomore-summer":
        "jpmorganchase.com fellowship page verbatim: 'All sophomore students who are "
        "interested in the JPMorganChase fellowship program, regardless of background, "
        "are welcome to apply' — a five-week paid sophomore-summer fellowship.",
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
    # 2026-07-25 sweep — postings list tools as pluses, not requirements:
    # EDF 2026 intern req: "SQL, Python, Tableau or similar" under preferred.
    # Gunvor 2026 req: Python/R/Tableau "would be advantageous".
    # Koch 2027 Finance Analyst req: PowerBI/Alteryx/Tableau + Python/SQL/R/VBA listed
    # only under "what puts you ahead"; Excel is the requirement.
    "edf-trading-north-america-commercial-summer", "gunvor-trading",
    "koch-supply-trading-commercial-trading",
}


# ---------------------------------------------------------------- sophomore confidence
# One number, 0-100, answering: "how confident are we that a class-of-2029 sophomore can
# actually get INTO this programme for Summer 2027?" The score measures EVIDENCE QUALITY,
# never optimism — house rule: a false negative is worse than a false positive, but an
# unverified claim must still LOOK unverified.
#
#   90-100  class-year language read verbatim from the firm's own posting/page and it
#           includes him (sophomore / class-of-2029 explicitly in range)
#   70-89   the firm's own page describes a first/second-year track, but this cycle's
#           req is not live yet, or the language is programme-level rather than req-level
#   50-69   evidence is from LAST cycle's posting, or a consistent multi-year pattern
#   30-49   no class-year language found anywhere — the curated "Sophomore+" is a claim
#   10-29   prose or history says the programme really targets juniors/penultimate years
#    0-9    verified class-year gate that excludes a May-2029 graduate
#
# Every explicit entry records its basis. Rows absent from this table get an honest
# default derived from what grad_2029() and the curated notes already establish.
#
# Populated 2026-07-25 from a firm-by-firm read of official pages and live reqs (mirrors
# noted where the firm domain blocked fetches). Verbatim quotes live in GRAD_ELIGIBLE /
# GRAD_INELIGIBLE where the verdict is settled; the basis here says what was actually read.
SOPH_SCORE: dict[str, tuple[int, str]] = {
    # ---- verified this cycle, firm's own words include him -------------------------
    "t-rowe-price-summer": (97,
        "Summer 2027 req LIVE on the firm's own ATS: grad window Dec 2027 - May/June 2029 "
        "explicitly includes the class of 2029"),
    "fidelity-investments-summer-analyst-sophomore": (95,
        "firm page: apply in fall of sophomore year; Summer 2027 apps open Fall 2026"),
    "goldman-sachs-emerging-leaders-series": (95,
        "firm page: 'graduating between December 2028 - June 2029' — his class exactly"),
    "optiver-sophomore-trading": (95,
        "req verbatim: graduation Dec 2027-Jun 2029 with sophomore standing+ — the class "
        "year fits; it is the STEM/programming gate that rules him out (see coding)"),
    "vanguard-sophomore-early-talent": (92,
        "firm page: C2C internship for 'college sophomores and juniors'"),
    "wellington-management-sophomore-early-insight": (92,
        "firm page: summer internship takes 'current sophomores and juniors'"),
    "citi-early-id-leadership": (92,
        "firm page: 'US sophomores enrolled in a four-year bachelor's degree'"),
    "musket-corp-love-s-trading-commodities": (92,
        "posting states sophomore+ explicitly (verified 2026-07-24)"),
    "kinder-morgan-finance": (90,
        "BOLT page: 'students entering sophomore, junior or senior year'"),
    "deloitte-discovery": (90, "firm page: open to all first- and second-years"),
    "pwc-elevate": (90, "firm page: open to any sophomore"),
    "calpine-finance": (90,
        "firm page: 'At least Sophomore status (30 credit hours)' — an explicit floor "
        "he clears"),
    "accenture-student-leadership": (90,
        "firm page: 'Second-year students' — 2026-edition language; 2027 registration "
        "not yet open"),
    "jpmorganchase-career-edyou-academy": (90,
        "firm page: 'designed for college sophomores studying in the United States'"),
    "hudson-river-trading-inside-hrt-underclassmen": (90,
        "HRT states first- and second-year eligibility; a Summer 2027 req went live "
        "2026-07-25 — but the work is programming (see coding)"),
    "jpmorganchase-fellowship-sophomore-summer": (88,
        "firm page: all sophomores welcome regardless of background; five-week paid "
        "summer fellowship"),
    "kalshi-internships-rolling-no": (85,
        "live req: no class-year gate at all — but hiring is ad-hoc, not a structured "
        "summer programme"),
    "polymarket-summer-marketing-finance": (82,
        "live Ashby posting: any undergrad in econ/finance/marketing qualifies; 2027 "
        "programme not yet formally launched"),
    # ---- open by preference or pattern, not yet this-cycle-verbatim ----------------
    "centerpoint-energy-finance": (70,
        "firm page: 'Junior or senior standing preferred' — a preference, not a gate; "
        "he can apply but competes uphill"),
    "shell-commercial-trading-assessed": (65,
        "Summer 2026 US posting (mirror): only academic gate is one more semester "
        "remaining after the internship + GPA 3.20 — no class-year bar. 2027 req "
        "expected fall 2026"),
    "cheniere-energy-commercial-finance": (60,
        "official page has no class-year gate and lists Commercial + Finance & Treasury "
        "intern functions; Vault profile explicitly lists sophomores — aggregator-backed, "
        "confirm on the fall 2026 posting"),
    "williams-finance": (60,
        "Summer 2026 posting (mirror): 'graduation date of December 2026 or beyond' is a "
        "floor, not a ceiling — May 2029 qualifies as written; reqs post mid-August"),
    "pimco-sophomore-early-insight": (60,
        "PIMCO Prep is freshman/sophomore-branded and feeds summer internships, but the "
        "readable evidence is a prior-cycle aggregator posting — pimco.com blocked every "
        "fetch. The 'Early Insights' sibling is diversity-restricted"),
    "totalenergies-us-internships-trading": (60,
        "firm US university-relations page lists Trading among internship divisions; "
        "'at least a sophomore with a 2.8 GPA' verbatim is from its refinery site "
        "programme — trading roles carry no stated class gate"),
    "gunvor-trading": (55,
        "Summer 2026 Houston req (aggregator copy of dead posting): 'currently pursuing "
        "or recently completed a degree' — no class-year gate; 2027 req expected fall "
        "2026, deadline ~Nov 30"),
    "edf-trading-north-america-commercial-summer": (55,
        "2026 Commercial Summer Internship (mirror): only requirement is currently "
        "pursuing a degree in listed fields — no class-year gate; aggregator evidence, "
        "2027 req not yet live"),
    "plains-all-american-finance": (55,
        "aggregator snippets: PAA Internship Program targets 'sophomores, juniors, or "
        "seniors' — but plains.com renders JS-only and no page with that language could "
        "be fetched"),
    "constellation-energy-commercial": (55,
        "firm page: 10-week paid internships for 'students currently pursuing their "
        "bachelor's or 2-year technical degree' — no class-year gate stated"),
    "equinor-summer-finance-trading": (55,
        "firm page: 2027 application window stated (25 Sep - 15 Oct 2026), no class-year "
        "gate; US/Houston availability verified only from the 2026-cycle posting"),
    # ---- unknown: nothing readable either way ---------------------------------------
    "ey-summer-leadership-launch": (50,
        "ey.com pages carry no Launch eligibility text; indexed copy says 'at least two "
        "years or more from graduation' (fits) with NABA/ALPFA/HBSA preference — "
        "unconfirmed on a live page"),
    "slb-schlumberger-finance": (50,
        "firm page: only gate is studying toward an accounting degree/qualification — "
        "no class year; the finance intern track is framed around accounting majors"),
    "halliburton-finance": (50,
        "Summer 2025 Accounting Intern posting (mirror, two cycles back): no class-year "
        "gate; firm pages carry no eligibility text"),
    "freeport-lng-summer": (50,
        "firm page: 'college students' generally, no class-year gate stated; commercial "
        "intern roles posted in past cycles"),
    "phillips-66-finance-commercial": (45,
        "firm interns page: 'undergraduate and graduate students', no class-year gate; "
        "an unfetched snippet cited a 2-year grad window that would include May 2029 if "
        "it rolls forward"),
    "exxonmobil-business-commercial-summer": (45,
        "firm page silent on class year; third-party guides claim a completed-sophomore "
        "minimum. Reqs open ~Aug 2026"),
    "enterprise-products-finance": (45,
        "firm page publishes no eligibility criteria; application is emailing resume + "
        "transcript to campus recruiting — a direct email is the practical way to test "
        "sophomore eligibility"),
    "baker-hughes-finance-fmp": (45,
        "Summer 2026 Houston Finance req now returns HTTP 410; snippets say enrolled "
        "Bachelor's/Master's + GPA 3.0 with no class-year gate — unconfirmed. The "
        "evergreen page describes the post-degree FMP, not the internship"),
    "glencore-commercial": (45,
        "firm early-careers USA page (stale — still says Summer 2025): Houston/NYC "
        "internships for students, no class-year criteria published"),
    "blackstone-future-women-leaders": (45,
        "class year likely fits (snippets: first-year and sophomore women) but every "
        "Blackstone page blocked fetches — and the programme is women-only, so the "
        "affinity gate applies regardless"),
    "bain-company-bel-on-case": (45,
        "bain.com: 2027 BEL edition confirmed coming, but ALL eligibility criteria have "
        "been removed from the page; historically sophomore-only with an affinity gate — "
        "watch when 2027 details post"),
    "invesco-summer-investments-finance": (40,
        "early-careers page has no eligibility language and zero intern reqs live; "
        "Summer 2027 opens in the fall — recheck the Workday board Aug-Sep"),
    "targa-resources-finance-commercial": (40,
        "targaresources.com timed out on every fetch 2026-07-25; no eligibility "
        "language read anywhere"),
    "nrg-energy-finance-commercial": (40,
        "official Student Opportunities page: no intern reqs live, no class-year "
        "language beyond 'graduate and undergraduate students'"),
    "kearney-sophomore-first-year": (40,
        "kearney.com blocked fetches; third-party references early-insight events with "
        "apps closing Sept-Oct of sophomore year — would suit 2026-27, unconfirmed"),
    # ---- evidence points against, short of a verified gate --------------------------
    "conocophillips-spirit-commercial-finance": (35,
        "careers FAQ has no class-year language; last cycle's snippets: Commercial = "
        "Junior/Senior/Grad (excludes him), Accounting & Finance = Sophomore-Senior. "
        "Mixed doors — verify when 2027 reqs post in fall"),
    "eog-resources-finance-commercial": (35,
        "college-recruiting page lists no finance/commercial track (closest is "
        "accounting) and no class-year language"),
    "state-street-sophomore-early": (35,
        "no sophomore programme found anywhere on the firm domain; 'Summer Sophomore "
        "Intern' branding appears only on aggregators — unconfirmed the door exists"),
    "strategy-pwc-sophomore-early-insight": (35,
        "pwc.com blocked fetches; third-party: the sophomore doors are Start "
        "(underrepresented backgrounds) and Women's Consulting Experience — both "
        "affinity-oriented, neither confirmed"),
    "cornerstone-research-sophomore-analyst": (25,
        "firm analyst page has no class-year language; aggregator summaries say Summer "
        "2027 requires Dec 2027-Jun 2028 graduation (class of 2028) — unconfirmed but "
        "bearish"),
    "charles-river-associates-cra-analyst": (25,
        "no US Summer 2027 req live; last cycle's titles ('2027 Bachelor's graduates ... "
        "Summer 2026') show a penultimate-year pattern that would exclude him"),
    "mercuria-trading": (25,
        "no US summer internship exists — only an EPFL Masters trainee track and a "
        "full-time apprenticeship; ad-hoc intern postings would appear on LinkedIn/site"),
    "l-e-k-consulting-sophomore-insight": (20,
        "Kaleidoscope page content removed; third-party describes it as a "
        "sophomore/junior diversity programme (Black, Hispanic/Latinx, Indigenous) — "
        "affinity gate"),
    "boston-consulting-group-growing-future-leaders": (20,
        "official GFL URLs now redirect to the generic on-campus page; indexed copies "
        "describe a sophomore diversity internship (affinity gate) — programme may be "
        "discontinued or renamed ('BCG Advance')"),
    "bp-commercial-energy-trading": (15,
        "Summer 2026 req (mirror; bp.com blocked fetches): 'Graduating between December "
        "2026 and May 2027 ... 3rd year of a four-year degree program' — juniors-only; "
        "rolled to 2027 that is the class of 2028"),
    "chevron-finance-commercial": (15,
        "FDP intern descriptions (aggregator, last cycle): juniors with intermediate "
        "accounting coursework, grads within ~1 yr of the internship — excludes a "
        "sophomore if it holds for 2027; not verified on chevron.com"),
    "koch-supply-trading-commercial-trading": (15,
        "no KS&T intern req exists; the adjacent LIVE Koch Summer 2027 Finance/Risk "
        "Analyst internships require full-time eligibility 'no later than Summer 2028' — "
        "excludes May 2029 if KS&T recruits through this pipeline"),
    "zs-associates-sophomore-early-insight": (15,
        "zs.com internships page targets final/penultimate-year students; no sophomore "
        "early-insight programme found on the domain — the tracked door may not exist"),
    "kpmg-embark-scholars-rise": (15,
        "Embark gate is first-generation OR community-college students in accounting/IT "
        "degree tracks — an Econ BA does not fit; Rise is a conference with no "
        "published criteria"),
    "mckinsey-company-achievement-award-freshman": (12,
        "mckinsey.com timed out; search evidence: US early programmes (Up Next, El "
        "Futuro, Ignite) are first-year-only — his freshman window has passed — and "
        "Achievement Awards is affinity-gated and reportedly closed"),
    # ---- verified out (bases in GRAD_INELIGIBLE) ------------------------------------
    "vitol-commercial-trading": (5, "no US internship; early-careers route is final-year/"
        "recent-grad only (firm page, read 2026-07-25)"),
    "capital-group-associate": (5,
        "CAP is junior/penultimate-year only (firm page, read 2026-07-25)"),
    "macquarie-group-commodities-global-markets": (5,
        "penultimate-year intake (firm page, read 2026-07-25); his window is the 2028 "
        "Summer Analyst intake, applying Aug 2027"),
    "dimensional-fund-advisors-summer": (3,
        "summer-before-final-year only (firm page, read 2026-07-25); Summer 2028 is his "
        "eligible window — apply Aug-Dec 2027"),
    "trafigura-commercial-graduate": (3,
        "post-degree graduate programme (live req, read 2026-07-25); no undergraduate "
        "summer internship exists"),
    "alliancebernstein-summer": (3,
        "explicit FAQ bar on sophomores (firm page, read 2026-07-25)"),
    "analysis-group-sophomore-analyst": (3,
        "rising seniors only (firm page, read 2026-07-25)"),
    "the-brattle-group-research-associate": (3,
        "rising seniors only (firm page, read 2026-07-25)"),
    "nera-economic-consulting-analyst": (3,
        "final-year undergraduates only (firm page, read 2026-07-25)"),
}


def soph_score(pid: str, grad: str, derived_confidence: str) -> tuple[int, str]:
    """(score 0-100, basis). Explicit research wins; defaults are derived, never invented."""
    if pid in SOPH_SCORE:
        return SOPH_SCORE[pid]
    if grad == "ineligible":
        return 3, "verified class-year gate excludes the class of 2029 — see grad_2029 basis"
    if grad == "eligible":
        return 80, ("class-year eligibility verified (see grad_2029 basis); "
                    "this cycle's req not yet re-read")
    if derived_confidence == "doubtful":
        return 25, ("curated notes suggest the programme really targets "
                    "juniors/penultimate-year students")
    if derived_confidence == "confirmed":
        return 70, ("curated notes quote the firm's own sophomore language; "
                    "posting not yet re-read this cycle")
    return 40, "class-year requirement not yet read from any posting — unknown, not a yes"


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
