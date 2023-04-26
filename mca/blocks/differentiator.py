import numpy as np

from mca.framework import data_types, util, Block
from mca.language import _


class Differentiator(Block):
    """Computes the gradient of the input signal."""
    name = _("Differentiator")
    description = _("Computes the gradient of the input signal.")
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
        gradient = np.gradient(input_signal.ordinate) / input_signal.increment

        unit_a = self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o / self.inputs[0].metadata.unit_a
        metadata = data_types.MetaData(None, unit_a=unit_a, unit_o=unit_o)

        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=gradient,
        )
        self.outputs[0].external_metadata = metadata
