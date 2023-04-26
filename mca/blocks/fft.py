import numpy as np

from mca.framework import data_types, Block, parameters, util
from mca.language import _


class FFT(Block):
    """Computes the FFT of the input signal."""
    name = _("FFT")
    description = _("Computes the FFT of the input signal.")
    tags = (_("Processing"), _("Fouriertransformation"))

    def setup_io(self):
        self.new_output(
            metadata=data_types.MetaData(
                "",
                unit_a="1/s",
                unit_o="V",
                quantity_a=_("Frequency"), )
        )
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({"normalize": parameters.BoolParameter(
            _("Normalize"), default=False)})

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        normalize = self.parameters["normalize"].value
        input_signal = self.inputs[0].data

        unit_o = self.inputs[0].metadata.unit_o
        unit_a = 1 / self.inputs[0].metadata.unit_a
        metadata = data_types.MetaData(None, unit_a=unit_a, unit_o=unit_o)

        ordinate = np.fft.fft(input_signal.ordinate)
        increment = 1 / (
                input_signal.increment * input_signal.values)
        values = input_signal.values

        if normalize:
            ordinate = ordinate / values

        self.outputs[0].data = data_types.Signal(
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = metadata
