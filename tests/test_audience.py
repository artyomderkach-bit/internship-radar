"""Board membership: every programme lands on the right sibling's board, and only there
where it should. The twins share the class-of-2029 arithmetic but not a career."""

from radar.audience import SISTER_EXCLUDE, SISTER_INCLUDE, for_artyom, for_sister
from radar.registry import load_seed


def prog(sector="Finance", loc_bucket="NYC", quant=False, pid="x"):
    return {"id": pid, "sector": sector, "loc_bucket": loc_bucket, "quant_role": quant}


# ---------------------------------------------------------------- rule behaviour

def test_hr_rows_are_hers_and_never_his():
    row = prog(sector="HR & Talent", loc_bucket="Houston")
    assert for_sister(row) and not for_artyom(row)


def test_everything_else_stays_on_his_board():
    for sector in ("Energy", "Finance", "Consulting"):
        assert for_artyom(prog(sector=sector))


def test_she_shares_nyc_houston_finance_and_energy():
    assert for_sister(prog(sector="Finance", loc_bucket="NYC"))
    assert for_sister(prog(sector="Energy", loc_bucket="Houston"))


def test_she_does_not_get_consulting_other_cities_or_quant_seats():
    assert not for_sister(prog(sector="Consulting"))
    assert not for_sister(prog(sector="Finance", loc_bucket="Other"))
    assert not for_sister(prog(sector="Finance", quant=True))


def test_overrides_beat_the_rule():
    inc, exc = prog(pid="inc-id", sector="Consulting"), prog(pid="exc-id", sector="Finance")
    SISTER_INCLUDE["inc-id"] = "test"
    SISTER_EXCLUDE["exc-id"] = "test"
    try:
        assert for_sister(inc) and not for_sister(exc)
    finally:
        del SISTER_INCLUDE["inc-id"], SISTER_EXCLUDE["exc-id"]


# ---------------------------------------------------------------- whole-seed invariants

def test_no_seed_row_is_orphaned():
    """A curated programme nobody sees is silent waste — every row belongs somewhere."""
    for p in load_seed():
        assert for_artyom(p) or for_sister(p), p["id"]


def test_his_board_is_exactly_the_non_hr_seed():
    seed = load_seed()
    his = [p for p in seed if for_artyom(p)]
    assert len(his) == sum(1 for p in seed if p["sector"] != "HR & Talent")


def test_her_board_never_carries_a_quant_seat():
    for p in load_seed():
        if for_sister(p) and p["id"] not in SISTER_INCLUDE:
            assert not p.get("quant_role", False), p["id"]
