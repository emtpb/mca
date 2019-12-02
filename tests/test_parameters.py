"""Tests concerning the validation of methods of parameters classes of
the mca."""


import pytest
from mca.framework import parameters as pm
from mca import exceptions

"""Test for the FloatParameter validation method."""


@pytest.mark.parametrize("test_input", ["a", [1, 2]])
def test_type_float(test_input):
    a = pm.FloatParameter("Test", value=42.2)
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate(test_input)
    a.validate(42)
    a.validate(42.1)


def test_bounds_float():
    a = pm.FloatParameter("Test", max_=4.5, min_=2.25)
    with pytest.raises(exceptions.OutOfBoundError):
        a.validate(4.51)
    with pytest.raises(exceptions.OutOfBoundError):
        a.validate(2.24)
    a.validate(4.2)


"""Test for the IntParameter validation method."""


def test_type_int():
    a = pm.IntParameter("Test", value=42)
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate("a")


def test_bounds_int():
    a = pm.IntParameter("Test", max_=4, min_=2)
    with pytest.raises(exceptions.OutOfBoundError):
        a.validate(5)
    with pytest.raises(exceptions.OutOfBoundError):
        a.validate(1)
    a.validate(4)


"""Test for the StrParameter validation method."""


def test_type_str():
    a = pm.StrParameter("Test", value="test")
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate(5.1)


def test_bounds_str():
    a = pm.StrParameter("Test", max_length=3)
    with pytest.raises(exceptions.OutOfBoundError):
        a.validate("test")
    a.validate("t")


"""Test for the ChoiceParameter validation method."""


def test_choice():
    a = pm.ChoiceParameter("Test", choices=[1.2, "a", 42], value=1.2)
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate("test")
    a.validate(42)
    a.validate("a")


"""Test for BoolParameter validation method."""


def test_type_bool():
    a = pm.BoolParameter("Test", value=True)
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate("test")
    a.validate(True)
