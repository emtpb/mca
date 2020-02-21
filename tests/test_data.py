from mca.framework import block_base, data_types
import numpy as np


class TestBlock(block_base.Block):
    def __init__(self, sig):
        super().__init__()
        self._new_output(meta_data=None)
        self.outputs[0].data = sig

    def _process(self):
        pass


sin_signal = data_types.Signal(data_types.MetaData("test", "Time", "t", "s", "Voltage", "U", "V"), 0, 628, 0.01,
                               np.sin(2*np.pi*np.linspace(0, 0.01*627, 628)))
sin_block = TestBlock(sin_signal)
unit_step_signal = data_types.Signal(None, -1, 200, 0.01,
                                     np.where(np.arange(-1, 1, 0.01) >= 0, 1, 0))
unit_step_block = TestBlock(unit_step_signal)
