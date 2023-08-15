import numpy as np

from mca.framework import Block, data_types, parameters, util


class FFTShift(Block):
    """Perform an FFT shift or the inverse FFT shift on the input signal."""
    name = "FFT Shift"
    description = "Perform an FFT shift on the input signal."
    tags = ("Processing", "Fouriertransformation")
    references = {"numpy.fft.fftshift":
        "https://numpy.org/doc/1.25/reference/generated/numpy.fft.fftshift.html",
        "numpy.fft.ifftshift":
        "https://numpy.org/doc/1.25/reference/generated/numpy.fft.ifftshift.html"}

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
        # Calculate the increment
        increment = input_signal.increment
        # Calculate the amount of values
        values = input_signal.values

        if not inverse:
            shifted = np.fft.fftshift(input_signal.ordinate)
            abscissa_start = -input_signal.increment*input_signal.values / 2
        else:
            shifted = np.fft.ifftshift(input_signal.ordinate)
            abscissa_start = 0

        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
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
