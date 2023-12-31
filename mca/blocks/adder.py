import copy

import numpy as np

from mca.framework import DynamicBlock, data_types, util


class Adder(DynamicBlock):
    """Adds multiple signals to one new signal."""
    name = "Adder"
    description = "Adds multiple signals to one signal."
    tags = ("Processing",)

    def setup_io(self):
        self.dynamic_input = (1, None)
        self.new_output()
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    @util.validate_units(abscissa=True, ordinate=True)
    @util.validate_intervals
    def process(self):
        # Read the input data
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        # Fill the signals with zeros so their lengths match
        modified_signals = util.fill_zeros(signals)
        # Calculate the ordinate
        ordinate = np.zeros(modified_signals[0].values)
        for sgn in modified_signals:
            ordinate += sgn.ordinate
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=modified_signals[0].abscissa_start,
            values=modified_signals[0].values,
            increment=modified_signals[0].increment,
            ordinate=ordinate)
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
