import numpy as np

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class Normalization(Block):
    """Normalizes input signal by the specified range (By default -1 to 1)."""
    name = _("Normalization")
    description = _("Normalizes input signal by the specified range "
                    "(By default 0-1).")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["min"] = parameters.FloatParameter(
            name=_("Min"), default=0
        )
        self.parameters["max"] = parameters.FloatParameter(
            name=_("Max"), default=1
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        min_value = self.parameters["min"].value
        max_value = self.parameters["max"].value
        # Calculate the normalization range
        norm_range = abs(max_value - min_value)

        ordinate = input_signal.ordinate
        # Normalize between 0 and 1
        normed_ordinate = (ordinate - np.min(ordinate))/np.abs(np.min(ordinate)-np.max(ordinate))
        # Normalize between min and max
        normed_ordinate *= norm_range
        normed_ordinate += min_value
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=normed_ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
