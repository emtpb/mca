import pytest
from mca.framework import data_types, block_io, block_registry
from mca.blocks import signal_plot
import numpy as np
import test_data

abscissa = np.linspace(0, 19 * 0.1, 20)
ordinate = np.sin(abscissa)
sin_signal = data_types.Signal(data_types.MetaData("test", "Time", "t", "s", "Voltage", "U", "V"), 0, 20, 0.1,
                               ordinate)
abscissa_2 = np.linspace(0, 9 * 0.1, 10)
ordinate_2 = np.sin(abscissa_2)
sin_signal_2 = data_types.Signal(data_types.MetaData("test_2", "Time", "t", "s", "Voltage", "U", "V"), 0, 10, 0.1,
                                 ordinate_2)


def test_labels():
    a = test_data.TestBlock(sin_signal)
    b = signal_plot.SignalPlot()
    b.inputs[0].connect(a.outputs[0])
    assert b.fig.axes[0].get_xlabel() == "Time t / s"
    assert b.fig.axes[0].get_ylabel() == "Voltage U / V"
    c = test_data.TestBlock(sin_signal)
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    assert b.fig.axes[0].get_xlabel() == ""
    assert b.fig.axes[0].get_ylabel() == ""


def test_axes():
    a = test_data.TestBlock(sin_signal)
    b = signal_plot.SignalPlot()
    c = test_data.TestBlock(sin_signal)
    assert len(b.fig.axes) == 0
    b.inputs[0].connect(a.outputs[0])
    assert len(b.fig.axes) == 1
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    assert len(b.fig.axes) == 1


def test_lines():
    a = test_data.TestBlock(sin_signal)
    b = signal_plot.SignalPlot()
    c = test_data.TestBlock(sin_signal_2)
    b.inputs[0].connect(a.outputs[0])
    assert len(b.fig.axes[0].lines) == 1
    assert np.array_equal(b.fig.axes[0].lines[0].get_xdata(), abscissa)
    assert np.array_equal(b.fig.axes[0].lines[0].get_ydata(), ordinate)
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    assert len(b.fig.axes[0].lines) == 2
    assert np.array_equal(b.fig.axes[0].lines[1].get_xdata(), abscissa_2)
    assert np.array_equal(b.fig.axes[0].lines[1].get_ydata(), ordinate_2)


def test_legend():
    a = test_data.TestBlock(sin_signal)
    b = signal_plot.SignalPlot()
    c = test_data.TestBlock(sin_signal_2)
    b.inputs[0].connect(a.outputs[0])
    b.fig.axes[0].get_legend_handles_labels()[1][0] == sin_signal.meta_data.name
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    b.fig.axes[0].get_legend_handles_labels()[1][1] == sin_signal_2.meta_data.name
