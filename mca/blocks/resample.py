from scipy.signal import resample

from mca.framework import Block, data_types, parameters, util


class Resample(Block):
    """Resamples the input signal."""
    name = "Resample"
    description = "Resamples the input signal."
    tags = ("Processing",)
    references = {"scipy.signal.resample":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["sample_freq"] = parameters.FloatParameter(
                name="Sampling frequency",
                min_=0, default=1, unit="Hz"
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        sample_freq = self.parameters["sample_freq"].value
        # Calculate the measure time
        measure_time = input_signal.increment * input_signal.values
        # Calculate the amount of values
        values = int(measure_time * sample_freq)
        # Calculate the ordinate
        ordinate = resample(input_signal.ordinate, values)
        # Calculate the increment
        increment = 1 / sample_freq
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
