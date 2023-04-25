import pytest
from mca.framework import data_types
from mca.blocks import complex_to_real

import numpy as np

test_cases = [(1+3j, (1, 3)),
              (np.array([1+1j, 1+2j]), (np.array([1, 1]), np.array([1, 2])))]


@pytest.mark.parametrize("test_input, expected_ordinate", test_cases)
def test_complex_to_real(test_input, expected_ordinate, test_output_block,
                         default_metadata):
    a = complex_to_real.ComplexToReal()
    b = test_output_block(
        data_types.Signal(None, None, None, test_input))
    a.inputs[0].connect(b.outputs[0])
    assert np.array_equal(a.outputs[0].data.ordinate, expected_ordinate[0])
    assert np.array_equal(a.outputs[1].data.ordinate, expected_ordinate[1])
    assert default_metadata == a.outputs[0].metadata
    assert default_metadata == a.outputs[1].metadata
