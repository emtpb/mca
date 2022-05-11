import numpy as np

from mca.framework import data_types, block_io
from mca.blocks import plot


abscissa = np.linspace(0, 19 * 0.1, 20)
ordinate = np.sin(abscissa)
sin_signal = data_types.Signal(data_types.MetaData("test", "s", "V", "Time",
                                                   "Voltage", "t", "U", ),
                               0, 20, 0.1,
                               ordinate)
abscissa_2 = np.linspace(0, 9 * 0.1, 10)
ordinate_2 = np.sin(abscissa_2)
sin_signal_2 = data_types.Signal(data_types.MetaData("test2", "s", "V", "Time",
                                                     "Voltage", "t", "U", ),
                                 0, 10, 0.1,
                                 ordinate_2)


def test_labels(test_output_block):
    a = test_output_block(sin_signal)
    b = plot.Plot()
    b.inputs[0].connect(a.outputs[0])
    assert b.fig.axes[0].get_xlabel() == "Time t / s"
    assert b.fig.axes[0].get_ylabel() == "Voltage U / V"
    c = test_output_block(sin_signal)
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    assert b.fig.axes[0].get_xlabel() == "Time t / s"
    assert b.fig.axes[0].get_ylabel() == "Voltage U / V"


def test_axes(test_output_block):
    b = plot.Plot()
    assert len(b.fig.axes) == 1


def test_lines(test_output_block):
    a = test_output_block(sin_signal)
    b = plot.Plot()
    c = test_output_block(sin_signal_2)
    b.inputs[0].connect(a.outputs[0])
    assert len(b.fig.axes[0].lines) == 1
    assert np.array_equal(b.fig.axes[0].lines[0].get_xdata(), abscissa)
    assert np.array_equal(b.fig.axes[0].lines[0].get_ydata(), ordinate)
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    assert len(b.fig.axes[0].lines) == 2
    assert np.array_equal(b.fig.axes[0].lines[1].get_xdata(), abscissa_2)
    assert np.array_equal(b.fig.axes[0].lines[1].get_ydata(), ordinate_2)


def test_legend(test_output_block):
    a = test_output_block(sin_signal)
    b = line_plot.Plot()
    c = test_output_block(sin_signal_2)
    b.inputs[0].connect(a.outputs[0])
    b.fig.axes[0].get_legend_handles_labels()[1][0] == sin_signal.metadata.name
    b.add_input(block_io.Input(b))
    b.inputs[1].connect(c.outputs[0])
    b.fig.axes[0].get_legend_handles_labels()[1][1] == sin_signal_2.metadata.name
