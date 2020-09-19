import pytest
from mca.framework import data_types
from mca.blocks import real_imag
import numpy as np

test_cases = [(1+3j, (1, 3)),
              (np.array([1+1j, 1+2j]), (np.array([1, 1]), np.array([1, 2])))]


@pytest.mark.parametrize("test_input, expected_ordinate", test_cases)
def test_real_imag(test_input, expected_ordinate, test_output_block,
                   default_meta_data):
    a = real_imag.RealImag()
    b = test_output_block(
        data_types.Signal(default_meta_data, None, None, None, test_input))
    a.inputs[0].connect(b.outputs[0])
    assert np.array_equal(a.outputs[0].data.ordinate, expected_ordinate[0])
    assert np.array_equal(a.outputs[1].data.ordinate, expected_ordinate[1])
    assert default_meta_data == a.outputs[0].meta_data
    assert default_meta_data == a.outputs[1].meta_data
