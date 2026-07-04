import pytest

from backend import training_store


def test_get_plan_defaults_to_empty_days():
    conn = training_store.get_connection(":memory:")
    plan = training_store.get_plan(conn=conn)
    assert list(plan.keys()) == training_store.DAYS_OF_WEEK
    assert all(description == "" for description in plan.values())


def test_set_day_and_get_plan():
    conn = training_store.get_connection(":memory:")
    training_store.set_day("Montag", "Push Day: Bankdrücken 4x8, Schulterdrücken 3x10", conn=conn)

    plan = training_store.get_plan(conn=conn)

    assert plan["Montag"] == "Push Day: Bankdrücken 4x8, Schulterdrücken 3x10"
    assert plan["Dienstag"] == ""


def test_set_day_overwrites_existing():
    conn = training_store.get_connection(":memory:")
    training_store.set_day("Montag", "Alter Plan", conn=conn)
    training_store.set_day("Montag", "Neuer Plan", conn=conn)

    plan = training_store.get_plan(conn=conn)

    assert plan["Montag"] == "Neuer Plan"


def test_set_day_rejects_invalid_day():
    conn = training_store.get_connection(":memory:")
    with pytest.raises(training_store.InvalidDayError):
        training_store.set_day("Blursday", "irrelevant", conn=conn)
