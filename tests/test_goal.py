from __future__ import annotations
import pytest
from stelar.etl import Goal

def test_goal_1(simple_catalog):
    # Create a catalog

    cat = simple_catalog

    goal = Goal(cat)
    goal.install("m3")

    assert goal._goal["m3"] is True
    assert len(goal._goal) == 1

    I, U = goal.logical_plan()

    assert len(I) == 2
    assert I == [cat.get("m1"), cat.get("m3")]

    assert len(U) == 0
    assert U == []


def test_goal_2(simple_catalog):
    # Create a catalog

    cat = simple_catalog

    goal = Goal(cat)
    goal.install("m2")

    assert goal._goal["m2"] is True
    assert len(goal._goal) == 1

    I, U = goal.logical_plan()

    assert len(I) == 5

    assert len(U) == 0
    assert U == []


def test_goal_3(simple_catalog):
    cat = simple_catalog

    goal = Goal(cat)
    goal.uninstall("m3")

    assert goal._goal["m3"] is False
    assert len(goal._goal) == 1

    I, U = goal.logical_plan()

    assert len(I) == 0

    assert len(U) == 5
    assert simple_catalog.get("m1") not in U


def test_goal_4(simple_catalog):
    cat = simple_catalog

    goal = Goal(cat)
    goal.install("m3")
    goal.uninstall("m2")

    assert goal._goal["m3"] is True
    assert goal._goal["m2"] is False
    assert len(goal._goal) == 2

    with pytest.raises(ValueError):
        goal.install("m2")
