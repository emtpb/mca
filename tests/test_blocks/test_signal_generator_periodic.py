import pytest
import numpy as np
from scipy import signal as sgn

from mca.blocks import signal_generator_periodic
from mca.framework import data_types


def test_function():
    a = signal_generator_periodic.SignalGenerator(function="sin")
    a.apply_parameter_changes()
    sin_signal = data_types.Signal(None,
                                   a.parameters["start_a"].value,
                                   a.parameters["values"].value,
                                   a.parameters["increment"].value,
                                   np.sin(2*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                       a.parameters["values"].value)))
    assert a.outputs[0].data == sin_signal
    a.parameters["function"].value = "rect"
    a.apply_parameter_changes()
    rect_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    np.sign(np.sin(2*np.pi*np.linspace(
                                        a.parameters["start_a"].value,
                                        (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                        a.parameters["values"].value))))
    assert a.outputs[0].data == rect_signal
    a.parameters["function"].value = "tri"
    a.apply_parameter_changes()
    triangle_signal = data_types.Signal(None,
                                        a.parameters["start_a"].value,
                                        a.parameters["values"].value,
                                        a.parameters["increment"].value,
                                        sgn.sawtooth(2*np.pi*np.linspace(
                                            a.parameters["start_a"].value,
                                            (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                            a.parameters["values"].value) + np.pi / 2, 0.5))
    assert a.outputs[0].data == triangle_signal


@pytest.mark.parametrize("test_input", [-5, 2])
def test_frequency(test_input):
    a = signal_generator_periodic.SignalGenerator(freq=test_input)
    a.apply_parameter_changes()
    test_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    np.sin(2*test_input*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                       a.parameters["values"].value)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [-5, 2])
def test_amp(test_input):
    a = signal_generator_periodic.SignalGenerator(amp=test_input)
    a.apply_parameter_changes()
    test_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    test_input*np.sin(2*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                       a.parameters["values"].value)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [np.pi, 1, -np.pi/2])
def test_phase(test_input):
    a = signal_generator_periodic.SignalGenerator(phase=test_input)
    a.apply_parameter_changes()
    test_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    np.sin(2*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                       a.parameters["values"].value)-test_input))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [-0.5, 2, 4.23])
def test_start_a(test_input):
    a = signal_generator_periodic.SignalGenerator(start_a=test_input)
    a.apply_parameter_changes()
    test_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    np.sin(2*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       a.parameters["start_a"].value + (a.parameters["values"].value-1) *
                                       a.parameters["increment"].value,
                                       a.parameters["values"].value)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [30, 90, 1746])
def test_values(test_input):
    a = signal_generator_periodic.SignalGenerator(values=test_input)
    a.apply_parameter_changes()
    test_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    np.sin(2*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                       a.parameters["values"].value)))
    assert a.outputs[0].data == test_signal


@pytest.mark.parametrize("test_input", [1, 0.03, 0.05])
def test_increment(test_input):
    a = signal_generator_periodic.SignalGenerator(increment=test_input)
    a.apply_parameter_changes()
    test_signal = data_types.Signal(None,
                                    a.parameters["start_a"].value,
                                    a.parameters["values"].value,
                                    a.parameters["increment"].value,
                                    np.sin(2*np.pi*np.linspace(
                                       a.parameters["start_a"].value,
                                       (a.parameters["values"].value-1)*a.parameters["increment"].value,
                                       a.parameters["values"].value)))
    assert a.outputs[0].data == test_signal