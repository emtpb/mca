import numpy as np

from mca.framework import Block, data_types, util


class Differentiator(Block):
    """Computes the gradient of the input signal."""
    name = "Differentiator"
    description = "Computes the gradient of the input signal."
    tags = ("Processing",)
    references = {"numpy.gradient":
        "https://numpy.org/doc/stable/reference/generated/numpy.gradient.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Calculate the ordinate
        gradient = np.gradient(input_signal.ordinate) / input_signal.increment
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=gradient,
        )
        # Calculate units for abscissa and ordinate
        unit_a = self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o / self.inputs[0].metadata.unit_a
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )
