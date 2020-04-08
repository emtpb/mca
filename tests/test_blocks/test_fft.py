from mca.blocks import fft
from mca.framework import data_types
import numpy as np


def test_fft(sin_block):
    a = fft.FFT()
    a.inputs[0].connect(sin_block.outputs[0])
    sin = sin_block.outputs[0].data
    expected_ordinate = np.fft.fft(sin.ordinate)
    increment = 1 / (sin.increment * sin.values)
    values = sin.values
    expected_signal = data_types.Signal(None, 0, values,
                                        increment, expected_ordinate)
    assert a.outputs[0].data == expected_signal
