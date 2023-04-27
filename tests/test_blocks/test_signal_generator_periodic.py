import pytest
import numpy as np
from scipy import signal as sgn

from mca.blocks import signal_generator_periodic
from mca.framework import data_types


def test_function():
    a = signal_generator_periodic.SignalGeneratorPeriodic(function="sin")
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    sin_signal = data_types.Signal(start, values, increment,
                                   np.sin(2 * np.pi * np.linspace(
                                       start, start + (values - 1) * increment,
                                       values)))
    assert a.outputs[0].data == sin_signal
    a.parameters["signal_type"].value = "rect"
    a.trigger_update()
    rect_signal = data_types.Signal(start, values, increment,
                                    np.sign(np.sin(2 * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values))))
    assert a.outputs[0].data == rect_signal
    a.parameters["signal_type"].value = "tri"
    a.trigger_update()
    triangle_signal = data_types.Signal(start, values, increment,
                                        sgn.sawtooth(2 * np.pi * np.linspace(
                                            start, start + (values - 1) * increment,
                                            values) + np.pi / 2, 0.5))
    assert a.outputs[0].data == triangle_signal


@pytest.mark.parametrize("test_input", [0.1, 2])
def test_frequency(test_input):
    a = signal_generator_periodic.SignalGeneratorPeriodic(freq=test_input)
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    test_signal = data_types.Signal(start, values, increment,
                                    np.sin(2 * test_input * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [0.1, 2])
def test_amp(test_input):
    a = signal_generator_periodic.SignalGeneratorPeriodic(amp=test_input)
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    test_signal = data_types.Signal(start, values, increment,
                                    test_input * np.sin(2 * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [np.pi, 1, -np.pi / 2])
def test_phase(test_input):
    a = signal_generator_periodic.SignalGeneratorPeriodic(phase=test_input)
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    test_signal = data_types.Signal(start, values, increment,
                                    np.sin(2 * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values)-test_input))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [-0.5, 2, 4.23])
def test_start(test_input):
    a = signal_generator_periodic.SignalGeneratorPeriodic(abscissa={"start":test_input})
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    test_signal = data_types.Signal(start, values, increment,
                                    np.sin(2 * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values)))
    print(np.allclose(test_signal.ordinate, a.outputs[0].data.ordinate))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [30, 90, 1746])
def test_values(test_input):
    a = signal_generator_periodic.SignalGeneratorPeriodic(abscissa={"values":test_input})
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    test_signal = data_types.Signal(start, values, increment,
                                    np.sin(2 * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [1, 0.03, 0.05])
def test_increment(test_input):
    a = signal_generator_periodic.SignalGeneratorPeriodic(abscissa={"increment":test_input})
    a.trigger_update()
    start = a.parameters["abscissa"].parameters["start"].value
    values = a.parameters["abscissa"].parameters["values"].value
    increment = a.parameters["abscissa"].parameters["increment"].value
    test_signal = data_types.Signal(start, values, increment,
                                    np.sin(2 * np.pi * np.linspace(
                                        start, start + (values - 1) * increment,
                                        values)))
    assert a.outputs[0].data == test_signal
