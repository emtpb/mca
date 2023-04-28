from scipy.signal import resample

from mca.framework import Block, data_types, parameters,  util
from mca.language import _


class Resample(Block):
    """Resamples the input signal."""
    name = _("Resample")
    description = _("Resamples the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["sample_freq"] = parameters.FloatParameter(
                name=_("Sampling frequency"),
                min_=0, default=1, unit="Hz"
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
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
