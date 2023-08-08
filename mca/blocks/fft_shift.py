import numpy as np

from mca.framework import Block, data_types, parameters, util


class FFTShift(Block):
    """Perform an FFT shift or the inverse FFT shift on the input signal."""
    name = "FFT Shift"
    description = "Perform an FFT shift on the input signal."
    tags = ("Processing", "Fouriertransformation")

    def setup_io(self):
        self.new_output(
            metadata=data_types.MetaData(
                name="", unit_a="1/s", unit_o="V", quantity_a="Frequency",)
        )
        self.new_input()

    def setup_parameters(self):
        self.parameters["inverse"] = parameters.BoolParameter(
            name="Inverse", default=False
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        inverse = self.parameters["inverse"].value
        # Calculate the ordinate
        if not inverse:
            shifted = np.fft.fftshift(input_signal.ordinate)
        else:
            shifted = np.fft.ifftshift(input_signal.ordinate)
        # Calculate the increment
        increment = 1 / (
                input_signal.increment * input_signal.values)
        # Calculate the amount of values
        values = input_signal.values
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=shifted,
        )
        # Calculate units for abscissa and ordinate
        unit_o = self.inputs[0].metadata.unit_o
        unit_a = self.inputs[0].metadata.unit_a
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )
