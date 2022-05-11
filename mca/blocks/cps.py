from mca.framework import validator, data_types, Block
from mca.language import _

import numpy as np


class CrossPowerSpectrum(Block):
    """Computes the cross power spectrum of the input signals."""
    name = _("CrossPowerSpectrum")
    description = _("Computes the cross power spectrum of the "
                    "input signals.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(metadata=data_types.MetaData(
                "",
                unit_a="1/s",
                unit_o="V*V",
                quantity_a=_("Frequency")
        ))
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.any_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        validator.check_type_signal(self.inputs[1].data)
        validator.check_same_units([self.inputs[0].data.metadata.unit_a,
                                   self.inputs[1].data.metadata.unit_a])
        first_signal = self.inputs[0].data
        second_signal = self.inputs[1].data
        validator.check_intervals([first_signal, second_signal])
        ccf = np.correlate(first_signal.ordinate, second_signal.ordinate,
                           mode="full")
        cpsd = np.fft.fft(ccf)
        abscissa_start = 0
        values = first_signal.values + second_signal.values - 1
        unit_o = first_signal.metadata.unit_o * second_signal.metadata.unit_o
        unit_a = 1/first_signal.metadata.unit_a
        metadata = data_types.MetaData(None, unit_a, unit_o)
        increment = 1 / (
                first_signal.increment * values)
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(metadata),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=cpsd,
        )