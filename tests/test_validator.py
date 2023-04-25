import pytest
from united import Unit

from mca import exceptions
from mca.framework import validator
from mca.framework import data_types


def test_check_signals():
    validator.check_type_signal(data_types.Signal(None, None, None, None))
    with pytest.raises(exceptions.DataTypeError):
        validator.check_type_signal(5)


def test_check_intervals():
    a = data_types.Signal(0, 10, 0.1, None)
    b = data_types.Signal(1, 5, 0.1, None)
    c = data_types.Signal(0.01, 5, 0.1, None)
    d = data_types.Signal(0, 10, 0.05, None)
    validator.check_intervals([a, b])
    with pytest.raises(exceptions.IntervalError):
        validator.check_intervals([a, c])
    with pytest.raises(exceptions.IntervalError):
        validator.check_intervals([a, d])


def test_check_units():
    a = Unit(["V"])
    b = Unit(["I"])
    c = Unit(["kg", "m", "m"], ["A", "s", "s", "s"])
    with pytest.raises(exceptions.UnitError):
        validator.check_same_units([a, b])
    with pytest.raises(exceptions.UnitError):
        validator.check_same_units([a, b, c])
    validator.check_same_units([a, c])
