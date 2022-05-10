import numpy as np

from mca.framework import validator, data_types, Block
from mca.language import _


class PowerSpectrum(Block):
    """Computes the power spectrum of the input signal."""
    name = _("PowerSpectrum")
    description = _("Computes the power spectrum of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(metadata=data_types.MetaData(
                "",
                unit_a="1/s",
                unit_o="V*V",
                quantity_a=_("Frequency")
        ))
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        ccf = np.correlate(input_signal.ordinate, input_signal.ordinate,
                           mode="full")
        psd = np.fft.fft(ccf)
        abscissa_start = 0
        values = input_signal.values*2-1
        increment = 1 / (
                input_signal.increment * values)
        unit_o = input_signal.metadata.unit_o**2
        unit_a = 1/input_signal.metadata.unit_a
        metadata = data_types.MetaData(None, unit_a, unit_o)
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(metadata),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=psd,
        )
