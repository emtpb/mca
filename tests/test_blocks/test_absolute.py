import pytest
from mca.blocks import absolute
from mca.framework import data_types
import numpy as np


@pytest.mark.parametrize("test_input", [-5, 1, np.arange(-1, 10)])
def test_absolute(test_input, test_output_block, default_meta_data):
    a = absolute.Absolute()
    a.outputs[0].abscissa_meta_data = True
    a.outputs[0].ordinate_meta_data = True
    b = test_output_block(data_types.Signal(default_meta_data,
                                            None, None, None, test_input))
    a.inputs[0].connect(b.outputs[0])
    assert a.outputs[0].data.meta_data == default_meta_data
    if isinstance(test_input, int):
        assert a.outputs[0].data.ordinate >= 0
    if isinstance(test_input, np.ndarray):
        assert all(x >= 0 for x in a.outputs[0].data.ordinate)
