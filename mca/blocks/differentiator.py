from mca.framework import validator, data_types, Block, parameters
from mca.language import _

import numpy as np


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

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        gradient = np.gradient(input_signal.ordinate) / input_signal.increment
        unit_a = input_signal.metadata.unit_a
        unit_o = input_signal.metadata.unit_o / input_signal.metadata.unit_a
        metadata = data_types.MetaData(None, unit_a=unit_a, unit_o=unit_o)
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(metadata),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=gradient,
        )
