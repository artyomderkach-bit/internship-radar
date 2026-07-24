"""Contract tests for the community-mirror checker.

Two things must stay true no matter how the parsing evolves:

  1. The mirror may NEVER report `open=False`. These repos are SWE-focused and barely cover
     Houston commodities or Fed research, so a miss is absence of evidence, not evidence of
     absence. Reporting a negative would start the chain that ends in a false `closed`.
  2. A programming role must never be reported as an opening. Artyom does not write code;
     pointing him at a Trading Systems Engineering req wastes an evening.
"""

from radar.checkers.github_mirror import (
    GithubMirrorChecker, _is_2027_intern, _is_coding_title, _norm,
)

PROG = {"id": "x", "firm": "Test Firm", "program": "Sophomore Trading"}


class FakeMirror(GithubMirrorChecker):
    """Subclass with the network pre-empted, so tests are hermetic."""

    def __init__(self, listings=None, quant=None):
        super().__init__()
        self._listings = listings or {}
        self._quant = quant or {}


def test_mirror_never_reports_a_negative():
    """No match at all — must be indeterminate, never 'not open'."""
    res = FakeMirror(listings={"other": []}, quant={"other": {}}).check(PROG, {})
    assert res.ok is True
    assert res.open is None, "a mirror miss must never be a negative"


def test_coding_only_quant_listing_is_not_an_opening():
    quant = {"testfirm": {"name": "Test Firm", "roles": [
        {"role_type": "SWE", "links": [{"url": "http://swe"}]},
        {"role_type": "QR", "links": [{"url": "http://qr"}]},
    ]}}
    res = FakeMirror(quant=quant).check(PROG, {})
    assert res.open is None
    assert "coding" in res.evidence


def test_trading_role_is_an_opening_at_medium_confidence():
    quant = {"testfirm": {"name": "Test Firm", "roles": [
        {"role_type": "QT", "links": [{"url": "http://qt"}]},
    ]}}
    res = FakeMirror(quant=quant).check(PROG, {})
    assert res.open is True
    assert res.apply_url == "http://qt"
    # Never "high": a human posted this, we did not verify it against the firm.
    assert res.confidence == "medium"


def test_coding_titles_in_the_general_listings_are_filtered_out():
    listings = {"testfirm": [
        {"title": "Software Engineer Intern 2027", "url": "http://swe", "active": True},
    ]}
    res = FakeMirror(listings=listings).check(PROG, {})
    assert res.open is None, "a SWE listing must not mark a trading programme open"


def test_non_coding_listing_is_an_opening():
    listings = {"testfirm": [
        {"title": "Investment Analyst Intern, Academy", "url": "http://ok", "active": True},
    ]}
    res = FakeMirror(listings=listings).check(PROG, {})
    assert res.open is True and res.apply_url == "http://ok"


def test_unreachable_sources_fail_rather_than_report_nothing_found():
    """A dead network is a broken check, not 'no internships exist'."""
    res = FakeMirror(listings={}, quant={}).check(PROG, {})
    assert res.ok is False
    assert res.open is None


def test_title_and_name_helpers():
    assert _is_coding_title("Quantitative Research Intern")
    assert _is_coding_title("FPGA Engineer")
    assert not _is_coding_title("Sophomore Trading Internship")
    assert _is_2027_intern("Summer Analyst Intern 2027")
    assert not _is_2027_intern("Head of Trading")
    assert _norm("Castleton Commodities (CCI)") == "castletoncommodities"
