from periodic_table_tui.data import CATEGORY_COLORS, ELEMENTS, ELEMENTS_BY_NUMBER


def test_all_118_elements_present():
    assert len(ELEMENTS) == 118
    assert {e.number for e in ELEMENTS} == set(range(1, 119))


def test_atomic_numbers_are_unique_keys():
    assert len(ELEMENTS_BY_NUMBER) == 118
    assert ELEMENTS_BY_NUMBER[1].symbol == "H"
    assert ELEMENTS_BY_NUMBER[118].symbol == "Og"


def test_every_element_has_a_known_category():
    for element in ELEMENTS:
        assert element.category in CATEGORY_COLORS


def test_grid_positions_do_not_collide():
    positions = [(e.period, e.group) for e in ELEMENTS]
    assert len(positions) == len(set(positions))


def test_phase_is_one_of_the_known_values():
    for element in ELEMENTS:
        assert element.phase in {"solid", "liquid", "gas", "unknown"}


def test_known_element_chemistry_looks_right():
    hydrogen = ELEMENTS_BY_NUMBER[1]
    assert hydrogen.phase == "gas"

    iron = ELEMENTS_BY_NUMBER[26]
    assert iron.phase == "solid"
    assert iron.density is not None and iron.density > 0
    assert iron.electron_configuration.startswith("[Ar]")

    mercury = ELEMENTS_BY_NUMBER[80]
    assert mercury.phase == "liquid"
