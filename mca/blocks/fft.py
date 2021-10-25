import numpy as np

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class FFT(Block):
    """Computes the FFT of the input signal."""
    name = _("FFT")
    description = _("Computes the FFT of the input signal.")
    tags = (_("Processing"), _("Fourier"))

    def setup_io(self):
        self._new_output(
            meta_data=data_types.MetaData(
                "",
                unit_a="1/s",
                unit_o="V*s",
                quantity_a=_("Frequency"),)
        )
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({"normalize": parameters.BoolParameter(
            _("Normalize"), default=False)})

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

        normalize = self.parameters["normalize"].value
        input_signal = self.inputs[0].data

        ordinate = np.fft.fft(input_signal.ordinate)
        increment = 1 / (
                input_signal.increment * input_signal.values)
        values = input_signal.values

        if normalize:
            ordinate = ordinate/values
            unit_o = input_signal.meta_data.unit_o
        else:
            unit_o = input_signal.meta_data.unit_a * input_signal.meta_data.unit_o
        meta_data = data_types.MetaData(
            name="",
            unit_a=1/input_signal.meta_data.unit_a,
            unit_o=unit_o
        )

        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
