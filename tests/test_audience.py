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


def test_she_never_gets_finance_energy_or_consulting_roles():
    """Her rule (Artyom, 2026-08-22): HR/headhunting doors only — people-work AT a
    finance or energy firm is curated as HR & Talent; the firm's finance and energy
    ROLES stay off her board however good they look."""
    for sector in ("Finance", "Energy", "Consulting"):
        assert not for_sister(prog(sector=sector, loc_bucket="NYC"))
        assert not for_sister(prog(sector=sector, loc_bucket="Houston"))


def test_overrides_beat_the_rule():
    inc = prog(pid="inc-id", sector="Finance")           # a people-analytics seat, say
    exc = prog(pid="exc-id", sector="HR & Talent")
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


def test_her_board_is_exactly_the_hr_talent_rows():
    seed = load_seed()
    hers = {p["id"] for p in seed if for_sister(p)}
    assert hers == {p["id"] for p in seed if p["sector"] == "HR & Talent"}
    assert not any(p.get("quant_role", False) for p in seed if p["id"] in hers)
