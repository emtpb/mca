import numpy as np
import pytest

from mca.framework import block_base, data_types


class TestOutputBlock(block_base.Block):
    name = "TestOutputBlock"

    def __init__(self, sig):
        super().__init__()
        self._new_output(meta_data=None)
        self.outputs[0].data = sig

    def _process(self):
        pass


@pytest.fixture(scope="module")
def test_output_block():
    return TestOutputBlock


@pytest.fixture(scope="module")
def sin_signal():
    return data_types.Signal(data_types.MetaData("test", "Time", "t", "s", "Voltage", "U", "V"), 0, 628, 0.01,
                             np.sin(2*np.pi*np.linspace(0, 0.01*627, 628)))


@pytest.fixture(scope="module")
def sin_block(sin_signal):
    return TestOutputBlock(sin_signal)


@pytest.fixture(scope="module")
def unit_step_signal():
    return data_types.Signal(None, -1, 200, 0.01,
                             np.where(np.arange(-1, 1, 0.01) >= 0, 1, 0))


@pytest.fixture(scope="module")
def unit_step_block(unit_step_signal):
    return TestOutputBlock(unit_step_signal)
