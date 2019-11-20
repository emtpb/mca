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


sin_signal = signal.Signal(None, 0, 628, 0.01,
                           np.sin(np.arange(0, 6.28, 0.01)))
SinBlock = TestBlock(sin_signal)
unit_step_signal = signal.Signal(None, -1, 200, 0.01,
                                 np.where(np.arange(-1, 1, 0.01) >= 0, 1, 0))
UnitStepBlock = TestBlock(unit_step_signal)
