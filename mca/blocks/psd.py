from mca.framework import validator, data_types, Block
from mca.language import _

import numpy as np
from copy import deepcopy


class PowerDensitySpectrum(Block):
    """Computes the auto correlation of the input signal."""
    name = _("PowerDensitySpectrum")
    description = _("Calculates the power density spectrum of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(meta_data=data_types.MetaData(
                "",
                unit_a="1/s",
                unit_o="V*V",
                quantity_a=_("Frequency")
        ))
        self._new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.check_all_empty_inputs():
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
        meta_data = deepcopy(input_signal.meta_data)
        unit_o = input_signal.meta_data.unit_o**2
        unit_a = 1/input_signal.meta_data.unit_a
        meta_data.unit_a = unit_a
        meta_data.quantity_a = unit_a.quantity
        meta_data.unit_o = unit_o
        meta_data.quantity_o = unit_o.quantity
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=psd,
        )
