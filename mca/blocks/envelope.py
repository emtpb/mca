import numpy as np
from scipy.signal import hilbert

from mca.framework import data_types, util, Block
from mca.language import _


class Envelope(Block):
    """Computes the envelope of the input signal."""
    name = _("Envelope")
    description = _("Computes the envelope of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        input_signal = self.inputs[0].data
        analytical_signal = hilbert(input_signal.ordinate)
        envelope = np.abs(analytical_signal)
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=envelope,
        )
        self.outputs[0].external_metadata = self.inputs[0].metadata
