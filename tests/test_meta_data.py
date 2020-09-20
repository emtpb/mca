import pytest
from mca.framework import data_types
from united import Unit

test_cases_string_to_unit = [
              ("V", Unit(["V"])), ("1/V", Unit([], ["V"])),
              ("s*V", Unit(["s", "V"])), ("1/(V*s)", Unit([], ["s", "V"])),
              ("(s*kg)/(A*cd)", Unit(["s", "kg"], ["A", "cd"])),
              ("V*A", Unit(["W"]))]


@pytest.mark.parametrize("test_string, expected_unit", test_cases_string_to_unit)
def test_string_to_unit(test_string, expected_unit):
    assert data_types.string_to_unit(test_string) == expected_unit


def test_meta_data_to_axis_label():
    assert data_types.meta_data_to_axis_label("Voltage", "V") == "Voltage in V"
    assert data_types.meta_data_to_axis_label("Voltage", "V", "U") == "Voltage U / V"
