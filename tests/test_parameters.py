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
    a = pm.ChoiceParameter("Test", choices=[(1.2, "1.2"), ("a", "all"), (42, "42")], value=1.2)
    with pytest.raises(exceptions.ParameterValueError):
        a.validate("test")
    a.validate(42)
    a.validate("a")


"""Test for BoolParameter validation method."""


def test_type_bool():
    a = pm.BoolParameter("Test", value=True)
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate("test")
    a.validate(True)


"""Test for PathParameter validation method."""


def test_type_path():
    a = pm.PathParameter("Test", value="test")
    with pytest.raises(exceptions.ParameterTypeError):
        a.validate(5)
    a.validate("test")


def test_file_format():
    a = pm.PathParameter("Test", value="test.json", file_formats=[".json", ".txt"])
    with pytest.raises(exceptions.ParameterValueError):
        a.validate("test.png")
    a.validate("test.json")


def test_parameter_conversion_1():
    a = pm.FloatParameter("dt", value=0.01, min_=0)
    b = pm.FloatParameter("fabt", value=100, min_=0)

    def conversion_func():
        b.value = 1/a.value
    conversion = pm.ParameterConversion([a], [b], conversion_func)
    a.value = 0.001
    conversion.conversion_func()
    assert b.value == 1000


def test_parameter_conversion_2():
    a = pm.FloatParameter("dt", value=0.01, min_=0)
    b = pm.FloatParameter("fabt", value=100, min_=0)
    c = pm.IntParameter("values", value=200, min_=0)
    d = pm.FloatParameter("t_mess", value=2.0, min_=0)

    def conversion_func():
        b.value = 1/a.value
        d.value = a.value*c.value
    conversion = pm.ParameterConversion([a, c], [b, d], conversion_func)
    a.value = 0.001
    conversion.conversion_func()
    assert b.value == 1000
    assert d.value == 0.2


def test_parameter_block_1():
    a = pm.FloatParameter("dt", value=0.01, min_=0)
    b = pm.FloatParameter("fabt", value=100, min_=0)

    def dt_to_fabt():
        b.value = 1/a.value

    def fabt_to_dt():
        a.value = 1/b.value

    conversion = pm.ParameterConversion([a], [b], dt_to_fabt)
    conversion_1 = pm.ParameterConversion([b], [a], fabt_to_dt)
    c = pm.ParameterBlock([a, b], [conversion, conversion_1], 0)
    assert c.parameters == [a]
    c.conversion_index = 1
    assert c.parameters == [b]
    c.conversion_index = 0
    a.value = 0.1
    assert b.value == 10
    c.conversion_index = 1
    b.value = 1000
    assert a.value == 0.001


def test_parameter_block_2():
    a = pm.FloatParameter("dt", value=0.01, min_=0)
    b = pm.FloatParameter("fabt", value=100, min_=0)
    c = pm.IntParameter("values", value=200, min_=0)
    d = pm.FloatParameter("t_mess", value=2.0, min_=0)

    def dt_to_fabt():
        b.value = 1/a.value

    def fabt_to_dt():
        a.value = 1/b.value

    def dt_values_to_tmess():
        d.value = a.value*c.value
        dt_to_fabt()

    def fabt_values_to_tmess():
        d.value = c.value/b.value
        fabt_to_dt()

    def tmess_values_to_dt():
        a.value = d.value/c.value
        dt_to_fabt()

    def tmess_dt_to_values():
        c.value = d.value/a.value
        dt_to_fabt()

    def tmess_fabt_to_values():
        c.value = d.value*b.value

        fabt_to_dt()

    conversion = pm.ParameterConversion(
        [a, c], [b, d], dt_values_to_tmess
    )
    conversion_1 = pm.ParameterConversion(
        [b, c], [a, d], fabt_values_to_tmess)
    conversion_2 = pm.ParameterConversion([c, d], [a, c], tmess_values_to_dt)
    conversion_3 = pm.ParameterConversion([a, d], [b, c], tmess_dt_to_values)
    conversion_4 = pm.ParameterConversion([b, d], [a, c], tmess_fabt_to_values)
    e = pm.ParameterBlock([a, b, c, d], [conversion, conversion_1,
                                         conversion_2, conversion_3,
                                         conversion_4], 0)
    assert e.parameters == [a, c]
    a.value = 0.1
    assert b.value == 10
    assert d.value == 20
    e.conversion_index = 4
    assert e.parameters == [b, d]
    b.value = 1000
    assert a.value == 0.001
    assert c.value == 20000
    e.conversion_index = 3
    with pytest.raises(exceptions.ParameterTypeError):
        a.value = 3
