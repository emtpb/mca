import numpy as np

from mca.framework import Block, data_types, parameters, util


class FFT(Block):
    """Computes the FFT or the inverse FFT of the input signal."""
    name = "FFT"
    description = "Computes the FFT or the inverse FFT of the input signal."
    tags = ("Processing", "Fourier transform")
    references = {"numpy.fft.fft":
        "https://numpy.org/doc/1.25/reference/generated/numpy.fft.fft.html",
        "numpy.fft.ifft":
        "https://numpy.org/doc/1.25/reference/generated/numpy.fft.ifft.html"}

    def setup_io(self):
        self.new_output(
            metadata=data_types.MetaData(
                name="", unit_a="1/s", unit_o="V", quantity_a="Frequency",)
        )
        self.new_input()

    def setup_parameters(self):
        self.parameters["normalize"] = parameters.BoolParameter(
            name="Normalize", default=False,
            description="Normalize the FFT by dividing with the total amount "
                        "of values"
        )
        self.parameters["inverse"] = parameters.BoolParameter(
            name="Inverse", default=False,
            description="Compute the inverse FFT"
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        normalize = self.parameters["normalize"].value
        inverse = self.parameters["inverse"].value
        # Calculate the ordinate
        if not inverse:
            fft = np.fft.fft(input_signal.ordinate)
        else:
            fft = np.fft.ifft(input_signal.ordinate)
        # Calculate the increment
        increment = 1 / (
                input_signal.increment * input_signal.values)
        # Calculate the amount of values
        values = input_signal.values
        # Normalize the fft if needed
        if normalize:
            fft = fft / values
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=fft,
        )
        # Calculate units for abscissa and ordinate
        unit_o = self.inputs[0].metadata.unit_o
        unit_a = 1 / self.inputs[0].metadata.unit_a
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )
