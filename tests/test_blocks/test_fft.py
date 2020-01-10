from mca.blocks import fft
from mca.framework import data_types
import numpy as np
import test_data


def test_fft():
    a = fft.FFT()
    a.inputs[0].connect(test_data.sin_block.outputs[0])
    sin = test_data.sin_block.outputs[0].data
    expected_ordinate = np.fft.fft(sin.ordinate)
    increment = 1 / (sin.increment * sin.values) * 2 * np.pi
    values = sin.values
    expected_signal = data_types.Signal(None, 0, values,
                                        increment, expected_ordinate)
    assert a.outputs[0].data == expected_signal
