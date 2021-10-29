import pytest
from mca.blocks import adder
from mca.framework import data_types
import numpy as np

test_metadata = data_types.MetaData("", "s", "V")
test_signal0 = data_types.Signal(test_metadata, 0, 5, 0.1, np.full((5,), 1))
test_signal1 = data_types.Signal(test_metadata, -2, 10, 0.1, np.full((10,), 1))
test_signal2 = data_types.Signal(test_metadata, -1, 15, 0.1, np.full((15,), 1))

expected_ordinate0 = np.full((25,), 1)
expected_ordinate0[10:20] = np.zeros(10)
expected_signal0 = data_types.Signal(test_metadata, -2, 25, 0.1, expected_ordinate0)

expected_ordinate1 = np.full((15,), 1)
expected_ordinate1[10:15] = np.full((5,), 2)
expected_signal1 = data_types.Signal(test_metadata, -1, 15, 0.1, expected_ordinate1)
test_cases = [((test_signal0, test_signal1), expected_signal0),
              ((test_signal0, test_signal2), expected_signal1)]


@pytest.mark.parametrize("test_input, expected_signal", test_cases)
def test_adder(test_input, expected_signal, test_output_block):
    a = adder.Adder()
    b = test_output_block(test_input[0])
    a.inputs[0].connect(b.outputs[0])
    c = test_output_block(test_input[1])
    a.inputs[1].connect(c.outputs[0])
    if test_input[1] == test_signal1:
        assert a.outputs[0].data == expected_signal
    if test_input[1] == test_signal2:
        assert a.outputs[0].data == expected_signal
