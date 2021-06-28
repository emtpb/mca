import numpy as np

from mca.framework import validator, data_types, Block
from mca.language import _


class FFT(Block):
    """Calculates the FFT of the input signal.

    This block has one input and one output.
    """
    name = _("FFT")
    description = _("Computes the FFT of the input signal.")
    tags = (_("Processing"), _("Fourier"))

    def setup_io(self):
        self._new_output(
            meta_data=data_types.MetaData(
                "",
                unit_a="1/s",
                unit_o="V",
                quantity_a=_("Frequency"),
                quantity_o=_("Voltage"))
        )
        self._new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        ordinate = np.fft.fft(input_signal.ordinate)
        increment = 1 / (
                input_signal.increment * input_signal.values)
        values = input_signal.values
        meta_data = data_types.MetaData(
            name="",
            unit_a=1/input_signal.meta_data.unit_a,
            unit_o=input_signal.meta_data.unit_o
        )
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
