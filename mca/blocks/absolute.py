from mca.framework import Block, data_types, util


class Absolute(Block):
    """Computes the absolute of the input signal."""
    name = "Absolute"
    description = "Computes the absolute of the input signal."
    tags = ("Processing",)

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
        ordinate = abs(input_signal.ordinate)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
