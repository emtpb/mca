import pytest
import numpy as np

from mca.framework import data_types
from united import Unit

reference_signal = data_types.Signal(
        abscissa_start=0,
        values=10,
        increment=1,
        ordinate=np.arange(10))
test_cases_signal_unequal = [
    (reference_signal, None),
    (reference_signal, data_types.Signal(
        abscissa_start=0,
        values=9,
        increment=1,
        ordinate=np.arange(10))),
    (reference_signal, data_types.Signal(
        abscissa_start=0,
        values=10,
        increment=0.5,
        ordinate=np.arange(10))),
    (reference_signal, data_types.Signal(
        abscissa_start=0,
        values=10,
        increment=1,
        ordinate=np.arange(1, 11))),
    ]


@pytest.mark.parametrize("first_signal, second_signal", test_cases_signal_unequal)
def test_signal_unequal(first_signal, second_signal):
    assert first_signal != second_signal


def test_signal_equal():
    second_signal = data_types.Signal(
        abscissa_start=0,
        values=10,
        increment=1,
        ordinate=np.arange(10))
    assert reference_signal == second_signal


test_cases_string_to_unit = [
              ("V", Unit(["V"])), ("1/V", Unit([], ["V"])),
              ("s*V", Unit(["s", "V"])), ("1/(V*s)", Unit([], ["s", "V"])),
              ("(s*kg)/(A*cd)", Unit(["s", "kg"], ["A", "cd"])),
              ("V*A", Unit(["W"]))]


@pytest.mark.parametrize("test_string, expected_unit", test_cases_string_to_unit)
def test_string_to_unit(test_string, expected_unit):
    assert data_types.string_to_unit(test_string) == expected_unit


def test_metadata_to_axis_label():
    assert data_types.metadata_to_axis_label("V", "Voltage") == "Voltage in V"
    assert data_types.metadata_to_axis_label("V", "Voltage", "U") == "Voltage U / V"


test_cases_unit_setters = [("m/s", Unit(["m"], ["s"])),
                           (Unit(["V"]), Unit(["V"]))]


@pytest.mark.parametrize("unit_a, result", test_cases_unit_setters)
def test_unit_a_setters(unit_a, result):
    metadata = data_types.MetaData("test", Unit(["s"]), Unit(["I"]))
    metadata.unit_a = unit_a
    assert metadata.unit_a == result


@pytest.mark.parametrize("unit_o, result", test_cases_unit_setters)
def test_unit_o_setters(unit_o, result):
    metadata = data_types.MetaData("test", Unit(["s"]), Unit(["I"]))
    metadata.unit_o = unit_o
    assert metadata.unit_o == result


reference_metadata = data_types.MetaData("Test", Unit(["s"]), Unit(["V"]),
                                          "Time", "Voltage", "t", "U")

test_cases_metadata_unequal = [
    (reference_metadata, None),
    (reference_metadata, data_types.MetaData("Test1", Unit(["m"]), Unit(["V"]),
                                              "Time", "Voltage", "t", "U")),
    (reference_metadata, data_types.MetaData("Test2", Unit(["s"]), Unit(["A"]),
                                              "Time", "Voltage", "t", "U")),
    (reference_metadata, data_types.MetaData("Test3", Unit(["s"]), Unit(["V"]),
                                              "Length", "Voltage", "t", "U")),
    (reference_metadata, data_types.MetaData("Test4", Unit(["s"]), Unit(["V"]),
                                              "Time", "Current", "t", "U")),
    (reference_metadata, data_types.MetaData("Test5", Unit(["s"]), Unit(["V"]),
                                              "Time", "Voltage", "l", "U")),
    (reference_metadata, data_types.MetaData("Test6", Unit(["s"]), Unit(["V"]),
                                              "Time", "Voltage", "t", "I")),
]


@pytest.mark.parametrize(
    "first_meta_object, second_meta_object",
    test_cases_metadata_unequal)
def test_metadata_unequal(first_meta_object, second_meta_object):
    assert first_meta_object != second_meta_object
