import pytest
from mca.block import adder
from mca.base import block_base
from mca.datatypes import signal
import numpy as np


class TestBlock(block_base.Block):
    def __init__(self, sig):
        super().__init__()
        self._new_output(meta_data=None)
        self.outputs[0].data = sig

    def _process(self):
        pass


test_signal0 = signal.Signal(None, 0, 5, 0.1, np.full((5,), 1))
test_signal1 = signal.Signal(None, -2, 10, 0.1, np.full((10,), 1))
test_signal2 = signal.Signal(None, -1, 15, 0.1, np.full((15,), 1))

expected_ordinate0 = np.full((25,), 1)
expected_ordinate0[10:20] = np.zeros(10)
expected_signal0 = signal.Signal(None, -2, 25, 0.1, expected_ordinate0)

expected_ordinate1 = np.full((15,), 1)
expected_ordinate1[10:15] = np.full((5,), 2)
expected_signal1 = signal.Signal(None, -1, 15, 0.1, expected_ordinate1)
test_cases = [((test_signal0, test_signal1), expected_signal0),
              ((test_signal0, test_signal2), expected_signal1)]


@pytest.mark.parametrize("test_input, expected", test_cases)
def test_adder_basic(test_input, expected):
    a = adder.Adder()
    b = TestBlock(test_input[0])
    a.inputs[0].connect(b.outputs[0])
    c = TestBlock(test_input[1])
    a.inputs[1].connect(c.outputs[0])
    if test_input[1] == test_signal1:
        assert a.outputs[0].data == expected
    if test_input[1] == test_signal2:
        assert a.outputs[0].data == expected
