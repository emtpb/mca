from scipy.signal import resample

from mca.framework import data_types, Block, util, parameters
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
        self.parameters.update({
            "sample_freq": parameters.FloatParameter(
                name=_("Sampling frequency"),
                min_=0, default=1, unit="Hz")
        })

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        input_signal = self.inputs[0].data
        sample_freq = self.parameters["sample_freq"].value

        measure_time = input_signal.increment * input_signal.values
        new_values = int(measure_time * sample_freq)
        ordinate = resample(input_signal.ordinate, new_values)
        new_increment = 1 / sample_freq
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=new_values,
            increment=new_increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = self.inputs[0].metadata
