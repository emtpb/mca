from mca.framework import validator, data_types, Block, parameters
from mca.language import _

from scipy.signal import resample


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

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        sample_freq = self.parameters["sample_freq"].value

        measure_time = input_signal.increment*input_signal.values
        new_values = int(measure_time*sample_freq)
        ordinate = resample(input_signal.ordinate, new_values)
        new_increment = 1 / sample_freq
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(input_signal.metadata),
            abscissa_start=input_signal.abscissa_start,
            values=new_values,
            increment=new_increment,
            ordinate=ordinate,
        )
